# Use a slim Python image and run with Gunicorn
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Avoid running as root
RUN useradd --create-home appuser

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . /app
RUN chown -R appuser:appuser /app
USER appuser

# Port - Render provides $PORT at runtime
ENV PORT 10000
EXPOSE 10000

# Start with Gunicorn. Use shell to allow $PORT expansion
CMD ["sh", "-c", "gunicorn -w 4 -b 0.0.0.0:$PORT app:app"]
