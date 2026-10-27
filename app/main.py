from fastapi import FastAPI

from app.routes import router

app = FastAPI(title="Text Summarizer API")
app.include_router(router)
