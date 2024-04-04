import os
from fastapi import APIRouter, Response, UploadFile, Header, Form
from typing import Annotated
import lib.log as log_man
import lib.security as security_man
from models.users import UserRole
from models.httpio import JsonResponse
from models.fs_index import IndexFileType
import database.fs_index_database_api as fs_index_database_api


_ROOT_ROUTE = f"{os.getenv('API_ROOT')}/attachments"
_MODULE_ID = 'routes.attachments_api'
_ALLOWED_USERS = [UserRole.ADMIN, UserRole.AUDITOR]
router = APIRouter()


@router.post(f"{_ROOT_ROUTE}/create-attachment")
async def create_attachment(file: UploadFile,airline_id: Annotated[str, Form()], res: Response, x_auth=Header(alias='X-Auth', default=None)):
    """Store attachment file in the database and return it's id.\n
    Returns: {..., data: {\n
    file_id: string,\n
    url_path: string,\n
    }}
    """
    func_id = f"{_MODULE_ID}.create_attachment"
    await log_man.add_log(func_id, "DEBUG", f"received create attachment file request: {file.filename}")

    # authorize user
    auth_service_response = await security_man.authorize_api(x_auth, _ALLOWED_USERS, func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    # save file to server
    username = auth_service_response.data['token_claims']['username']
    organization = auth_service_response.data['token_claims']['organization']
    fs_service_response = await fs_index_database_api.create_fs_index_entry(username=username, organization=organization,airline_id=airline_id, file_type=IndexFileType.AIRLINES_ATTACHMENT, filename=file.filename, data=file.file.read())
    if not fs_service_response.success:
        res.status_code = fs_service_response.status_code
        return JsonResponse(
            success=fs_service_response.success,
            msg=fs_service_response.msg,
        )

    return JsonResponse(data={
        'file_id': fs_service_response.data['file_id'],
        'url_path': fs_service_response.data['url_path'],
    })
