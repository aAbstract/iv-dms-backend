from typing import Optional
from pydantic import BaseModel
from enum import Enum
from datetime import datetime


class RegulationType(str, Enum):
    IOSA = 'IOSA'
    ECAR = 'ECAR'


class Constrain(BaseModel):
    text: str
    children: list['Constrain'] = []


class IOSAItem(BaseModel):
    code: str
    guidance: Optional[str] = None
    iosa_map: list[str] = []
    paragraph: str
    page: int
    # constraints: list[Constrain]


class IOSASection(BaseModel):
    name: str
    code: str
    applicability: str
    guidance: Optional[str] = None
    items: list[IOSAItem] = []


class IOSARegulation(BaseModel):
    id: Optional[str] = None
    type: RegulationType = RegulationType.IOSA
    name: str
    effective_date: datetime
    sections: list[IOSASection]

    class Config:
        use_enum_values = True


class RegulationsMetaData(BaseModel):
    id: Optional[str] = None
    type: RegulationType
    name: str
    effective_date: datetime

    class Config:
        use_enum_values = True


class RegulationsSourceMap(BaseModel):
    code: str
    title: str
    sub_section: list[str]
    regulation_id: str
