import os
from fastapi import APIRouter, Response, Header
import lib.log as log_man
import lib.security as security_man
from models.users import UserRoles
from models.httpio import JsonResponse
import database.activity_database_api as activity_database_api
from models.httpio import GetLogsRequest


_ROOT_ROUTE = f"{os.getenv('API_ROOT')}/activity"
_MODULE_ID = 'routes.activity_api'
_ALLOWED_USERS = [UserRoles.ADMIN]
router = APIRouter()


@router.post(f"{_ROOT_ROUTE}/get-logs")
async def get_logs(req: GetLogsRequest, res: Response, authorization=Header(default=None)):
    func_id = f"{_MODULE_ID}.get_logs"

    # authorize user
    auth_service_response = await security_man.authorize_api(authorization, _ALLOWED_USERS, func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )
    await log_man.add_log(func_id, 'DEBUG', f"received get logs request: username={auth_service_response.data['token_claims']['username']}, limit={req.limit}")

    # get activity logs
    db_service_response = await activity_database_api.get_logs(req.limit)
    res.status_code = db_service_response.status_code
    if not db_service_response.success:
        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )
    return JsonResponse(data=db_service_response.data)
