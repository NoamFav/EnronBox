FROM python:3.11-slim

# Install build tools & required libraries for spaCy and others
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

# Copy only requirements first for caching
COPY apps/flask_api/requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY apps/flask_api/ .

RUN python3 postinstall.py

EXPOSE 5050

CMD ["python3", "-m", "app.server"]
