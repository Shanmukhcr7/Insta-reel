from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
import re
import os
import time
from app.models.schemas import DownloadRequest, DownloadResponse
from app.services.downloader import download_instagram_video

router = APIRouter()

def is_valid_instagram_url(url: str) -> bool:
    # Basic validation for instagram URLs
    pattern = r'^(https?:\/\/)?(www\.)?instagram\.com\/(reel|p|tv)\/[a-zA-Z0-9_-]+\/?.*$'
    return re.match(pattern, url) is not None

def cleanup_old_files():
    """Deletes files in the static directory older than 1 hour to save disk space."""
    static_dir = "static"
    if not os.path.exists(static_dir):
        return
        
    current_time = time.time()
    for filename in os.listdir(static_dir):
        filepath = os.path.join(static_dir, filename)
        if os.path.isfile(filepath):
            # If older than 1 hour (3600 seconds)
            if current_time - os.path.getmtime(filepath) > 3600:
                try:
                    os.remove(filepath)
                except Exception:
                    pass

@router.post("/download", response_model=DownloadResponse)
async def process_download(request: DownloadRequest, req: Request, background_tasks: BackgroundTasks):
    url = request.url.strip()
    
    # Trigger cleanup of old files in the background
    background_tasks.add_task(cleanup_old_files)
    
    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty")
        
    if not is_valid_instagram_url(url):
        return DownloadResponse(success=False, error="Invalid Instagram URL. Must be a reel, post (/p/), or tv link.")
        
    try:
        # Download the video to the server and get the filename
        filename = download_instagram_video(url)
        
        if filename:
            # Construct the full URL to the static file
            base_url = str(req.base_url).rstrip("/")
            download_url = f"{base_url}/static/{filename}"
            return DownloadResponse(success=True, download_url=download_url)
        else:
            return DownloadResponse(success=False, error="Failed to download video. It might be private or unavailable.")
            
    except Exception as e:
        return DownloadResponse(success=False, error=str(e))
