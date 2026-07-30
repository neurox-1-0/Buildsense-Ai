import requests
from config.settings import get_settings
from core.exceptions import ExternalToolError


class GooglePlacesClient:
    TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def available(self) -> bool:
        return bool(self.settings.google_maps_api_key)

    def search_reviews(self, query: str, limit: int = 10) -> list[dict]:
        if not self.available:
            return []
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.settings.google_maps_api_key,
            "X-Goog-FieldMask": (
                "places.id,places.displayName,places.formattedAddress,"
                "places.location,places.rating,places.userRatingCount,"
                "places.primaryType,places.reviews,places.googleMapsUri"
            ),
        }
        try:
            response = requests.post(self.TEXT_SEARCH_URL, headers=headers, json={"textQuery": query, "maxResultCount": 3}, timeout=self.settings.request_timeout_seconds)
            response.raise_for_status()
            output = []
            for place in response.json().get("places", []):
                name = place.get("displayName", {}).get("text", "")
                place_metadata = {
                    "place_id": place.get("id", ""),
                    "place_name": name,
                    "formatted_address": place.get("formattedAddress", ""),
                    "latitude": (place.get("location") or {}).get("latitude"),
                    "longitude": (place.get("location") or {}).get("longitude"),
                    "rating": place.get("rating"),
                    "user_rating_count": place.get("userRatingCount"),
                    "primary_type": place.get("primaryType", ""),
                }
                for review in place.get("reviews", []):
                    text = review.get("text", {}).get("text", "") or review.get("originalText", {}).get("text", "")
                    if text:
                        output.append({
                            "source": "google_places",
                            "title": name,
                            "content": text,
                            "author": review.get("authorAttribution", {}).get("displayName", ""),
                            "published_at": review.get("publishTime"),
                            "url": place.get("googleMapsUri", ""),
                            "metadata": place_metadata,
                        })
                    if len(output) >= limit:
                        return output
            return output
        except requests.RequestException as exc:
            raise ExternalToolError(f"Google Places request failed: {exc}") from exc
