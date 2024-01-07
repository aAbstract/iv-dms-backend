from typing import Optional
from pydantic import BaseModel
from enum import Enum


class UserRole(str, Enum):
    ADMIN = 'ADMIN'
    AUDITOR = 'AUDITOR'
    AIRLINES = 'AIRLINES'


class User(BaseModel):
    id: Optional[str] = None
    username: str
    disp_name: str
    pass_hash: str
    user_role: UserRole
    phone_number: str
    email: str

    class Config:
        use_enum_values = True
