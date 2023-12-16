from pydantic import BaseModel
from enum import Enum


class RegulationType(str, Enum):
    IOSA = 'IOSA'
    ECAR = 'ECAR'


class IOSAItem(BaseModel):
    guidance: str
    constraints: str


class IOSASection(BaseModel):
    applicability: str
    guidance: str
    items: list[IOSAItem]


class IOSARegulation(BaseModel):
    type: RegulationType = RegulationType.IOSA
    sections: list[IOSASection]

    class Config:
        use_enum_values = True
