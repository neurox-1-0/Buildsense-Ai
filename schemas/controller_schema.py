from pydantic import BaseModel, Field


class ControllerDecision(BaseModel):
    action: str
    reason: str = Field(min_length=5, max_length=500)
