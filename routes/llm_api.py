import os
from fastapi import APIRouter, Response, Body, Header
import lib.log as log_man
import database.regulations_database_api as regulations_database_api
import database.fs_index_database_api as fs_index_database_api
import database.gpt35t_contexts_database_api as gpt35t_contexts_database_api
from models.users import UserRole
from models.regulations import IOSAItem, RegulationType
from models.httpio import JsonResponse
import lib.security as security_man
import lib.gpt_35t_unstruct as gpt_35t_unstruct
import lib.gpt_35t_struct as gpt_35t_struct
from models.gpt_35t import GPT35TAuditTag
import lib.sonnet_unstruct as sonnet_unstruct

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
    llm_service_response = await gpt_35t_struct.iosa_audit_text(iosa_checklist, text)
    if not llm_service_response.success:
        res.status_code = llm_service_response.status_code
        return JsonResponse(
            success=llm_service_response.success,
            msg=llm_service_response.msg,
        )

    return JsonResponse(data=llm_service_response.data)


@router.post(f"{_ROOT_ROUTE}/iosa-audit-unstruct")
async def iosa_audit_unstruct(res: Response, regulation_id: str = Body(), checklist_code: str = Body(), text: str = Body(), x_auth=Header(alias='X-Auth', default=None)) -> JsonResponse:
    """Audit text against checklist_code from regulation_id using AI.\n
    =================================================================\n
    Returns: {..., data: {\n
    llm_resp: string,\n
    overall_compliance_score: number, // [0, 100]\n
    context_id: string, // LLM context identifier\n
    }}\n
    """
    func_id = f"{_MODULE_ID}.iosa_audit_unstruct"
    await log_man.add_log(func_id, 'DEBUG', f"received iosa audit unstruct request: regulation_id={regulation_id}, checklist_code={checklist_code}")

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
    regulation_type: RegulationType = db_service_response.data['regulation_type']

    llm_service_response = await sonnet_unstruct.llm_audit_item(iosa_checklist, text,regulation_type)
    if not llm_service_response.success:
        res.status_code = llm_service_response.status_code
        return JsonResponse(
            success=llm_service_response.success,
            msg=llm_service_response.msg,
        )

    # create chat context entry
    gpt35t_cdb_service_response = await gpt35t_contexts_database_api.create_gpt35t_context(
        auth_service_response.data['token_claims']['username'],
        auth_service_response.data['token_claims']['organization'],
        llm_service_response.data['conversation'],
    )

    return JsonResponse(data={
        'llm_resp': llm_service_response.data['llm_resp'],
        'overall_compliance_score': llm_service_response.data['overall_compliance_score'],
        'overall_compliance_tag': llm_service_response.data['overall_compliance_tag'],
        'context_id': gpt35t_cdb_service_response.data['context_id']
    })


