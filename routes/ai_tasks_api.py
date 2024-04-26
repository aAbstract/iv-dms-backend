import os
from fastapi import APIRouter, Response, Header, Body
import lib.log as log_man
import lib.security as security_man
from models.users import UserRole
from models.httpio import JsonResponse
import database.ai_tasks_database_api as ai_tasks_database_api


_ROOT_ROUTE = f"{os.getenv('API_ROOT')}/ai-tasks"
_MODULE_ID = 'routes.ai_tasks_api'
_ALLOWED_USERS = [UserRole.ADMIN, UserRole.AUDITOR,UserRole.AIRLINES]
router = APIRouter()


@router.post(f"{_ROOT_ROUTE}/check-task")
async def check_task(res: Response, task_id: str = Body(embed=True), x_auth=Header(alias='X-Auth', default=None)) -> JsonResponse:
    """Gets AI task status with given task_id.\n
    ==========================================\n
    type AITaskStatus = 'IN_PROGRESS' | 'FINISHED' | 'FAILD';\n
    interface JsonResponse {\n
    success: boolean,\n
    msg: string,\n
    data: Object,\n
    };\n
    ==========================================\n
    Returns: {..., data: {\n
    ai_task_status: AITaskStatus,\n
    json_res: JsonResponse,\n
    }}\n
    """
    func_id = f"{_MODULE_ID}.check_task"

    # authorize user
    auth_service_response = await security_man.authorize_api(x_auth, _ALLOWED_USERS, func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    username = auth_service_response.data['token_claims']['username']
    await log_man.add_log(func_id, 'DEBUG', f"received check AI task request: task_id={task_id}, username={username}")

    # get AI task status
    db_service_response = await ai_tasks_database_api.get_ai_task_status(task_id, username)
    if not db_service_response.success:
        res.status_code = db_service_response.status_code
        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )
    return JsonResponse(data=db_service_response.data)


@router.post(f"{_ROOT_ROUTE}/get-all-tasks")
async def get_all_tasks(res: Response, x_auth=Header(alias='X-Auth', default=None)) -> JsonResponse:
    """Gets all AI tasks in the system for certain username.\n
    ========================================================\n
    type AITaskStatus = 'IN_PROGRESS' | 'FINISHED' | 'FAILD';\n
    type AITaskType = 'COMPLIANCE_CHECK' | 'PARSING_PDF' | 'SCANNING_PDF';\n
    interface AITask {\n
    id: string,\n
    start_datetime: Date,\n
    end_datetime: Date,\n
    task_type: AITaskType,\n
    task_status: AITaskStatus,\n
    };\n
    =========================================================\n
    Returns: {..., data: {\n
    ai_tasks: AITask[],\n
    }}\n
    """
    func_id = f"{_MODULE_ID}.get_all_tasks"

    # authorize user
    auth_service_response = await security_man.authorize_api(x_auth, _ALLOWED_USERS, func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    username = auth_service_response.data['token_claims']['username']
    await log_man.add_log(func_id, 'DEBUG', f"received getl all AI tasks request: username={username}")

    # get AI task status
    db_service_response = await ai_tasks_database_api.get_all_ai_tasks(username)
    if not db_service_response.success:
        res.status_code = db_service_response.status_code
        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )
    return JsonResponse(data=db_service_response.data)
