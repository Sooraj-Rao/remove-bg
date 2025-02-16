FROM python:3.11-slim

WORKDIR /app

COPY . /app

# Install required packages and clean up
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV REMBG_CACHE_DIR=/tmp/rembg
ENV REMBG_MODEL=u2netp

EXPOSE 8000

CMD uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}