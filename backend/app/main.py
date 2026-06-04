from fastapi import FastAPI

from app.api.routes import confirm

app = FastAPI(title="Action Router Agent")

app.include_router(confirm.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
