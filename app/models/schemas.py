from pydantic import BaseModel, HttpUrl, Field

class DownloadRequest(BaseModel):
    url: str = Field(..., description="The Instagram Reel or Post URL")

class DownloadResponse(BaseModel):
    success: bool
    download_url: str | None = None
    error: str | None = None
