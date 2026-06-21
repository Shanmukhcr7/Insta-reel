from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import download

app = FastAPI(
    title="ReelSaver Backend",
    description="Backend API for downloading Instagram Reels",
    version="1.0.0"
)

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
