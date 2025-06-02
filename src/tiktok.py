import pyktok as pyk
import os

class TiktokDownloader:
    def download(self, url: str)-> str:
        # extact tiktok ref code https://vm.tiktok.com/ZNdB5roN3
        code = url.split('/')[3]
        pyk.save_tiktok(url, True)
        path = os.getcwd() + os.sep + code + '.mp4'

        return path

    def clean(self, path: str):
        os.remove(path)
