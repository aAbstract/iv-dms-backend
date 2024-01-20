import os
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class IndexFileType(str, Enum):
    AIRLINES_MANUAL = 'AIRLINES_MANUAL'
    AIRLINES_ATTACHMENT = 'AIRLINES_ATTACHMENT'


FILE_TYPE_PATH_MAP = {
    IndexFileType.AIRLINES_MANUAL: os.path.join('airlines_files', 'manuals'),
    IndexFileType.AIRLINES_ATTACHMENT: os.path.join('airlines_files', 'attachments'),
}


class ChatDOCStatus(str, Enum):
    PARSING = 'PARSING'
    PARSED = 'PARSED'
    PARSING_FAILD = 'PARSING_FAILD'

    @classmethod
    def map_status_code(cls, status_code: int) -> 'ChatDOCStatus':
        if status_code == 300:
            return cls.PARSED
        elif status_code > 0:
            return cls.PARSING
        elif status_code < 0:
            return cls.PARSING_FAILD


class FSIndexFile(BaseModel):
    id: Optional[str] = None
    username: str
    datetime: datetime
    file_type: IndexFileType
    filename: str
    doc_uuid: str
    doc_status: ChatDOCStatus