@router.post(f"{_ROOT_ROUTE}/iosa-enhance-unstruct")
async def iosa_enhance_unstruct(res: Response,overall_compliance_tag:str=Body(embed=True) ,regulation_id: str = Body(embed=True), checklist_code: str = Body(embed=True),  context_id: str = Body(embed=True), x_auth=Header(alias='X-Auth', default=None)) -> JsonResponse:
    """Apply suggested AI recommendations to enhance overall compliance score.\n
    =================================================================\n
    Returns: {..., data: {\n
    llm_resp: string,\n
    new_compliance_score: number, // [0, 100]\n
    context_id: string,\n // LLM context identifier
    }}\n
    """
    func_id = f"{_MODULE_ID}.iosa_enhance_unstruct"
    await log_man.add_log(func_id, 'DEBUG', f"received iosa enhance unstruct request: context_id={context_id}")

    # authorize user
    auth_service_response = await security_man.authorize_api(x_auth, _ALLOWED_USERS, func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    if(overall_compliance_tag == GPT35TAuditTag.NON_COMPLIANT):
        
        # get IOSA item from database
        db_service_response = await regulations_database_api.get_iosa_checklist(regulation_id, checklist_code)
        if not db_service_response.success:
            res.status_code = db_service_response.status_code
            return JsonResponse(
                success=db_service_response.success,
                msg=db_service_response.msg,
            )
        iosa_checklist: IOSAItem = db_service_response.data['iosa_checklist']

        # call LLM API
        llm_service_response = await gpt_35t_unstruct.iosa_generate_text(iosa_checklist)
        if not llm_service_response.success:
            res.status_code = llm_service_response.status_code
            return JsonResponse(
                success=llm_service_response.success,
                msg=llm_service_response.msg,
            )
        # create chat context entry
        gpt35t_cdb_service_response = await gpt35t_contexts_database_api.create_gpt35t_context(
            auth_service_response.data['token_claims']['username'],
            auth_service_response.data['token_claims']['organization'],
            llm_service_response.data['conversation'],
        )
        context_id = gpt35t_cdb_service_response.data['context_id']
    elif(overall_compliance_tag == GPT35TAuditTag.PARTIALLY_COMPLIANT):
        
        # get context from database
        db_service_response = await gpt35t_contexts_database_api.get_gpt35t_context(context_id,auth_service_response.data['token_claims']['organization'])
        if not db_service_response.success:
            res.status_code = db_service_response.status_code
            return JsonResponse(
                success=db_service_response.success,
                msg=db_service_response.msg,
            )

        # call LLM API
        gpt35t_context = db_service_response.data['gpt35t_context']
        llm_service_response = await gpt_35t_unstruct.iosa_enhance_text(gpt35t_context)
        if not llm_service_response.success:
            res.status_code = llm_service_response.status_code
            return JsonResponse(
                success=llm_service_response.success,
                msg=llm_service_response.msg,
            )

        # update gpt35t context in database
        gpt35t_cdb_service_response = await gpt35t_contexts_database_api.update_gpt35t_context(context_id,auth_service_response.data['token_claims']['organization'], llm_service_response.data['conversation'])
        if not gpt35t_cdb_service_response.success:
            res.status_code = gpt35t_cdb_service_response.status_code
            return JsonResponse(
                success=gpt35t_cdb_service_response.success,
                msg=gpt35t_cdb_service_response.msg,
            )
    else:
        return JsonResponse(
           success=False,
            msg="Invalid Audit Tag Type",
    )

    return JsonResponse(data={
        'llm_resp': llm_service_response.data['llm_resp'],
        'overall_compliance_score': llm_service_response.data['overall_compliance_score'],
        'overall_compliance_tag': llm_service_response.data['overall_compliance_tag'],
        'context_id': context_id
    })

@router.post(f"{_ROOT_ROUTE}/iosa-audit-pages")
async def iosa_audit_pages(res: Response, regulation_id: str = Body(embed=True), checklist_code: str = Body(embed=True), text: str = Body(embed = True), pagesMapper: dict[str, list[str]] = Body(embed=True), x_auth=Header(alias='X-Auth', default=None)) -> JsonResponse:
    """Audit text against pages from an FSIndex entry using Chatdoc ID.\n
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
    func_id = f"{_MODULE_ID}.iosa_audit_pages"

    # authorize user
    auth_service_response = await security_man.authorize_api(x_auth, _ALLOWED_USERS, func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    username = auth_service_response.data['token_claims']['username']
    organization = auth_service_response.data['token_claims']['organization']

    await log_man.add_log(func_id, 'DEBUG', f"received iosa audit pages request: username = {username}, organization= {organization}, regulation_id={regulation_id}, pagesMapper: {pagesMapper}, checklist_code={checklist_code}")

   
    # get IOSA item from database
    db_service_response = await regulations_database_api.get_iosa_checklist(regulation_id, checklist_code)
    if not db_service_response.success:
        res.status_code = db_service_response.status_code
        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )
    iosa_checklist: IOSAItem = db_service_response.data['iosa_checklist']
    regulation_type: RegulationType = db_service_response.data['regulation_type']

    # call get pages api
    get_pages_service_response = await fs_index_database_api.get_pages_from_sections(organization, pagesMapper)
    if not get_pages_service_response.success:
        res.status_code = get_pages_service_response.status_code
        return JsonResponse(
            success=get_pages_service_response.success,
            msg=get_pages_service_response.msg,
        )
    text_to_audit = get_pages_service_response.data['text']

    # Select sent text if sent from front
    if text.strip():
       iosa_checklist.paragraph = text.strip()

    llm_service_response = await sonnet_unstruct.llm_audit_item(iosa_checklist, text_to_audit,regulation_type)
    if not llm_service_response.success:
        res.status_code = llm_service_response.status_code
        return JsonResponse(
            success=llm_service_response.success,
            msg=llm_service_response.msg,
        )

    # create chat context entry
    gpt35t_cdb_service_response = await gpt35t_contexts_database_api.create_gpt35t_context(
        auth_service_response.data['token_claims']['username'],
        auth_service_response.data['token_claims']['organization'],
        llm_service_response.data['conversation'],
    )

    return JsonResponse(data={
        'llm_resp': llm_service_response.data['llm_resp'],
        'overall_compliance_score': llm_service_response.data['overall_compliance_score'],
        'overall_compliance_tag': llm_service_response.data['overall_compliance_tag'],
        'manual_ref_text': get_pages_service_response.data['text'],
        'context_id': gpt35t_cdb_service_response.data['context_id'],
    })
