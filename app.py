from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="PsycheOS",
    description="Sistema Operativo Cognitivo Modular",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "🧠 PsycheOS - Sistema Operativo Cognitivo",
        "status": "online",
        "version": "1.0.0",
        "model": "gpt-5.2 (OpenAI)",
        "documentation": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "agent": "active"}

@app.get("/api/status")
async def status():
    return {
        "agent": "main",
        "model": "openai/gpt-5.2",
        "provider": "OpenAI"
    }