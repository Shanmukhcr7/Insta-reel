import yt_dlp
import logging
import os
import uuid

logger = logging.getLogger(__name__)

def download_instagram_video(instagram_url: str) -> str | None:
    """
    Uses yt-dlp to download the video and audio, merge them, and save to the static directory.
    Returns the filename of the downloaded video.
    """
    
    # Generate a unique filename prefix
    file_id = str(uuid.uuid4())
    
    # First try without cookies to get the full unauthenticated DASH manifest
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f'static/{file_id}.%(ext)s',
        'merge_output_format': 'mp4',
        'postprocessor_args': {
            'merger': ['-c:v', 'copy', '-c:a', 'aac']
        },
        'skip_download': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(instagram_url, download=True)
            if 'entries' in info_dict:
                info = info_dict['entries'][0]
            else:
                info = info_dict
            return f"{file_id}.mp4"

    except Exception as e:
        logger.error(f"First attempt without cookies failed: {e}. Retrying with cookies...")
        
        # Fallback to using cookies if rate-limited or login required
        if os.path.exists('cookies.txt'):
            ydl_opts['cookiefile'] = 'cookies.txt'
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(instagram_url, download=True)
                    if 'entries' in info_dict:
                        info = info_dict['entries'][0]
                    else:
                        info = info_dict
                    return f"{file_id}.mp4"
            except Exception as e2:
                logger.error(f"Second attempt with cookies failed: {e2}")
                return None
        return None
