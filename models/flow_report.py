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


class FlowStage(BaseModel):
    stage_name: str
    assigned_user: Optional[str] = None
    assigned_role: Optional[UserRole] = None
    description: Optional[str] = None

class FlowStageTemplate(BaseModel):
    name: Optional[str] = None
    stages: list[FlowStage] = []

class FlowStageTemplateMap(dict, Enum):
    STAGES_4 = FlowStageTemplate(
        name="STAGES_4",
        stages=[
            FlowStage(
                stage_name="Stage 1 FAT",
                assigned_user=None,
                assigned_role=UserRole.FATTER,
                description="This stage is where we preproces that fat data",
            ),
            FlowStage(
                stage_name="Stage 1 FAT",
                assigned_user=None,
                assigned_role=UserRole.CARER,
                description="This stage is where we preproces that fat data",
            ),
            FlowStage(
                stage_name="Stage 1 FAT",
                assigned_user=None,
                assigned_role=UserRole.MANER,
                description="This stage is where we preproces that fat data",
            ),
            FlowStage(
                stage_name="Stage 1 FAT",
                assigned_user=None,
                assigned_role=UserRole.ADMIN,
                description="This stage is where we preproces that fat data",
            ),
        ],
    )
    STAGES_2 = FlowStageTemplate(
        name="STAGES_2",
        stages=[
            FlowStage(
                stage_name="Stage 1 FAT",
                assigned_user=None,
                assigned_role=UserRole.FATTER,
                description="This stage is where we preproces that fat data",
            ),
            FlowStage(
                stage_name="Stage 2 FAT",
                assigned_user=None,
                assigned_role=UserRole.ADMIN,
                description="This stage is where we preproces that fat data",
            ),
        ],
    )


class FlowReport(BaseModel):
    title: Optional[str] = None
    regulation_id: str
    code: str
    sub_sections: list[ReportSubSectionWritten] = []
    flow_stages: list[FlowStage] = []
    status: FlowReportStatus
    current_stage_index: int
    start_date: datetime
    end_date: datetime
    organization: str
    creator: str

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
    report_after: Optional[FlowReport] = None
    date: Optional[datetime] = datetime.now()

class FlowReportChange(BaseModel):
    report_id: str
    organization: str
    user_changes: list[UserChange] = []
