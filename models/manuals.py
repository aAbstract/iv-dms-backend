from .regulations import RegulationType
from pydantic import BaseModel


class ManualRegulationCode(BaseModel):
    type: RegulationType
    cat_code: str
    code: str

    class Config:
        use_enum_values = True


class ManualSection(BaseModel):
    header: str
    order: int
    text: str
    regulations_codes: list[ManualRegulationCode]


class ManualChapter(BaseModel):
    name: str
    order: int
    sections: list[ManualSection]


class Manual(BaseModel):
    name: str
    chapters: list[ManualChapter]
