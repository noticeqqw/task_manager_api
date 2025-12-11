from fastapi import FastAPI
import os

app = FastAPI(
    title="Task Manager API",
    version="0.1.0"
)

@app.get("/health")
def health():
    return {"status": "ok"}