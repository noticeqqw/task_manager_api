from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.tasks import router as tasks_router


app = FastAPI(
    title="Task Manager API",
    version="0.1.0",
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(tasks_router, prefix="/tasks", tags=["Tasks"])

@app.get("/health")
def health():
    return {"status": "ok"}
