import os
from fastapi import APIRouter, Response, Header
import lib.log as log_man
import lib.security as security_man
from models.users import UserRoles
from models.httpio import JsonResponse
import database.regulations_database_api as regulations_database_api


_ROOT_ROUTE = f"{os.getenv('API_ROOT')}/regulations"
_MODULE_ID = 'routes.regulations_api'
_ALLOWED_USERS = [UserRoles.ADMIN, UserRoles.AUDITOR]
router = APIRouter()


@router.post(f"{_ROOT_ROUTE}/get-options")
async def get_options(res: Response, authorization=Header(default=None)) -> JsonResponse:
    """Get all regulations check lists meta data.\n
    Returns: {..., data: {\n
    regulations_options: <{id: string, type: string, name: string}>[]\n
    }}
    """
    func_id = f"{_MODULE_ID}.get_options"
    await log_man.add_log(func_id, 'DEBUG', 'received get regulations options request')

    # authorize user
    auth_service_response = await security_man.authorize_api(authorization, _ALLOWED_USERS, func_id)
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
