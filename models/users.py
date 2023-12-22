from typing import Optional
from pydantic import BaseModel
from enum import Enum


class UserRoles(str, Enum):
    ADMIN = 'ADMIN'
    AUDITOR = 'AUDITOR'
    AIRLINES = 'AIRLINES'


class User(BaseModel):
    _id: Optional[str]
    username: str
    disp_name: str
    pass_hash: str
    user_role: UserRoles
    phone_number: str
    email: str

    class Config:
        use_enum_values = True
