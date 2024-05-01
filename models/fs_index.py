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
    doc_status: Optional[ChatDOCStatus] = None
    organization: str
    airline:Optional[str] = None
    args: dict = {}


class FSIndexNode(BaseModel):
    label: str
    pages: list[int]
    key:str
    children: Optional[list['FSIndexNode']] = None

class FSIndexTree(BaseModel):
    doc_uuid: str
    label: str
    children: Optional[list['FSIndexNode']] = None
    key:str

class FSIndexFileTree(BaseModel):
    label: str
    key:str
    children: Optional[list['FSIndexTree']] = None

class TocLink(BaseModel):
    link_idx: str
    link_label: str
    target_page: int
    next_link_page: int = -1
    next_link_idx: Optional[str] = None

class ZTree(BaseModel):
    label: str
    section_label:str
    key:str
    pages: Optional[list[int]] = []
    children: Optional[list['ZTree']] = []

class TocTreeNode(BaseModel):
    link_idx: str
    link_label: str
    start_page: int
    end_page: int = -1
    end_tag: Optional[str] = None
    children: list['TocTreeNode'] = []