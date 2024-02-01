from pydantic import BaseModel, computed_field
from enum import Enum


GPT35T_MAX_SCORE = 3


class GPT35TAuditScore(Enum):
    FULLY_COMPLIANT = GPT35T_MAX_SCORE
    PARTIALLY_COMPLIANT = GPT35T_MAX_SCORE - 1
    NON_COMPLIANT = GPT35T_MAX_SCORE - 2
    NONE = 0

    @classmethod
    def map_audit_score_lbl(cls, audit_score) -> str:
        if audit_score == cls.FULLY_COMPLIANT:
            return 'FULLY_COMPLIANT'
        elif audit_score == cls.PARTIALLY_COMPLIANT:
            return 'PARTIALLY_COMPLIANT'
        elif audit_score == cls.NON_COMPLIANT:
            return 'NON_COMPLIANT'
        else:
            return 'NONE'

    @classmethod
    def trans_audit_score(cls, audit_score) -> str:
        if audit_score == cls.FULLY_COMPLIANT:
            return 'All aspects are clearly and accurately addressed.'
        elif audit_score == cls.PARTIALLY_COMPLIANT:
            return 'Some aspects are addressed, but improvements or clarifications are needed.'
        elif audit_score == cls.NON_COMPLIANT:
            return 'Significant deviations from IOSA standards; a thorough revision is required.'
        else:
            return 'NONE'


class GTP35TIOSAItemResponse(BaseModel):
    text: str
    score: GPT35TAuditScore
    pct_score: float
    children: list['GTP35TIOSAItemResponse'] = []

    @computed_field
    @property
    def score_tag(self) -> str:
        return GPT35TAuditScore.map_audit_score_lbl(self.score)

    @computed_field
    @property
    def score_text(self) -> str:
        return GPT35TAuditScore.trans_audit_score(self.score)


class GPT35TAuditResponse(BaseModel):
    score: GPT35TAuditScore
    pct_score: float
    comments: str
    suggestions: str
    modified: str
    details: list[GTP35TIOSAItemResponse] = []

    @computed_field
    @property
    def score_tag(self) -> str:
        return GPT35TAuditScore.map_audit_score_lbl(self.score)

    @computed_field
    @property
    def score_text(self) -> str:
        return GPT35TAuditScore.trans_audit_score(self.score)
