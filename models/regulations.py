from typing import Optional
from pydantic import BaseModel
from enum import Enum


class RegulationType(str, Enum):
    IOSA = 'IOSA'
    ECAR = 'ECAR'


class Constrain(BaseModel):
    text: str
    children: list['Constrain'] = []


class IOSAItem(BaseModel):
    code: str
    guidance: str
    constraint: Constrain


class IOSASection(BaseModel):
    name: str
    code: str
    applicability: str
    guidance: str
    items: list[IOSAItem]


class IOSARegulation(BaseModel):
    _id: Optional[str]
    type: RegulationType = RegulationType.IOSA
    name: str
    sections: list[IOSASection]

    class Config:
        use_enum_values = True
