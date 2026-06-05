from fastapi import FastAPI

from app.api.routes import analyze, confirm, feedback

app = FastAPI(title="Action Router Agent")

app.include_router(analyze.router)
app.include_router(confirm.router)
app.include_router(feedback.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
