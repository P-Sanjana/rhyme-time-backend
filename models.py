from pydantic import BaseModel, Field

class RandomWordResponse(BaseModel):
    word: str = Field(..., description='A single random English word based on the given difficulty.')