import os
import time
import shutil
import threading
import instaloader
from typing import Optional

class Loader:
    def __init__(self):
        self.loader = instaloader.Instaloader()
        self.loader.load_session_from_file("nick.pen12", filename="sessions/session-nick.pen12")
        self.loader.context.iphone_support = False
        self.loader.context._full_metadata = False
        self.loader.context._post_metadata_txt_pattern = None
        self.last_download_time = 0
        self.lock = threading.Lock()

    def download_instagram_video(self, shortcode: str) -> Optional[str]:
        """Download Instagram video with 5-second delay enforcement"""
        with self.lock:
            # Ensure at least 5 seconds have passed since last download
            current_time = time.time()
            time_since_last = current_time - self.last_download_time

            if time_since_last < 5.0:
                sleep_time = 5.0 - time_since_last
                print(f"[LOADER] Waiting {sleep_time:.1f} seconds before download...")
                time.sleep(sleep_time)

            try:
                print(f"[LOADER] Downloading {shortcode}...")
                post = instaloader.Post.from_shortcode(self.loader.context, shortcode)
                self.loader.download_post(post, target=shortcode)

                # Update last download time
                self.last_download_time = time.time()

                # Return the path to the downloaded file
                if post.is_video:
                    path = self.get_video_path(shortcode)
                else:
                    path = self.get_img_path(shortcode)

                print(f"[LOADER] Downloaded to: {path}")
                return path

            except Exception as e:
                print(f"[LOADER] Error downloading {shortcode}: {e}")
                self.last_download_time = time.time()  # Still update time to maintain delay
                raise e

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
