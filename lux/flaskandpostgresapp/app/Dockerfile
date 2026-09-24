FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
COPY app.py .
COPY templates .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["sh", "-c", "python app.py"]
