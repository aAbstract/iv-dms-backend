from typing import Optional
from pydantic import BaseModel, ConfigDict
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
    organization: str
    airline: Optional[str] = None
    is_disabled: Optional[bool] = None
    input_token_count: Optional[int] = None
    output_token_count: Optional[int] = None
    request_count : Optional[int] = None
    model_config = ConfigDict(use_enum_values=True)
