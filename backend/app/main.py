from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analyze, confirm, feedback

app = FastAPI(title="Action Router Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router)
app.include_router(confirm.router)
app.include_router(feedback.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
