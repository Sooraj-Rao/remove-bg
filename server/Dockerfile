# Use Python 3.11 as base image
FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn rembg pillow requests

# Expose the port FastAPI runs on
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
