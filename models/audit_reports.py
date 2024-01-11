from pydantic import BaseModel
from models.regulations import RegulationType, IOSAItem


class ReportSubSection(BaseModel):
    title: str
    checklist_items: list[IOSAItem] = []


class ReportTemplate(BaseModel):
    title: str
    type: RegulationType
    applicability: str
    general_guidance: str
    sub_sections: list[ReportSubSection] = []
