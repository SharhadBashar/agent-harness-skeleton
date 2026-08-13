from pydantic import BaseModel, field_validator


class AgentRequest(BaseModel):
    user_query: str

    @field_validator('user_query', mode = 'before')
    @classmethod
    def validate_user_query(cls, v):
        if not v or v.strip() == '':
            raise ValueError('User query cannot be empty')
        return v
