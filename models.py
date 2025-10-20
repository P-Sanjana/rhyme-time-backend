from pydantic import BaseModel, Field

class RandomWordResponse(BaseModel):
    word: str = Field(..., description='A single random English word based on the given difficulty.')

class RhymesResponse(BaseModel):
    word: str = Field(..., description='The input word for which rhymes are found.')
    rhymes: list[str] = Field(..., description='List of rhymes for the given word.')