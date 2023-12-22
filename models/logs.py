from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class Log(BaseModel):
    _id: Optional[str]
    date: datetime
    level: str
    source: str
    description: str
