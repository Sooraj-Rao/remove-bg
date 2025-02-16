# Use Python 3.11 as base image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy everything inside server/ into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir onnxruntime  

# Expose the port FastAPI runs on
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
