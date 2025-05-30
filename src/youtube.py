from uuid import UUID
from pytubefix import YouTube
import random

def download_youtube_video(url: str) -> str:
    path = str(UUID(int=random.getrandbits(128)))

    try:
        file_name = YouTube(url).streams.first().download(output_path=path)
        return file_name
    except Exception as e:
        print(f"Failed to download YouTube video: {e}")
