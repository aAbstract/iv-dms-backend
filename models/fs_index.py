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


CHAT_DOC_STATUS_CODE_MAP = {
    300: ChatDOCStatus.PARSED,
    1: ChatDOCStatus.PARSING,
    12: ChatDOCStatus.PARSING,
}


class FSIndexFile(BaseModel):
    id: Optional[str] = None
    username: str
    datetime: datetime
    file_type: IndexFileType
    filename: str
    doc_uuid: str
    doc_status: ChatDOCStatus
