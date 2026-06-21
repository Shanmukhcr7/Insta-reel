import yt_dlp
import instaloader
import logging
import os
import uuid
import requests

logger = logging.getLogger(__name__)

def download_instagram_video(instagram_url: str) -> str | None:
    file_id = str(uuid.uuid4())
    save_path = f"static/{file_id}.mp4"
    
    # Extract shortcode from URL
    try:
        # e.g., https://www.instagram.com/reel/DZrWDl9u40_/?igsh=...
        parts = instagram_url.split('/')
        shortcode = ""
        for i, part in enumerate(parts):
            if part in ["reel", "p", "tv"]:
                shortcode = parts[i+1].split('?')[0]
                break
        
        if shortcode:
            logger.info(f"Trying Instaloader for shortcode: {shortcode}")
            L = instaloader.Instaloader()
            if os.path.exists('cookies.txt'):
                # Instaloader handles cookies differently, but we can try without auth first
                pass
            
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            video_url = post.video_url
            
            if video_url:
                logger.info("Successfully extracted video URL via Instaloader. Downloading...")
                response = requests.get(video_url, stream=True)
                response.raise_for_status()
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return f"{file_id}.mp4"
    except Exception as e:
        logger.error(f"Instaloader attempt failed: {e}")

    # Fallback to yt-dlp if instaloader fails
    logger.info("Falling back to yt-dlp...")
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
            ydl.extract_info(instagram_url, download=True)
            return f"{file_id}.mp4"

    except Exception as e:
        logger.error(f"First yt-dlp attempt failed: {e}")
        
        if os.path.exists('cookies.txt'):
            ydl_opts['cookiefile'] = 'cookies.txt'
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.extract_info(instagram_url, download=True)
                    return f"{file_id}.mp4"
            except Exception as e2:
                logger.error(f"Second yt-dlp attempt failed: {e2}")
                
    return None
