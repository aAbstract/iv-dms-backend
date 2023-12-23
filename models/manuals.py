from typing import Optional
from models.regulations import RegulationType
from pydantic import BaseModel


class ManualRegulationCode(BaseModel):
    type: RegulationType
    cat_code: str
    code: str

    class Config:
        use_enum_values = True


class ManualSection(BaseModel):
    header: str
    text: str
    regulations_codes: list[ManualRegulationCode]


class ManualChapter(BaseModel):
    name: str
    sections: list[ManualSection]


class StructuredManual(BaseModel):
    _id: Optional[str]
    name: str
    chapters: list[ManualChapter]


class UnstructuredManual(BaseModel):
    _id: Optional[str]
    name: str
    pages: list[str]
