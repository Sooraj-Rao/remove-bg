FROM python:3.11-slim

WORKDIR /app

COPY . /app

# Install required packages and clean up in a single layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf ~/.cache/pip

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    REMBG_CACHE_DIR=/tmp/rembg \
    REMBG_MODEL=u2netp \
    MALLOC_TRIM_THRESHOLD_=100000

# Add a non-root user
RUN useradd -m -u 1000 appuser
USER appuser

CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port $PORT --workers 1"]