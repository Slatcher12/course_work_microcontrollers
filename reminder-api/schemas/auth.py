from pydantic import BaseModel
from pydantic import Field


class Token(BaseModel):
    access_token: str = Field(example="access-token.123-abc")
    token_type: str = Field(default="bearer")
