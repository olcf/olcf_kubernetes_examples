import os

import psycopg
from flask import Flask, request
from openai import OpenAI
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer

app = Flask(__name__)

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "google/embeddinggemma-300m")
GENERATION_MODEL = os.getenv("GENERATION_MODEL", "google/gemma-3-4b-it")
VLLM_BASE_URL = os.getenv("VLLM_BASE_URL", "http://vllm:8000/v1")
TOP_K = int(os.getenv("TOP_K", "5"))

embedder = SentenceTransformer(EMBEDDING_MODEL)
generator = OpenAI(base_url=VLLM_BASE_URL, api_key=os.getenv("VLLM_API_KEY", "unused"))


def connect(use_vectors=False):
    connection = psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )
    if use_vectors:
        register_vector(connection)
    return connection


def initialize_database():
    with connect() as connection:
        connection.execute("CREATE EXTENSION IF NOT EXISTS vector")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id BIGSERIAL PRIMARY KEY,
                source TEXT NOT NULL,
                content TEXT NOT NULL,
                embedding VECTOR(768) NOT NULL
            )
            """
        )


def chunks(text, size=200, overlap=40):
    words = text.split()
    step = size - overlap
    return [" ".join(words[index : index + size]) for index in range(0, len(words), step)]


@app.get("/health")
def health():
    with connect() as connection:
        connection.execute("SELECT 1")
    return {"status": "ok"}


@app.post("/documents")
def add_document():
    source = request.args.get("source", "document")
    content = request.get_data(as_text=True).strip()
    if not content:
        return {"error": "Request body is empty"}, 400

    document_chunks = chunks(content)
    embeddings = embedder.encode_document(document_chunks, normalize_embeddings=True)

    with connect(use_vectors=True) as connection:
        connection.execute("DELETE FROM documents WHERE source = %s", (source,))
        connection.executemany(
            "INSERT INTO documents (source, content, embedding) VALUES (%s, %s, %s)",
            [(source, chunk, embedding) for chunk, embedding in zip(document_chunks, embeddings)],
        )

    return {"source": source, "chunks": len(document_chunks)}, 201


@app.post("/ask")
def ask():
    question = request.get_data(as_text=True).strip()
    if not question:
        return {"error": "Request body is empty"}, 400

    embedding = embedder.encode_query(question, normalize_embeddings=True)
    with connect(use_vectors=True) as connection:
        rows = connection.execute(
            """
            SELECT source, content, 1 - (embedding <=> %s) AS score
            FROM documents
            ORDER BY embedding <=> %s
            LIMIT %s
            """,
            (embedding, embedding, TOP_K),
        ).fetchall()

    if not rows:
        return {"error": "No documents have been added"}, 400

    context = "\n\n".join(f"Source: {source}\n{content}" for source, content, _ in rows)
    response = generator.chat.completions.create(
        model=GENERATION_MODEL,
        messages=[
            {
                "role": "system",
                "content": "Answer only from the supplied context. Say when the context is insufficient.",
            },
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        temperature=0.2,
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": [
            {"source": source, "score": round(float(score), 3)} for source, _, score in rows
        ],
    }


initialize_database()
