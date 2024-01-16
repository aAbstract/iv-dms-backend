from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import datetime
from models.httpio import JsonResponse


class AITaskStatus(str, Enum):
    IN_PROGRESS = 'IN_PROGRESS'
    FINISHED = 'FINISHED'
    FAILD = 'FAILD'


class AITaskType(str, Enum):
    COMPLIANCE_CHECK = 'COMPLIANCE_CHECK'
    PARSING_PDF = 'PARSING_PDF'
    SCANNING_PDF = 'SCANNING_PDF'


class AITask(BaseModel):
    id: Optional[str] = None
    username: str
    start_datetime: datetime
    end_datetime: Optional[datetime]
    task_type: AITaskType
    task_status: AITaskStatus
    json_resp: JsonResponse
