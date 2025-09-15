import requests

def get_real_instagram_url(share_url) -> str| None:
    try:
        response = requests.get(share_url, allow_redirects=True)
        print("Real Instagram URL:", response.url)
        return response.url
    except Exception as e:
        print(f"Error fetching real Instagram URL: {e}")
        return None
