import yt_dlp
import uuid
import os

ydl_opts = {}

class TwitterDownloader:
    def download(self, url: str)-> str:
        uuid_id = str(uuid.uuid4())
        output_path = f"{uuid_id}.mp4"

        ydl_opts = {
            'outtmpl': output_path,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return output_path

    def clean(self, path: str):
        print(f"Cleaning up {path}")
        os.remove(path)
