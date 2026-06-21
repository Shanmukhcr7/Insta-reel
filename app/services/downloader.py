import yt_dlp
import logging

import os

logger = logging.getLogger(__name__)

def extract_instagram_url(instagram_url: str) -> str | None:
    """
    Uses yt-dlp to extract the direct MP4 URL from an Instagram link.
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best[ext=mp4]/best',
        'skip_download': True,
    }
    
    # Instagram requires authentication for most requests now.
    # We look for a cookies.txt file in the backend directory.
    if os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'


    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(instagram_url, download=False)
            
            # Instagram often provides multiple formats or just one directly.
            # We look for the best video URL.
            
            # If it's a playlist/multi-video post, get the first one for simplicity (MVP)
            if 'entries' in info_dict:
                first_entry = info_dict['entries'][0]
                return first_entry.get('url')
            
            return info_dict.get('url')

    except yt_dlp.utils.DownloadError as e:
        logger.error(f"Download Error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected Error: {e}")
        return None
