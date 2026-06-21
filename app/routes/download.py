from fastapi import APIRouter, HTTPException
import re
from app.models.schemas import DownloadRequest, DownloadResponse
from app.services.downloader import extract_instagram_url

router = APIRouter()

def is_valid_instagram_url(url: str) -> bool:
    # Basic validation for instagram URLs
    pattern = r'^(https?:\/\/)?(www\.)?instagram\.com\/(reel|p|tv)\/[a-zA-Z0-9_-]+\/?.*$'
    return re.match(pattern, url) is not None

@router.post("/download", response_model=DownloadResponse)
async def process_download(request: DownloadRequest):
    url = request.url.strip()
    
    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty")
        
    if not is_valid_instagram_url(url):
        return DownloadResponse(success=False, error="Invalid Instagram URL. Must be a reel, post (/p/), or tv link.")
        
    try:
        download_url = extract_instagram_url(url)
        
        if download_url:
            return DownloadResponse(success=True, download_url=download_url)
        else:
            return DownloadResponse(success=False, error="Failed to extract video URL. It might be private or unavailable.")
            
    except Exception as e:
        return DownloadResponse(success=False, error=str(e))
