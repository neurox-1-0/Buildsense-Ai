import requests
from config.settings import get_settings
from core.exceptions import ExternalToolError


class YouTubeClient:
    SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
    COMMENT_URL = "https://www.googleapis.com/youtube/v3/commentThreads"

    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def available(self) -> bool:
        return bool(self.settings.youtube_api_key)

    def search_comments(self, query: str, limit: int = 20) -> list[dict]:
        if not self.available:
            return []
        params = {"part": "snippet", "q": query, "type": "video", "maxResults": min(5, limit), "key": self.settings.youtube_api_key}
        try:
            response = requests.get(self.SEARCH_URL, params=params, timeout=self.settings.request_timeout_seconds)
            response.raise_for_status()
            videos = response.json().get("items", [])
            output = []
            for video in videos:
                video_id = video["id"]["videoId"]
                title = video["snippet"]["title"]
                cparams = {"part": "snippet", "videoId": video_id, "maxResults": min(20, limit), "textFormat": "plainText", "key": self.settings.youtube_api_key}
                cres = requests.get(self.COMMENT_URL, params=cparams, timeout=self.settings.request_timeout_seconds)
                if cres.status_code != 200:
                    continue
                for item in cres.json().get("items", []):
                    sn = item["snippet"]["topLevelComment"]["snippet"]
                    output.append({"source": "youtube", "title": title, "content": sn.get("textDisplay", ""), "author": sn.get("authorDisplayName", ""), "published_at": sn.get("publishedAt"), "url": f"https://www.youtube.com/watch?v={video_id}"})
                    if len(output) >= limit:
                        return output
            return output
        except requests.RequestException as exc:
            raise ExternalToolError(f"YouTube request failed: {exc}") from exc
