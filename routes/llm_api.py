import os
from fastapi import APIRouter, Response, Body, Header
import lib.log as log_man
import database.regulations_database_api as regulations_database_api
from models.users import UserRole
from models.regulations import IOSAItem
from models.httpio import JsonResponse
import lib.security as security_man
import lib.gemini as gemini_man
import lib.gpt_35t as gpt_35t_man


_ROOT_ROUTE = f"{os.getenv('API_ROOT')}/llm"
_MODULE_ID = 'routes.llm_api'
_ALLOWED_USERS = [UserRole.ADMIN, UserRole.AUDITOR]
router = APIRouter()


@router.post(f"{_ROOT_ROUTE}/iosa-audit")
async def iosa_audit(res: Response, regulation_id: str = Body(), checklist_code: str = Body(), text: str = Body(), x_auth=Header(alias='X-Auth', default=None)) -> JsonResponse:
    """Audit text against checklist_code from regulation_id using AI.\n
    =================================================================\n
    interface LLMIOSAItemResponse {\n
    text: string,\n
    score: 3 | 2 | 1 | 0,\n
    score_tag: 'FULLY_COMPLIANT' | 'PARTIALLY_COMPLIANT' | 'NON_COMPLIANT' | 'NONE',\n
    score_text: string,\n
    pct_score: float,\n
    children: LLMIOSAItemResponse[],\n
    };\n
    =================================================================\n
    Returns: {..., data: {\n
    score: 3 | 2 | 1 | 0,\n
    score_tag: 'FULLY_COMPLIANT' | 'PARTIALLY_COMPLIANT' | 'NON_COMPLIANT' | 'NONE',\n
    score_text: string,\n
    pct_score: float,\n
    comments: string,\n
    suggestions: string,\n
    modified: string,\n
    details: LLMIOSAItemResponse[],\n
    }}\n
    """
    func_id = f"{_MODULE_ID}.iosa_audit"
    await log_man.add_log(func_id, 'DEBUG', f"received iosa audit request: regulation_id={regulation_id}, checklist_code={checklist_code}")

    # authorize user
    auth_service_response = await security_man.authorize_api(x_auth, _ALLOWED_USERS, func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    # get IOSA item from database
    db_service_response = await regulations_database_api.get_iosa_checklist(regulation_id, checklist_code)
    if not db_service_response.success:
        res.status_code = db_service_response.status_code
        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )
    iosa_checklist: IOSAItem = db_service_response.data['iosa_checklist']

    # call llm api
    llm_service_response = await gpt_35t_man.iosa_audit_text(iosa_checklist, text)
    if not llm_service_response.success:
        res.status_code = llm_service_response.status_code
        return JsonResponse(
            success=llm_service_response.success,
            msg=llm_service_response.msg,
        )

    return JsonResponse(data=llm_service_response.data)
