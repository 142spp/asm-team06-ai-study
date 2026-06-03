from fastapi import FastAPI

app = FastAPI(title="Action Router Agent")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
