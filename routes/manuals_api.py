import os
from fastapi import APIRouter, Response, UploadFile, Header
import lib.log as log_man
import lib.security as security_man
from models.users import UserRoles
from models.httpio import JsonResponse, GetManualPageRequest, GetManualMetaDataRequest, DeleteManualRequest
from models.manuals import UnstructuredManual
import database.manuals_database_api as manuals_database_api
import lib.pdf as pdf_man


_ROOT_ROUTE = f"{os.getenv('API_ROOT')}/manuals"
_MODULE_ID = 'routes.manuals_api'
_ALLOWED_USERS = [UserRoles.ADMIN, UserRoles.AUDITOR]
router = APIRouter()


@router.post(f"{_ROOT_ROUTE}/parse-pdf")
async def parse_pdf(file: UploadFile, res: Response, authorization=Header(default=None)):
    """ TODO """
    func_id = f"{_MODULE_ID}.parse_pdf"
    await log_man.add_log(func_id, "DEBUG", f"received parse pdf request: {file.filename}")

    # authorize user
    auth_service_response = await security_man.authorize_api(authorization, _ALLOWED_USERS, func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    all_pages = pdf_man.extract(file.file)

    parsed_file = UnstructuredManual(
        name=file.filename,
        pages=all_pages,
    )

    db_service_response = await manuals_database_api.create_unstructured_manual(parsed_file)
    res.status_code = db_service_response.status_code
    if not db_service_response.success:
        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )
    return JsonResponse(data=db_service_response.data)


@router.post(f"{_ROOT_ROUTE}/delete-manual")
async def delete_manual(req: DeleteManualRequest, res: Response, authorization=Header(default=None)):
    """ TODO """
    func_id = f"{_MODULE_ID}.delete_manual"

    # authorize user
    auth_service_response = await security_man.authorize_api(authorization, [UserRoles.ADMIN], func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )
    await log_man.add_log(func_id, 'DEBUG', f"received delete manual request: username={auth_service_response.data['token_claims']['username']}, manual_id={req.manual_id}")

    db_service_response = await manuals_database_api.delete_unstructured_manual(req.manual_id)
    res.status_code = db_service_response.status_code
    return JsonResponse(
        success=db_service_response.success,
        msg=db_service_response.msg,
    )


@router.post(f"{_ROOT_ROUTE}/get-page")
async def get_page(req: GetManualPageRequest, res: Response, authorization=Header(default=None)) -> JsonResponse:
    """Get a page from a manual.\n
    Returns: {..., data: {page: string}}
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


@router.post(f"{_ROOT_ROUTE}/get-meta-data")
async def get_meta_data(req: GetManualMetaDataRequest, res: Response, authorization=Header(default=None)) -> JsonResponse:
    """Get manual meta data.\n
    Returns: {..., data: {\n
    manual_meta_data: {id: string, name: string, page_count: number}\n
    }}
    """
    func_id = f"{_MODULE_ID}.get_meta_data"
    await log_man.add_log(func_id, 'DEBUG', f"received get manual meta data request: {req}")

    # authorize user
    auth_service_response = await security_man.authorize_api(authorization, _ALLOWED_USERS, func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    db_service_response = await manuals_database_api.get_manual_meta_data(req.manual_id)
    res.status_code = db_service_response.status_code
    if not db_service_response.success:
        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )
    return JsonResponse(data=db_service_response.data)


@router.post(f"{_ROOT_ROUTE}/get-options")
async def get_options(res: Response, authorization=Header(default=None)) -> JsonResponse:
    """Get all manuals meta data.\n
    Returns: {..., data: {\n
    manuals_options: <{id: string, name: string, page_count: number}>[]\n
    }}
    """
    func_id = f"{_MODULE_ID}.get_options"
    await log_man.add_log(func_id, 'DEBUG', 'received get manuals options request')

    # authorize user
    auth_service_response = await security_man.authorize_api(authorization, _ALLOWED_USERS, func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    db_service_response = await manuals_database_api.get_manuals_options()
    res.status_code = db_service_response.status_code
    if not db_service_response.success:
        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )
    return JsonResponse(data=db_service_response.data)
