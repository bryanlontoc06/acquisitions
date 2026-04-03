from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str
    id_token: str | None = None
    expires_in: int
    token_type: str = "bearer"


class TokenResponse(BaseModel):
    token: Token
