FROM python:3.9-slim

WORKDIR /app

COPY backend/requirements.txt .
COPY backend/ .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["gunicorn", "-b", "0.0.0.0:8080", "server:app"]
