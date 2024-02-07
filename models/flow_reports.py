from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel
from pydantic.dataclasses import dataclass
from models.regulations import RegulationType, IOSAItem
from models.users import UserRole


class ReportSubSection(BaseModel):
    title: str
    checklist_items: list[IOSAItem] = []

class ReportTemplate(BaseModel):
    title: Optional[str] = None
    type: RegulationType
    applicability: str
    general_guidance: str
    sub_sections: list[ReportSubSection] = []

class FinalComment(str, Enum):
    NOTDOCNOTIMP = "Not Documented, Not Implemented"
    DOCNOTIMP = "Documented, Not Implemented"
    NOTDOCIMP = "Not Documented, Implemented"
    DOCIMP = "Documented, Implemented"

class ManualReference(BaseModel):
    check_in_code: str
    description: Optional[str] = None

class ReportItem(BaseModel):
    code: str
    manual_references: list[ManualReference] = []
    final_comment: Optional[FinalComment] = None
    comments: Optional[str] = None
    actions: Optional[str] = None

class ReportSubSectionWritten(BaseModel):
    title: str
    checklist_items: list[ReportItem] = []

class FlowReportStatus(str, Enum):
    CLOSED = "CLOSED"
    REJECTED = "REJECTED"
    INPROGRESS = "IN-PROGRESS"
    DELETED = "DELETED"

class UserChangeType(str, Enum):
    DELETE = "DELETE"
    UPDATE = "UPDATE"
    VIEW = "VIEW"
    CREATE = "CREATE"
    FORWARD = "FORWARD"

class UserChange(BaseModel):
    user_name: str
    user_comment: str = ""
    change_type: UserChangeType
    date: Optional[datetime] = datetime.now()

class FlowReport(BaseModel):
    title: Optional[str] = None
    regulation_id: str
    code: str
    sub_sections: list[ReportSubSectionWritten] = []
    status: FlowReportStatus
    organization: str
    creator: str
    user_changes: list[UserChange] = []

class FlowReportChange(BaseModel):
    report_id: str
    organization: str
    user_changes: list[UserChange] = []