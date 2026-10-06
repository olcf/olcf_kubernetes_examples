FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
COPY app.py .
RUN mkdir /app/templates
COPY templates/index.html /app/templates
RUN  pip install -r requirements.txt

EXPOSE 5000

CMD ["gunicorn", "--bind=0.0.0.0:8000", "--workers=1", "--timeout=300", "app:app"]
