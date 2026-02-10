from pydantic import BaseModel, Field


class BlindRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=255)
