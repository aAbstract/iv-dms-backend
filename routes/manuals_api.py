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
from database.mongo_driver import get_database


_ROOT_ROUTE = f"{os.getenv('API_ROOT')}/manuals"
_MODULE_ID = 'routes.manuals_api'
_ALLOWED_USERS = [UserRole.ADMIN, UserRole.AUDITOR]
router = APIRouter()


@router.post(f"{_ROOT_ROUTE}/parse-pdf")
async def parse_pdf(file: UploadFile, res: Response, x_auth=Header(alias='X-Auth', default=None)):
    """Parse PDF file, store it in the database and return it's id.\n
    Returns: {..., data: {\n
    doc_uuid: string,\n
    file_id: string,\n
    url_path: string,\n
    }}
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

    file_ext = os.path.splitext(file.filename)[1]
    if file_ext != '.pdf':
        res.status_code = 409
        return JsonResponse(
            success=False,
            msg='Bad File Extention',
        )

    # parse file using ChatDOC API
    cd_service_response = await chat_doc_man.parse_doc(file.filename, file.file)
    if not cd_service_response.success:
        res.status_code = cd_service_response.status_code
        return JsonResponse(
            success=cd_service_response.success,
            msg=cd_service_response.msg,
        )

    # TODO-L0: add doc parsing status check background task

    # save file to server
    username = auth_service_response.data['token_claims']['username']
    organization = auth_service_response.data['token_claims']['organization']
    fs_service_response = await fs_index_database_api.create_fs_index_entry(username, organization, IndexFileType.AIRLINES_MANUAL, file.filename, file.file.read(), chat_doc_uuid=cd_service_response.data['chat_doc_uuid'])
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


@router.post(f"{_ROOT_ROUTE}/create-manual")
async def create_manual(file: UploadFile, res: Response, x_auth=Header(alias='X-Auth', default=None)):
    """
    Create fs index from file
    """
    func_id = f"{_MODULE_ID}.create_manual"

    # authorize user
    auth_service_response = await security_man.authorize_api(x_auth, _ALLOWED_USERS, func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )
    username = auth_service_response.data['token_claims']['username']
    organization = auth_service_response.data['token_claims']['organization']

    await log_man.add_log(func_id, "DEBUG", f"received create manual request: {file.filename}, username:{username}, organization:{organization}")

    file_ext = os.path.splitext(file.filename)[1]
    if file_ext != '.pdf':
        res.status_code = 409
        return JsonResponse(
            success=False,
            msg='Bad File Extention',
        )

    # save file to server
    fs_service_response = await fs_index_database_api.create_fs_index_entry(username, organization, IndexFileType.AIRLINES_MANUAL, file.filename, file.file.read())
    if not fs_service_response.success:
        res.status_code = fs_service_response.status_code
        return JsonResponse(
            success=fs_service_response.success,
            msg=fs_service_response.msg,
        )

    return JsonResponse(data={
        'doc_uuid': "00000000-0000-0000-0000-000000000000",
        'file_id': fs_service_response.data['file_id'],
        'url_path': fs_service_response.data['url_path'],
    })


@router.post(f"{_ROOT_ROUTE}/list-manuals")
async def list_manuals(res: Response, x_auth=Header(alias='X-Auth', default=None)):
    """ list all manuals that belong to this organization"""
    func_id = f"{_MODULE_ID}.list_manuals"

    # authorize user
    auth_service_response = await security_man.authorize_api(x_auth, [UserRole.ADMIN, UserRole.AUDITOR], func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    await log_man.add_log(func_id, 'DEBUG', f"received list manuals request: username={auth_service_response.data['token_claims']['username']}, organization={auth_service_response.data['token_claims']['organization']}")

    fs_service_response = await fs_index_database_api.list_fs_index(auth_service_response.data['token_claims']['organization'])
    res.status_code = fs_service_response.status_code
    return JsonResponse(
        success=fs_service_response.success,
        msg=fs_service_response.msg,
        data=fs_service_response.data
    )


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

    fs_service_response = await fs_index_database_api.delete_fs_index_entry(doc_uuid, auth_service_response.data['token_claims']['organization'])
    res.status_code = fs_service_response.status_code
    return JsonResponse(
        success=fs_service_response.success,
        msg=fs_service_response.msg,
    )
    # TODO-LATER: remove file from ChatDOC cloud
@router.post(f"{_ROOT_ROUTE}/rename-manual")
async def rename_manual(res: Response, doc_uuid: str = Body(embed=True),new_name: str = Body(embed=True), x_auth=Header(alias='X-Auth', default=None)):
    """ rename an airlines manual from database."""
    func_id = f"{_MODULE_ID}.rename_manual"

    # authorize user
    auth_service_response = await security_man.authorize_api(x_auth, [UserRole.ADMIN], func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )
    await log_man.add_log(func_id, 'DEBUG', f"received rename manual request: username={auth_service_response.data['token_claims']['username']},organization={auth_service_response.data['token_claims']['organization']}, doc_uuid={doc_uuid}")

    fs_service_response = await fs_index_database_api.rename_fs_index_entry(doc_uuid, auth_service_response.data['token_claims']['organization'],new_name)
    res.status_code = fs_service_response.status_code
    return JsonResponse(
        success=fs_service_response.success,
        msg=fs_service_response.msg,
    )

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


@router.post(f"{_ROOT_ROUTE}/get-tree")
async def get_tree(res: Response, doc_uuid: str = Body(embed=True), x_auth=Header(alias='X-Auth', default=None)) -> JsonResponse:
    """Get Tree structure of manual.\n
    =============================================\n
    Input {\n
        doc_uuid: string,\n
    }
    =============================================\n
    Returns: {..., data: {tree: list[TreeFSIndex]}}
    """
    func_id = f"{_MODULE_ID}.get_tree"
    # authorize user
    auth_service_response = await security_man.authorize_api(x_auth, _ALLOWED_USERS, func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )
    username = auth_service_response.data['token_claims']['username']
    organization = auth_service_response.data['token_claims']['organization']
    await log_man.add_log(func_id, 'DEBUG', f"received get docs request: username={username}, organization={organization}")

    # TODO-GALAL: remove this
    if doc_uuid != os.environ['COMPLETE_CHAT_DOC_UUID']:
        return JsonResponse(data={'tree': []})

    # get table of content (toc) pages
    toc_pages = [9, 77, 133, 155, 173, 183, 215, 239, 253, 611, 633, 693, 759, 767, 821, 861]  # TODO-GALAL: laod toc_pages from database
    get_pages_service_response = await fs_index_database_api.get_pages(organization, toc_pages, doc_uuid)

    if not get_pages_service_response.success:
        res.status_code = get_pages_service_response.status_code
        return JsonResponse(
            success=get_pages_service_response.success,
            msg=get_pages_service_response.msg,
        )

    # get tree
    fs_service_response = await fs_index_database_api.get_tree_structure(get_pages_service_response.data['text'])

    if not fs_service_response.success:
        res.status_code = fs_service_response.status_code
        return JsonResponse(
            success=fs_service_response.success,
            msg=fs_service_response.msg,
        )

    return JsonResponse(data=fs_service_response.data)


@router.post(f"{_ROOT_ROUTE}/get-tree-v2")
async def get_tree_v2(res: Response, doc_uuid: str = Body(embed=True), x_auth=Header(alias='X-Auth', default=None)) -> JsonResponse:
    # TODO-GALAL: clean this route
    func_id = f"{_MODULE_ID}.get_tree_v2"
    # authorize user
    auth_service_response = await security_man.authorize_api(x_auth, _ALLOWED_USERS, func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )
    await log_man.add_log(func_id, 'DEBUG', f"received get manual content tree request: doc_uuid={doc_uuid}")

    fs_index_entry = await get_database().get_collection('fs_index').find_one({'doc_uuid': doc_uuid})
    if not fs_index_entry:
        return JsonResponse(success=False, msg='File Index not Found', status_code=404)

    return JsonResponse(data={'toc_info': fs_index_entry['args']['toc_info']})

@router.post(f"{_ROOT_ROUTE}/get-all-trees")
async def get_all_trees(res: Response, x_auth=Header(alias='X-Auth', default=None)) -> JsonResponse:

    func_id = f"{_MODULE_ID}.get_all_trees"

    # authorize user
    auth_service_response = await security_man.authorize_api(x_auth, _ALLOWED_USERS, func_id)
    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )
    username = auth_service_response.data['token_claims']['username']
    organization = auth_service_response.data['token_claims']['organization']
    await log_man.add_log(func_id, 'DEBUG', f"received get all trees request: username={username} organization={organization}")
    
    # get tree
    fs_service_response = await fs_index_database_api.get_all_tree_db(organization=organization)

    if not fs_service_response.success:
        res.status_code = fs_service_response.status_code
        return JsonResponse(
            success=fs_service_response.success,
            msg=fs_service_response.msg,
        )

    return JsonResponse(data=fs_service_response.data)