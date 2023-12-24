import os
from fastapi import APIRouter, Response, UploadFile, Header
import lib.log as log_man
import lib.security as security_man
from models.users import UserRoles
from models.httpio import JsonResponse, GetManualPageRequest
from models.manuals import UnstructuredManual
import database.manuals_database_api as manuals_database_api


_ROOT_ROUTE = f"{os.getenv('API_ROOT')}/manuals"
_MODULE_ID = 'routes.manuals_api'
_ALLOWED_USERS = [UserRoles.ADMIN, UserRoles.AUDITOR]
router = APIRouter()


@router.post(f"{_ROOT_ROUTE}/parse-pdf")
async def parse_pdf(file: UploadFile, res: Response, authorization=Header(default=None)):
    """ TODO """
    func_id = f"{_MODULE_ID}.parse_pdf"
    await log_man.add_log(func_id, 'DEBUG', f"received parse pdf request: {file.filename}")

    # authorize user
    auth_service_response = await security_man.authorize_api(authorization, _ALLOWED_USERS, func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    # TODO-GAMAL: parse {file}
    parsed_file = UnstructuredManual(
        name=file.filename,
        pages=[
            'page1 content',
            'page2 content',
            'page3 content',
        ],
    )
    # TODO-GAMAL: store {parsed_file} in database collection unstructured_manuals
    return JsonResponse(data={'manual_id': 'database_id'})


@router.post(f"{_ROOT_ROUTE}/get-page")
async def get_page(req: GetManualPageRequest, res: Response, authorization=Header(default=None)):
    """Gets a page from a manual.\n
    Returns: {..., "data": {"page": string}}.
    """
    func_id = f"{_MODULE_ID}.get_page"
    await log_man.add_log(func_id, 'DEBUG', f"received get manual page request: {req}")

    # authorize user
    auth_service_response = await security_man.authorize_api(authorization, _ALLOWED_USERS, func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    db_service_response = await manuals_database_api.get_manual_page(req.manual_id, req.page_order)
    res.status_code = db_service_response.status_code
    if not db_service_response.success:
        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )
    return JsonResponse(data=db_service_response.data)
