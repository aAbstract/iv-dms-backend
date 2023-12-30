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


class FSIndexFile(BaseModel):
    id: Optional[str] = None
    username: str
    datetime: datetime
    file_type: IndexFileType
    filename: str
