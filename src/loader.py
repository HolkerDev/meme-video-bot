import os
import time
import shutil
import threading
import instaloader
from typing import Optional, List

class Loader:
    def __init__(self, delay_seconds: float = 5.0):
        self.loader = instaloader.Instaloader()
        self.loader.load_session_from_file("nick.pen12", filename="sessions/session-nick.pen12.")
        self.loader.context.iphone_support = False
        self.loader.context._full_metadata = False
        self.loader.context._post_metadata_txt_pattern = None
        self.queue: List[str] = []
        self.delay = delay_seconds
        self.running = True
        self.queue_lock = threading.Lock()
        threading.Thread(target=self.run_queue_forever, daemon=True).start()

    def add_to_queue(self, shortcode: str):
        with self.queue_lock:
            self.queue.append(shortcode)

    def run_queue_forever(self):
        while self.running:
            shortcode = None
            with self.queue_lock:
                if self.queue:
                    shortcode = self.queue.pop(0)

            if shortcode:
                try:
                    print(f"[LOADER] Downloading {shortcode}...")
                    path = self.download_instagram_video(shortcode)
                    print(f"[LOADER] Saved to: {path}")
                except Exception as e:
                    print(f"[LOADER] Failed to download {shortcode}: {e}")

            time.sleep(self.delay)

    def download_instagram_video(self, shortcode: str) -> Optional[str]:
        try:
            post = instaloader.Post.from_shortcode(self.loader.context, shortcode)
        except Exception as e:
            print(f"[LOADER] Error resolving shortcode: {e}")
            raise e

        self.loader.download_post(post, target=shortcode)

        return self.get_video_path(shortcode) if post.is_video else self.get_img_path(shortcode)

    def get_video_path(self, download_path: str) -> Optional[str]:
        for file in os.listdir(download_path):
            if file.endswith('.mp4'):
                return os.path.join(download_path, file)
        return None

    def get_img_path(self, download_path: str) -> Optional[str]:
        for file in os.listdir(download_path):
            if file.endswith('.jpg'):
                return os.path.join(download_path, file)
        return None

    def clear(self, path: str):
        shutil.rmtree(os.path.dirname(path), ignore_errors=True)
