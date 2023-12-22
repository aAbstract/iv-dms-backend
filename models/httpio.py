from typing import Optional, Any
from pydantic import BaseModel


class ServiceResponse(BaseModel):
    success: Optional[bool] = True
    status_code: Optional[int] = 200
    msg: Optional[str] = ''
    data: Optional[Any] = {}


class JsonResponse(BaseModel):
    success: Optional[bool] = True
    msg: Optional[str] = ''
    data: Optional[Any] = {}


class LoginRequest(BaseModel):
    username: str
    password: str
