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
class forget(BaseModel):
    email:str
class verify_otp(BaseModel):
    email:str
    user_otp:int
class resetpassword(BaseModel):
    email:str
    password:str
    confirmPassword:str