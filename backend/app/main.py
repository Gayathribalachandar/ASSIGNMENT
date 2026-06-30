from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Candidate Intelligence Engine",
    version="1.0.0",
    description="Canonical Candidate Profile Generator"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "application": "Candidate Intelligence Engine",
        "version": "1.0.0",
        "status": "Running"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }