from models.regulations import IOSAItem
from models.httpio import LLMAuditResponse, LLMAuditScore
from models.runtime import ServiceResponse


# TODO-GALAL
score_tags_text_map: dict[str, str] = {
    LLMAuditScore.IRRELEVANT: '',
    LLMAuditScore.SOME: '',
    LLMAuditScore.DOCUMENTED: '',
    LLMAuditScore.ACTIVE: '',
}


async def iosa_audit_text(iosa_item: IOSAItem, text: str) -> ServiceResponse:
    # TODO-GALAL: construct LLM prompt
    # TODO-GALAL: send api request (use async HTTPX not requests)
    # TODO-GALAL: return output
    score = LLMAuditScore.DOCUMENTED
    llm_resp = LLMAuditResponse(
        score_tag=score,
        score_text=score_tags_text_map[score],
        description='some description',
        details=[],  # [OPTIONAL] details is computed recursively on constrains tree in iosa_item
    )
    return ServiceResponse(data={'llm_resp': llm_resp})
