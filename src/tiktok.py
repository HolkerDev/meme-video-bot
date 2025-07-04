import pyktok as pyk
import os

class TiktokDownloader:
    def download(self, url: str) -> str:
        if "tiktok.com/" in url:
            parts = url.rstrip('/').split('/')
            if "video" in parts:
                # Full URL: https://www.tiktok.com/@username/video/7360718987627400481
                username = parts[3]
                video_id = parts[-1]
                filename = f"{username}_video_{video_id}.mp4"
            else:
                # Short URL: https://vm.tiktok.com/ZNdB5roN3
                code = parts[-1]
                filename = f"{code}.mp4"
        else:
            # Fallback: just use last part
            code = url.rstrip('/').split('/')[-1]
            filename = f"{code}.mp4"

        pyk.save_tiktok(url, True)
        path = os.path.join(os.getcwd(), filename)
        return path

    def clean(self, path: str):
        os.remove(path)
