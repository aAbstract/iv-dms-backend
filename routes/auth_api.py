import os
from fastapi import APIRouter, Response
import lib.log as log_man
import database.users_database_api as users_database_api
from models.httpio import LoginRequest
from models.httpio import JsonResponse


_ROOT_ROUTE = f"{os.getenv('API_ROOT')}/auth"
_MODULE_ID = 'routes.auth_api'
router = APIRouter()


@router.post(f"{_ROOT_ROUTE}/login")
async def login(req: LoginRequest, res: Response) -> JsonResponse:
    """Handles user login request by validating credentials and generating JWT token.\n
    Returns: {..., "data": {"access_token": string}}.
    """
    func_id = f"{_MODULE_ID}.login"
    await log_man.add_log(func_id, 'DEBUG', f"received login request: {req}")

    db_service_response = await users_database_api.login_user(req.username, req.password)
    res.status_code = db_service_response.status_code

    if not db_service_response.success:
        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )

    return JsonResponse(data=db_service_response.data)
