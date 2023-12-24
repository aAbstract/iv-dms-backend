from typing import Optional, Any
from pydantic import BaseModel


class ServiceResponse(BaseModel):
    success: Optional[bool] = True
    status_code: Optional[int] = 200
    msg: Optional[str] = ''
    data: Optional[Any] = {}
