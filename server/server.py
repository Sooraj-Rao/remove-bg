import os
import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Server is running!"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Read PORT from env, default to 8000
    uvicorn.run(app, host="0.0.0.0", port=port)
