from pydantic import BaseModel


class ChatResponse(BaseModel):
    output: str
