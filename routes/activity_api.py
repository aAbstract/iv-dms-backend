import os
from fastapi import APIRouter, Response, Header, Body
import lib.log as log_man
import lib.security as security_man
from models.users import UserRole
from models.httpio import JsonResponse
import database.activity_database_api as activity_database_api


_ROOT_ROUTE = f"{os.getenv('API_ROOT')}/activity"
_MODULE_ID = 'routes.activity_api'
_ALLOWED_USERS = [UserRole.ADMIN]
router = APIRouter()


@router.post(f"{_ROOT_ROUTE}/get-logs")
async def get_logs(res: Response, limit: int = Body(embed=True), x_auth=Header(alias='X-Auth', default=None)) -> JsonResponse:
    """Get activity logs.\n
    =====================\n
    interface Log {\n
    id: string,\n
    level: string,\n
    description: string,\n
    datetime: Date,\n
    source: string,\n
    };\n
    =====================\n
    Returns: {..., data: {logs: Log[]}}
    """
    func_id = f"{_MODULE_ID}.get_logs"

    # authorize user
    auth_service_response = await security_man.authorize_api(x_auth, _ALLOWED_USERS, func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )
    await log_man.add_log(func_id, 'DEBUG', f"received get logs request: username={auth_service_response.data['token_claims']['username']}, limit={limit}")

    # get activity logs
    db_service_response = await activity_database_api.get_logs(limit)
    if not db_service_response.success:
        res.status_code = db_service_response.status_code
        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )
    return JsonResponse(data=db_service_response.data)

@router.post(f"{_ROOT_ROUTE}/get-user-activity")
async def get_user_activity(res: Response, x_auth=Header(alias='X-Auth', default=None)) -> JsonResponse:
    """Get user AI activity.\n
    Returns: {..., data: {\n
        gemini_audits: int,
        chatdoc_parse_docs: int,
        chatdoc_check_docs: int,
        chatdoc_scan_docs: int}}
    """
    func_id = f"{_MODULE_ID}.get-user-activity"
    # authorize user
    auth_service_response = await security_man.authorize_api(x_auth, _ALLOWED_USERS, func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )
    await log_man.add_log(func_id, 'DEBUG', f"received get logs request: username={auth_service_response.data['token_claims']['username']}")

    # get activity logs
    db_service_response = await activity_database_api.get_activity(auth_service_response.data['token_claims']['username'])
    if not db_service_response.success:
        res.status_code = db_service_response.status_code
        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )
    return JsonResponse(data=db_service_response.data)