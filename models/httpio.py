from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel


class JsonResponse(BaseModel):
    success: Optional[bool] = True
    msg: Optional[str] = ''
    data: Optional[Any] = {}
