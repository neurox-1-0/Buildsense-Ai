import json
import logging
from openai import OpenAI
from config.settings import get_settings

logger = logging.getLogger(__name__)


class OpenAIClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.openai_api_key) if self.settings.openai_api_key else None

    @property
    def available(self) -> bool:
        return self.client is not None

    def json_response(self, system_prompt: str, user_prompt: str) -> dict | None:
        if not self.client:
            return None
        try:
            # The Responses API requires the input message itself (not only the
            # instructions) to mention JSON when json_object mode is enabled.
            if "json" not in user_prompt.lower():
                user_prompt = f"Return a JSON object for the following input:\n{user_prompt}"
            response = self.client.responses.create(
                model=self.settings.openai_model,
                instructions=system_prompt,
                input=user_prompt,
                text={"format": {"type": "json_object"}},
            )
            return json.loads(response.output_text)
        except Exception as exc:
            logger.warning("OpenAI call failed; local fallback will be used: %s", exc)
            return None
