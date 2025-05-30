from typing import Optional
import os
import instaloader
import shutil

class Loader:
    def __init__(self):
        self.loader = instaloader.Instaloader()

    def download_instagram_video(self,shortcode:str) -> Optional[str]:
        try:
            post = instaloader.Post.from_shortcode(self.loader.context, shortcode)
        except Exception as e:
            print(f"Error downloading video: {e}")
            raise e
        self.loader.download_post(post, target=shortcode)

        # Ensure that only video posts are downloaded
        if not post.is_video:
            return self.get_img_path(shortcode)
        return self.get_video_path(shortcode)

    def get_video_path(self, download_path:str) -> Optional[str]:
        src :Optional[str]=None
        for file in os.listdir(download_path):
            if file.endswith('.mp4'):
                src = os.path.join(download_path, file)
                break
        return src

    def get_img_path(self, download_path:str) -> Optional[str]:
        src :Optional[str]=None
        for file in os.listdir(download_path):
            if file.endswith('.jpg'):
                src = os.path.join(download_path, file)
                break
        return src

    def clear(self, path:str):
        shutil.rmtree(os.path.dirname(path))
