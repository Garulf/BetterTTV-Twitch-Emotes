import requests

API_URL = "https://api.betterttv.net/3/emotes/shared/"
CDN_URL = "https://cdn.betterttv.net/emote/{id}/{size}.{ext}"
HEADERS = {"accept": "json", "accept-language": "en-US,en;q=0.9"}
TIMEOUT = 10
MIN_QUERY_LEN = 3


def image_url(emote, size="1x"):
    return CDN_URL.format(id=emote["id"], ext=emote["imageType"], size=size)


def _get(endpoint, params):
    response = requests.get(API_URL + endpoint, headers=HEADERS, params=params, timeout=TIMEOUT)
    data = response.json()
    if isinstance(data, dict):
        return []
    return data


def search_emotes(search_term, limit=25):
    return _get("search", {"query": search_term, "limit": limit})


def top_emotes(limit=25):
    return [entry["emote"] for entry in _get("top", {"offset": 0, "limit": limit})]
