from typing import Optional
from pydantic import BaseModel
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    AUDITOR = "AUDITOR"
    AIRLINES = "AIRLINES"

class ApiUsageKey(str, Enum):
    GEMINI_AUDITS = 'gemini_audits'
    CHATDOC_PARSE_DOCS = 'chatdoc_parse_docs'
    CHATDOC_CHECK_DOCS = 'chatdoc_check_docs'
    CHATDOC_SCAN_DOCS = 'chatdoc_scan_docs'

class UserActivity(BaseModel):
    gemini_audits: int = 0
    chatdoc_parse_docs: int = 0
    chatdoc_check_docs: int = 0
    chatdoc_scan_docs: int = 0


class User(BaseModel):
    id: Optional[str] = None
    username: str
    disp_name: str
    pass_hash: str
    user_role: UserRole
    phone_number: str
    email: str
    activity: UserActivity

    class Config:
        use_enum_values = True
