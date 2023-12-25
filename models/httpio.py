from typing import Optional, Any
from pydantic import BaseModel


class JsonResponse(BaseModel):
    success: Optional[bool] = True
    msg: Optional[str] = ''
    data: Optional[Any] = {}


class LoginRequest(BaseModel):
    username: str
    password: str


class GetLogsRequest(BaseModel):
    limit: int


class GetManualPageRequest(BaseModel):
    manual_id: str
    page_order: int


class GetManualMetaDataRequest(BaseModel):
    manual_id: str
