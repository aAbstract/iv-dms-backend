from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel


class JsonResponse(BaseModel):
    success: Optional[bool] = True
    msg: Optional[str] = ''
    data: Optional[Any] = {}


class LLMAuditScore(str, Enum):
    IRRELEVANT = 'IRRELEVANT'
    SOME = 'SOME'
    DOCUMENTED = 'DOCUMENTED'
    ACTIVE = 'ACTIVE'


class LLMAuditResponse(BaseModel):
    score_tag: LLMAuditScore
    score_text: str  # what does the tag mean
    description: str  # explaination generated from the LLM
    details: list['LLMAuditResponse'] = []
