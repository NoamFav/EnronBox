FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpq-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY apps/flask_api/requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY apps/flask_api/ .

RUN python3 postinstall.py

EXPOSE 5050

# Add these lines
ENV FLASK_ENV=development
ENV FLASK_APP=app.server

CMD ["flask", "run", "--host=0.0.0.0", "--port=5050"]
