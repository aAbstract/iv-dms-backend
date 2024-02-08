import os
from fastapi import APIRouter, Response, Header, Body
import lib.log as log_man
import lib.security as security_man
from models.users import UserRole
from models.httpio import JsonResponse
from database.flow_report_database_api import *
from datetime import datetime

_ROOT_ROUTE = f"{os.getenv('API_ROOT')}/flow_report"
_MODULE_ID = "routes.flow_report_api"
_ALLOWED_USERS = [UserRole.ADMIN, UserRole.AUDITOR]
router = APIRouter()

@router.post(f"{_ROOT_ROUTE}/create-flow-report")
async def create_flow_report(
    res: Response,
    regulation_id: str = Body(embed=True),
    title: str = Body(embed=True),
    checklist_template_code: str = Body(embed=True),
    x_auth=Header(alias="X-Auth", default=None),
) -> JsonResponse:
    func_id = f"{_MODULE_ID}.create_flow_report"
    # authorize user
    auth_service_response = await security_man.authorize_api(
        x_auth, _ALLOWED_USERS, func_id
    )
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    await log_man.add_log(
        func_id,
        "DEBUG",
        f"received create flow report request: username={auth_service_response.data['token_claims']['username']} organization={auth_service_response.data['token_claims']['organization']}",
    )

    db_service_response = await create_flow_report_db(
        regulation_id=regulation_id,
        title=title,
        checklist_template_code=checklist_template_code,
        organization=auth_service_response.data["token_claims"]["organization"],
        username=auth_service_response.data["token_claims"]["username"],
    )

    if not db_service_response.success:
        res.status_code = db_service_response.status_code
        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )

    return JsonResponse(data=db_service_response.data)

@router.post(f"{_ROOT_ROUTE}/list-flow-report")
async def list_flow_report(
    res: Response,creator:str=Body(embed=True), x_auth=Header(alias="X-Auth", default=None)
) -> JsonResponse:
    func_id = f"{_MODULE_ID}.list_flow_report"
    # authorize user
    auth_service_response = await security_man.authorize_api(
        x_auth, _ALLOWED_USERS, func_id
    )
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    await log_man.add_log(
        func_id,
        "DEBUG",
        f"received list flow report request: username={auth_service_response.data['token_claims']['username']} organization={auth_service_response.data['token_claims']['organization']}",
    )

    db_service_response = await list_flow_report_db(
        organization=auth_service_response.data["token_claims"]["organization"],creator=creator
    )

    if not db_service_response.success:
        res.status_code = db_service_response.status_code
        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )
    return JsonResponse(data=db_service_response.data)

@router.post(f"{_ROOT_ROUTE}/get-flow-report")
async def get_flow_report(
    res: Response,
    flow_report_id: str = Body(embed=True),
    x_auth=Header(alias="X-Auth", default=None),
) -> JsonResponse:
    func_id = f"{_MODULE_ID}.get_flow_report_history"
    # authorize user
    auth_service_response = await security_man.authorize_api(
        x_auth, _ALLOWED_USERS, func_id
    )
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    await log_man.add_log(
        func_id,
        "DEBUG",
        f"received get flow report history request: username={auth_service_response.data['token_claims']['username']} organization={auth_service_response.data['token_claims']['organization']}",
    )

    db_service_response = await get_flow_report_db(
        username=auth_service_response.data["token_claims"]["username"],
        flow_report_id=flow_report_id,
        organization=auth_service_response.data["token_claims"]["organization"],
    )

    if not db_service_response.success:
        res.status_code = db_service_response.status_code
        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )
    return JsonResponse(data=db_service_response.data)

@router.post(f"{_ROOT_ROUTE}/delete-flow-report")
async def delete_flow_report(
    res: Response,
    flow_report_id: str = Body(embed=True),
    comment: str = Body(embed=True),
    x_auth=Header(alias="X-Auth", default=None),
) -> JsonResponse:
    func_id = f"{_MODULE_ID}.delete_flow_report"
    # authorize user
    auth_service_response = await security_man.authorize_api(
        x_auth, _ALLOWED_USERS, func_id
    )
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    await log_man.add_log(
        func_id,
        "DEBUG",
        f"received delete flow report request: username={auth_service_response.data['token_claims']['username']} organization={auth_service_response.data['token_claims']['organization']}",
    )

    db_service_response = await delete_flow_report_db(
        user_comment=comment,
        username=auth_service_response.data["token_claims"]["username"],
        flow_report_id=flow_report_id,
        organization=auth_service_response.data["token_claims"]["organization"],
    )

    if not db_service_response.success:
        res.status_code = db_service_response.status_code
        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )
    return JsonResponse(data=db_service_response.data)

@router.post(f"{_ROOT_ROUTE}/update-flow-report-sub-sections")
async def update_flow_report_sub_sections(
    res: Response,
    flow_report_id: str = Body(embed=True),
    comment: str = Body(embed=True),
    sub_sections: list = Body(embed=True),
    x_auth=Header(alias="X-Auth", default=None),
) -> JsonResponse:
    func_id = f"{_MODULE_ID}.update_flow_report_sub_sections"
    # authorize user
    auth_service_response = await security_man.authorize_api(
        x_auth, _ALLOWED_USERS, func_id
    )
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    await log_man.add_log(
        func_id,
        "DEBUG",
        f"received update flow report sub-sections request: username={auth_service_response.data['token_claims']['username']} organization={auth_service_response.data['token_claims']['organization']}",
    )

    db_service_response = await change_flow_report_sub_sections_db(
        comment=comment,
        username=auth_service_response.data["token_claims"]["username"],
        flow_report_id=flow_report_id,
        organization=auth_service_response.data["token_claims"]["organization"],
        sub_sections=sub_sections,
    )

    if not db_service_response.success:
        res.status_code = db_service_response.status_code
        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )
    
    return JsonResponse(data=db_service_response.data)