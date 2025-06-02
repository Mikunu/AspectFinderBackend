from pydantic import BaseModel


class AspectRequestDto(BaseModel):
    version: str
