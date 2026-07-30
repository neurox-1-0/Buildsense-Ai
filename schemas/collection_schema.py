from pydantic import BaseModel, Field


class CollectedItem(BaseModel):
    item_id: str
    source: str
    content: str = Field(min_length=1)
    title: str = ""
    author: str = ""
    url: str = ""
    published_at: str | None = None
    metadata: dict = Field(default_factory=dict)
