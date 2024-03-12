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
    NOTDOCNOTIMP = "Not Documented not Implemented (Finding)"
    DOCNOTIMP = "Implemented not Documented (Finding)"
    NOTDOCIMP = "Documented not Implemented (Finding)"
    DOCIMP = "Documented and Implemented (Conformity)"
    N_A = "N/A"
    
class AuditorActions(str, Enum):
    IDENTIFIED = "IDENTIFIED"
    INTERVIEWED = "INTERVIEWED"
    EX_SYLLABI = "EX_SYLLABI"
    EX_TRAINING = "EX_TRAINING"

class ManualReference(BaseModel):
    fs_index: str
    pages: list[int] = []
    
class Checkin(BaseModel):
    description: str
    label: str
    pages: Optional[list] = []
    manual_references: Optional[dict] = {}
    isComplying: Optional[bool]
    isComplied: Optional[bool]
    comments: Optional[str]
    pct_score: Optional[float|int]
    context_id: Optional[str]
    overall_compliance_tag: Optional[str]

class ReportItem(BaseModel):
    code: str
    page: Optional[int] = None
    checkins: Optional[list[Checkin]] = []
    final_comment: Optional[FinalComment] = None
    comments: Optional[str] = None
    actions: list[AuditorActions] = []
    other_actions : Optional[str] = None
    recommendations: Optional[str] = None
    fs_index: Optional[str] = None
    url_path: Optional[str] = None
    # attachment ~ fs index id

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
    airline:str
    creator: str
    user_changes: list[UserChange] = []

class FlowReportChange(BaseModel):
    report_id: str
    organization: str
    user_changes: list[UserChange] = []

class Airline(BaseModel):
    name: str
    organization: str