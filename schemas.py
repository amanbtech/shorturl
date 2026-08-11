from typing import Optional
from pydantic import BaseModel, HttpUrl


class Urls(BaseModel):
    original_url: HttpUrl
    custom_code: Optional[str] = None
    expiry_days: int = 7


class Signup(BaseModel):
    username: str
    email: str
    password_hash: str


class Login(BaseModel):
    username: str
    password_hash: str


class UpdateUrl(BaseModel):
    original_url: str