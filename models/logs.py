from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class Log(BaseModel):
    id: Optional[str] = None
    datetime: datetime
    level: str
    source: str
    description: str
