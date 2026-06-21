import yt_dlp
import logging
import os
import uuid

logger = logging.getLogger(__name__)

def download_instagram_video(instagram_url: str) -> str | None:
    file_id = str(uuid.uuid4())
    save_path = f"static/{file_id}.%(ext)s"
    
    # First try without cookies to get the full unauthenticated DASH manifest
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': save_path,
        'merge_output_format': 'mp4',
        'postprocessor_args': {
            'merger': ['-c:v', 'copy', '-c:a', 'aac']
        },
        'skip_download': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(instagram_url, download=True)
            return f"{file_id}.mp4"

    except Exception as e:
        logger.error(f"First attempt without cookies failed: {e}. Retrying with cookies...")
        
        # Fallback to using cookies if rate-limited or login required
        if os.path.exists('cookies.txt'):
            ydl_opts['cookiefile'] = 'cookies.txt'
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(instagram_url, download=True)
                    return f"{file_id}.mp4"
            except Exception as e2:
                logger.error(f"Second attempt with cookies failed: {e2}")
                return None
        return None
