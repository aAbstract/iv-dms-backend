from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel


class JsonResponse(BaseModel):
    success: Optional[bool] = True
    msg: Optional[str] = ''
    data: Optional[Any] = {}


class LLMAuditScore(str, Enum):
    IRRELEVANT = 'IRRELEVANT'
    PARTIAL = 'PARTIAL'
    DOCUMENTED = 'DOCUMENTED'
    ACTIVE = 'ACTIVE'
    NULL = 'NULL'
    SERVER_ERROR = 'SERVER_ERROR'


class LLMIOSAItemResponse(BaseModel):
    text: str
    explanation: str = 'NULL'
    score: str = 'NULL'
    children: list['LLMIOSAItemResponse'] = []


class LLMAuditResponse(BaseModel):
    score_tag: LLMAuditScore
    score_text: str  # what does the tag mean
    summary: str  # explaination generated from the LLM
    details: list[LLMIOSAItemResponse] = []
