from pydantic import BaseModel
from enum import Enum

class JsonResponse(BaseModel):
    success: bool = True
    msg: str = ''
    data: dict = {}

class LLMAuditScore(str, Enum):
    IRRELEVANT = 'IRRELEVANT'
    PARTIAL = 'PARTIAL'
    DOCUMENTED = 'DOCUMENTED'
    CONFORMITY  = 'CONFORMITY '
    NULL = 'NULL'
    SERVER_ERROR = 'SERVER_ERROR'


class LLMIOSAItemResponse(BaseModel):
    text: str
    explanation: str = 'NULL'
    score: str = 'NULL'
    children: list['LLMIOSAItemResponse'] = []


class LLMAuditResponse(BaseModel):
    score: float
    score_tag: LLMAuditScore
    score_text: str  # what does the tag mean
    summary: str  # explaination generated from the LLM
    details: list[LLMIOSAItemResponse] = []

