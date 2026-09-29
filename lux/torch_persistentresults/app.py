
import os

import psycopg
from flask import Flask, request
from openai import OpenAI
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer
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
