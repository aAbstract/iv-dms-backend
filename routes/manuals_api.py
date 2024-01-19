import os
from fastapi import APIRouter, Response, UploadFile, Header, Body, BackgroundTasks
import lib.log as log_man
import lib.security as security_man
from models.users import UserRole
from models.httpio import JsonResponse
from models.fs_index import IndexFileType, FSIndexFile
from models.regulations import IOSAItem
import database.manuals_database_api as manuals_database_api
import database.regulations_database_api as regulations_database_api
import database.fs_index_database_api as fs_index_database_api
import lib.chat_doc as chat_doc_man
import database.ai_tasks_database_api as ai_tasks_database_api
from models.ai_tasks import AITaskType


_ROOT_ROUTE = f"{os.getenv('API_ROOT')}/manuals"
_MODULE_ID = 'routes.manuals_api'
_ALLOWED_USERS = [UserRole.ADMIN, UserRole.AUDITOR]
router = APIRouter()


@router.post(f"{_ROOT_ROUTE}/parse-pdf")
async def parse_pdf(file: UploadFile, res: Response, x_auth=Header(alias='X-Auth', default=None)):
    """Parse PDF file, store it in the database and return it's id.\n
    Returns: {..., data: {doc_uuid: string}}
    """
    func_id = f"{_MODULE_ID}.parse_pdf"
    await log_man.add_log(func_id, "DEBUG", f"received parse pdf request: {file.filename}")

    # authorize user
    auth_service_response = await security_man.authorize_api(x_auth, _ALLOWED_USERS, func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    # parse file using ChatDOC API
    cd_service_response = await chat_doc_man.parse_doc(file.filename, file.file)
    if not cd_service_response.success:
        res.status_code = cd_service_response.status_code
        return JsonResponse(
            success=cd_service_response.success,
            msg=cd_service_response.msg,
        )

    # save file to server
    username = auth_service_response.data['token_claims']['username']
    fs_service_response = await fs_index_database_api.create_fs_index_entry(username, IndexFileType.AIRLINES_MANUAL, file.filename, cd_service_response.data['chat_doc_uuid'], file.file.read())
    if not fs_service_response.success:
        res.status_code = fs_service_response.status_code
        return JsonResponse(
            success=fs_service_response.success,
            msg=fs_service_response.msg,
        )

    return JsonResponse(data={
        'doc_uuid': cd_service_response.data['chat_doc_uuid'],
        'file_id': fs_service_response.data['file_id'],
        'url_path': fs_service_response.data['url_path'],
    })


@router.post(f"{_ROOT_ROUTE}/delete-manual")
async def delete_manual(res: Response, doc_uuid: str = Body(embed=True), x_auth=Header(alias='X-Auth', default=None)):
    """ Delete an airlines manual from database. [ALPHA] """
    func_id = f"{_MODULE_ID}.delete_manual"

    # authorize user
    auth_service_response = await security_man.authorize_api(x_auth, [UserRole.ADMIN], func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )
    await log_man.add_log(func_id, 'DEBUG', f"received delete manual request: username={auth_service_response.data['token_claims']['username']}, doc_uuid={doc_uuid}")

    fs_service_response = await fs_index_database_api.delete_fs_index_entry(doc_uuid)
    res.status_code = fs_service_response.status_code
    return JsonResponse(
        success=fs_service_response.success,
        msg=fs_service_response.msg,
    )

    # TODO-LATER: remove file from ChatDOC cloud


@router.post(f"{_ROOT_ROUTE}/get-page")
async def get_page(res: Response, manual_id: str = Body(), page_order: int = Body(), x_auth=Header(alias='X-Auth', default=None)) -> JsonResponse:
    """Get a page from a manual.\n
    Returns: {..., data: {page: string}}
    """
    func_id = f"{_MODULE_ID}.get_page"
    await log_man.add_log(func_id, 'DEBUG', f"received get manual page request: manual_id={manual_id}, page_order={page_order}")

    # authorize user
    auth_service_response = await security_man.authorize_api(x_auth, _ALLOWED_USERS, func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    db_service_response = await manuals_database_api.get_manual_page(manual_id, page_order)
    if not db_service_response.success:
        res.status_code = db_service_response.status_code
        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )
    return JsonResponse(data=db_service_response.data)


@router.post(f"{_ROOT_ROUTE}/get-meta-data")
async def get_meta_data(res: Response, manual_id: str = Body(embed=True), x_auth=Header(alias='X-Auth', default=None)) -> JsonResponse:
    """Get manual meta data.\n
    Returns: {..., data: {\n
    manual_meta_data: {id: string, name: string, page_count: number}\n
    }}
    """
    func_id = f"{_MODULE_ID}.get_meta_data"
    await log_man.add_log(func_id, 'DEBUG', f"received get manual meta data request: manual_id={manual_id}")

    # authorize user
    auth_service_response = await security_man.authorize_api(x_auth, _ALLOWED_USERS, func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    db_service_response = await manuals_database_api.get_manual_meta_data(manual_id)
    if not db_service_response.success:
        res.status_code = db_service_response.status_code
        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )
    return JsonResponse(data=db_service_response.data)


@router.post(f"{_ROOT_ROUTE}/get-options")
async def get_options(res: Response, x_auth=Header(alias='X-Auth', default=None)) -> JsonResponse:
    """Get all manuals meta data.\n
    =============================\n
    interface ManualOption {\n
    id: string,\n
    name: string,\n
    page_count: number,\n
    };\n
    =============================\n
    Returns: {..., data: {manuals_options: ManualOption[]}}
    """
    func_id = f"{_MODULE_ID}.get_options"
    await log_man.add_log(func_id, 'DEBUG', 'received get manuals options request')

    # authorize user
    auth_service_response = await security_man.authorize_api(x_auth, _ALLOWED_USERS, func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    db_service_response = await manuals_database_api.get_manuals_options()
    if not db_service_response.success:
        res.status_code = db_service_response.status_code
        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )
    return JsonResponse(data=db_service_response.data)


@router.post(f"{_ROOT_ROUTE}/scan-pdf")
async def scan_pdf(res: Response, background_tasks: BackgroundTasks, regulation_id: str = Body(), checklist_code: str = Body(), doc_uuid: str = Body(), x_auth=Header(alias='X-Auth', default=None)) -> JsonResponse:
    """Scan PDF to get a section that documents certain checklist_code.\n
    ===================================================================\n
    interface Match {\n
    text: string,\n
    refs: number[], // list of page numbers\n
    };\n
    ===================================================================\n
    Returns: {..., data: {\n
    matches: Match[],\n
    }}
    """
    func_id = f"{_MODULE_ID}.scan_pdf"
    await log_man.add_log(func_id, 'DEBUG', f"received scan pdf request: regulation_id={regulation_id}, checklist_code={checklist_code}, doc_uuid={doc_uuid}")

    # authorize user
    auth_service_response = await security_man.authorize_api(x_auth, _ALLOWED_USERS, func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    # get fs index entry
    fs_service_response = await fs_index_database_api.get_fs_index_entry(chat_doc_uuid=doc_uuid)
    if not fs_service_response.success:
        res.status_code = fs_service_response.status_code
        return JsonResponse(
            success=fs_service_response.success,
            msg=fs_service_response.msg,
        )
    fs_index_entry: FSIndexFile = fs_service_response.data['fs_index_entry']

    # get iosa item
    db_service_response = await regulations_database_api.get_iosa_checklist(regulation_id, checklist_code)
    if not db_service_response.success:
        res.status_code = db_service_response.status_code
        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )
    iosa_checklist: IOSAItem = db_service_response.data['iosa_checklist']

    # create AI task
    username = auth_service_response.data['token_claims']['username']
    ait_db_service_response = await ai_tasks_database_api.create_ai_task(username, AITaskType.SCANNING_PDF)
    if not ait_db_service_response.success:
        res.status_code = ait_db_service_response.status_code
        return JsonResponse(
            success=ait_db_service_response.success,
            msg=ait_db_service_response.msg,
        )

    # run FastAPI background task
    ai_task_id = ait_db_service_response.data['ai_task_id']
    background_tasks.add_task(chat_doc_man.scan_doc, fs_index_entry.doc_uuid, fs_index_entry.filename, iosa_checklist, ai_task_id)
    return JsonResponse(data={'ai_task_id': ai_task_id})


@router.post(f"{_ROOT_ROUTE}/check-pdf")
async def check_pdf(res: Response, doc_uuid: str = Body(embed=True), x_auth=Header(alias='X-Auth', default=None)) -> JsonResponse:
    """Check PDF parsing status.\n
    Returns: {..., data: {\n
    chat_doc_status: 'PARSED' | 'PARSING' | 'PARSING_FAILD'\n
    }}
    """
    func_id = f"{_MODULE_ID}.check_pdf"
    await log_man.add_log(func_id, 'DEBUG', f"received check pdf request: doc_uuid={doc_uuid}")

    # authorize user
    auth_service_response = await security_man.authorize_api(x_auth, _ALLOWED_USERS, func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    cd_service_response = await chat_doc_man.check_doc(doc_uuid)
    if not cd_service_response.success:
        res.status_code = cd_service_response.status_code
        return JsonResponse(
            success=cd_service_response.success,
            msg=cd_service_response.msg,
        )
    return JsonResponse(data=cd_service_response.data)


@router.post(f"{_ROOT_ROUTE}/get-manuals")
async def get_manuals(res: Response, x_auth=Header(alias='X-Auth', default=None)) -> JsonResponse:
    """Get user manuals and their parsing status.\n
    =============================================\n
    interface ManualFile {\n
    id: string,\n
    username: string,\n
    datetime: Date,\n
    file_type: IndexFileType, // 'AIRLINES_MANUAL' | 'AIRLINES_ATTACHMENT'\n
    filename: string,\n
    doc_uuid: string,\n
    url_path: string, // a link to the PDF file on the server\n
    doc_status: ChatDOCStatus, // 'PARSED' | 'PARSING' | 'PARSING_FAILD'\n
    };\n
    =============================================\n
    Returns: {..., data: {files: ManualFile[]}}
    """
    func_id = f"{_MODULE_ID}.get_manuals"
    # authorize user
    auth_service_response = await security_man.authorize_api(x_auth, _ALLOWED_USERS, func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )
    username = auth_service_response.data['token_claims']['username']
    await log_man.add_log(func_id, 'DEBUG', f"received get docs request: username={username}")

    fs_service_response = await fs_index_database_api.get_user_manuals(username)
    if not fs_service_response.success:
        res.status_code = fs_service_response.status_code
        return JsonResponse(
            success=fs_service_response.success,
            msg=fs_service_response.msg,
        )
    return JsonResponse(data=fs_service_response.data)
