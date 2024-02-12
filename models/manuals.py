from typing import Optional
from models.regulations import RegulationType
from pydantic import BaseModel, Field, ConfigDict


class ManualRegulationCode(BaseModel):
    type: RegulationType
    cat_code: str
    code: str

    model_config = ConfigDict(use_enum_values=True)


class ManualSection(BaseModel):
    header: str
    text: str
    regulations_codes: list[ManualRegulationCode]


class ManualChapter(BaseModel):
    name: str
    sections: list[ManualSection]


class StructuredManual(BaseModel):
    id: Optional[str] = None
    name: str
    chapters: list[ManualChapter]


class UnstructuredManual(BaseModel):
    id: Optional[str] = None
    name: str
    pages: list[str]


class UnstructuredManualMetaData(BaseModel):
    id: Optional[str] = None
    name: str
    page_count: int
