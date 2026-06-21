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
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        # Get best video + best audio and merge them into an mp4. Fallback to best single mp4 if merging isn't possible.
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': f'static/{file_id}.%(ext)s',
        'merge_output_format': 'mp4',
        'skip_download': False,
    }
    
    # Instagram requires authentication for most requests now.
    if os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # download=True actually downloads and saves the file based on outtmpl
            info_dict = ydl.extract_info(instagram_url, download=True)
            
            # Since we downloaded it, yt-dlp provides the exact filename it saved it as
            if 'entries' in info_dict:
                info = info_dict['entries'][0]
            else:
                info = info_dict
                
            # The final extension is .mp4 because of merge_output_format
            return f"{file_id}.mp4"

    except yt_dlp.utils.DownloadError as e:
        logger.error(f"Download Error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected Error: {e}")
        return None
