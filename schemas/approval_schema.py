from typing import Literal
from pydantic import BaseModel, Field, model_validator


class ApprovalRequest(BaseModel):
    action: Literal["approve", "reject", "modify", "request_analysis", "restart"]
    feedback: str = Field(default="", max_length=3000)
    modified_summary: str | None = None

    @model_validator(mode="after")
    def validate_action_details(self):
        if self.action == "modify" and not (self.modified_summary or "").strip():
            raise ValueError("A modified recommendation summary is required")
        if self.action in {"request_analysis", "restart"} and not self.feedback.strip():
            raise ValueError("Feedback is required to guide the next execution")
        return self
