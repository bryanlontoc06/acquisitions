from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .token import Token


class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)
    role: str = Field(min_length=1, max_length=50)


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class UserPrivate(UserPublic):
    email: EmailStr


class LoginResponse(BaseModel):
    token: Token
