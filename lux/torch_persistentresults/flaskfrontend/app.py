import os

import psycopg
from flask import Flask, render_template

app = Flask(__name__)


def connect():
    connection = psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        dbname=os.environ["POSTGRES_DB"],
        port=os.getenv("POSTGRES_PORT", "5432"),
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )
    return connection


@app.route("/")
def show_results():
    with connect() as conn:
        rows = conn.execute(
            "SELECT id, date, log FROM torchlogs ORDER BY id DESC"
        ).fetchall()
    return render_template("index.html", rows=rows)
