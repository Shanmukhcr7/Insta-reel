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
    
    # 1. Try Instaloader first (bypasses many datacenter blocks by using mobile API)
    try:
        parts = instagram_url.split('/')
        shortcode = ""
        for i, part in enumerate(parts):
            if part in ["reel", "p", "tv"]:
                shortcode = parts[i+1].split('?')[0]
                break
        
        if shortcode:
            logger.info(f"Trying Instaloader for shortcode: {shortcode}")
            L = instaloader.Instaloader()
            
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

    # 2. Fallback to yt-dlp anonymously
    logger.info("Falling back to yt-dlp...")
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
        # Strictly require both video and audio. Do NOT fallback to silent videos.
        'format': 'bestvideo+bestaudio',
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
        
        # 3. Fallback to yt-dlp with cookies
        if os.path.exists('cookies.txt'):
            ydl_opts['cookiefile'] = 'cookies.txt'
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.extract_info(instagram_url, download=True)
                    return f"{file_id}.mp4"
            except Exception as e2:
                logger.error(f"Second yt-dlp attempt failed: {e2}")
                
    # If everything fails, return None so the app shows an error instead of saving a broken video
    return None
