FROM python:3.11-slim

WORKDIR /app

COPY apps/flask_api/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY apps/flask_api/ .

EXPOSE 5050

CMD ["python3", "-m", "app.server"]

