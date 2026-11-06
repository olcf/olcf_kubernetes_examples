FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
COPY app.py .
RUN mkdir /app/templates
COPY templates/index.html /app/templates
RUN  pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["sh", "-c", "python app.py"]
