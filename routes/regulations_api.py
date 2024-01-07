import os
from fastapi import APIRouter, Response, Header, Body
import lib.log as log_man
import lib.security as security_man
from models.users import UserRole
from models.httpio import JsonResponse
import database.regulations_database_api as regulations_database_api


_ROOT_ROUTE = f"{os.getenv('API_ROOT')}/regulations"
_MODULE_ID = 'routes.regulations_api'
_ALLOWED_USERS = [UserRole.ADMIN, UserRole.AUDITOR]
router = APIRouter()


@router.post(f"{_ROOT_ROUTE}/get-options")
async def get_options(res: Response, x_auth=Header(alias='X-Auth', default=None)) -> JsonResponse:
    """Get all regulations check lists meta data.\n
    Returns: {..., data: {\n
    regulations_options: <{id: string, type: string, name: string}>[]\n
    }}
    """
    func_id = f"{_MODULE_ID}.get_options"
    await log_man.add_log(func_id, 'DEBUG', 'received get regulations options request')

    # authorize user
    auth_service_response = await security_man.authorize_api(x_auth, _ALLOWED_USERS, func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    db_service_response = await regulations_database_api.get_regulations_options()
    res.status_code = db_service_response.status_code
    if not db_service_response.success:
        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )
    return JsonResponse(data=db_service_response.data)


@router.post(f"{_ROOT_ROUTE}/get-codes")
async def get_codes(res: Response, regulation_id: str = Body(embed=True), x_auth=Header(alias='X-Auth', default=None)) -> JsonResponse:
    """Get regulation codes.\n
    Returns: {..., data: {\n
    regulation_codes: <{section_name: string, section_code: string, checklist_codes: string[]}>[]\n
    }}
    """
    func_id = f"{_MODULE_ID}.get_codes"
    await log_man.add_log(func_id, 'DEBUG', f"received get regulation codes request: regulation_id={regulation_id}")

    # authorize user
    auth_service_response = await security_man.authorize_api(x_auth, _ALLOWED_USERS, func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    db_service_response = await regulations_database_api.get_regulation_codes(regulation_id)
    res.status_code = db_service_response.status_code
    if not db_service_response.success:
        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )
    return JsonResponse(data=db_service_response.data)


@router.post(f"{_ROOT_ROUTE}/get-iosa-map")
async def get_iosa_map(res: Response, regulation_id: str = Body(), checklist_code: str = Body(), x_auth=Header(alias='X-Auth', default=None)) -> JsonResponse:
    """Get index of a given checklist code in the regulations document.\n
    Returns: {..., data: {iosa_map: string[]}}
    """
    func_id = f"{_MODULE_ID}.get_iosa_map"
    await log_man.add_log(func_id, 'DEBUG', f"received get iosa map request: regulation_id={regulation_id}, checklist_code={checklist_code}")

    # authorize user
    auth_service_response = await security_man.authorize_api(x_auth, _ALLOWED_USERS, func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    db_service_response = await regulations_database_api.get_checklist_code_iosa_map(regulation_id, checklist_code)
    res.status_code = db_service_response.status_code
    if not db_service_response.success:
        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )
    return JsonResponse(data=db_service_response.data)


@router.post(f"{_ROOT_ROUTE}/get-iosa-checklist")
async def get_iosa_checklist(res: Response, regulation_id: str = Body(), checklist_code: str = Body(), x_auth=Header(alias='X-Auth', default=None)) -> JsonResponse:
    """Get iosa checklist details.\n
    ==============================\n
    interface Constrain {\n
    text: string,\n
    children: Constrain[],\n
    };\n
    ==============================\n
    Returns: {..., data: {\n
    code: string,\n
    guidance: string,\n
    iosa_map: string[],\n
    constraints: Constrain[],\n
    }}
    """
    func_id = f"{_MODULE_ID}.get_iosa_checklist"
    await log_man.add_log(func_id, 'DEBUG', f"received get iosa checklist request: regulation_id={regulation_id}, checklist_code={checklist_code}")

    # authorize user
    auth_service_response = await security_man.authorize_api(x_auth, _ALLOWED_USERS, func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    db_service_response = await regulations_database_api.get_iosa_checklist(regulation_id, checklist_code)
    res.status_code = db_service_response.status_code
    if not db_service_response.success:
        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )
    return JsonResponse(data=db_service_response.data)
