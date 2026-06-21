import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import download

# Ensure static directory exists
os.makedirs("static", exist_ok=True)

app = FastAPI(
    title="ReelSaver Backend",
    description="Backend API for downloading Instagram Reels",
    version="1.0.0"
)

# Mount the static directory so the Flutter app can download the merged videos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

app.include_router(download.router, prefix="/api")
