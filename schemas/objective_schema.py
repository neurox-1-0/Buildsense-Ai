from pydantic import BaseModel, Field, field_validator
from core.url_safety import validate_public_url


class ObjectiveCreate(BaseModel):
    title: str = Field(min_length=3, max_length=160)
    description: str = Field(min_length=10, max_length=2000)
    industry: str = "Computer retail"
    target_market: str = "University students"
    keywords: list[str] = Field(default_factory=list)
    source_urls: list[str] = Field(default_factory=list)

    @field_validator("source_urls")
    @classmethod
    def validate_source_urls(cls, urls: list[str]) -> list[str]:
        if len(urls) > 10:
            raise ValueError("At most 10 source URLs are allowed")
        return [validate_public_url(url) for url in urls]


class ObjectiveResponse(ObjectiveCreate):
    objective_id: str
    status: str
