import os
import aiofiles
import aiofiles.os
from datetime import datetime
from models.fs_index import FSIndexFile, IndexFileType, FILE_TYPE_PATH_MAP, ChatDOCStatus
from models.runtime import ServiceResponse
from database.mongo_driver import get_database, validate_bson_id


_PUBLIC_DIR = 'public'


async def create_fs_index_entry(username: str, file_type: IndexFileType, filename: str, chat_doc_uuid: str, data: bytes) -> ServiceResponse:
    # check file extention
    file_ext = os.path.splitext(filename)[1]
    if file_ext != '.pdf':
        return ServiceResponse(success=False, msg='Bad File Extention', status_code=409)

    # check if index entry already exists
    fs_index = await get_database().get_collection('fs_index').find_one({
        '$and': [
            {'username': username},
            {'filename': filename}
        ]
    })
    if fs_index:
        file_id = str(fs_index['_id'])
        disk_filename = f"{file_id}.pdf"
        file_type = fs_index['file_type']
        url_path = f"{FILE_TYPE_PATH_MAP[file_type]}/{disk_filename}"
        return ServiceResponse(data={
            'url_path': url_path,
            'file_id': file_id,
        })

    # create fs index entry in database
    fs_index_entry = FSIndexFile(
        username=username,
        datetime=datetime.now(),
        file_type=file_type,
        filename=filename,
        chat_doc_uuid=chat_doc_uuid,
        chat_doc_status=ChatDOCStatus.PARSING,
    )
    mdb_result = await get_database().get_collection('fs_index').insert_one(fs_index_entry.model_dump())
    file_id = str(mdb_result.inserted_id)

    # save file to disk
    disk_filename = f"{file_id}.pdf"
    file_path = os.path.join(_PUBLIC_DIR, FILE_TYPE_PATH_MAP[file_type], disk_filename)
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(data)
    url_path = f"{FILE_TYPE_PATH_MAP[file_type]}/{disk_filename}"

    return ServiceResponse(data={
        'url_path': url_path,
        'file_id': file_id,
    })


async def delete_fs_index_entry(doc_uuid: str) -> ServiceResponse:
    # fetch entry from database
    fs_index_entry = await get_database().get_collection('fs_index').find_one({'chat_doc_uuid': doc_uuid})
    if not fs_index_entry:
        return ServiceResponse(success=False, status_code=404, msg='File Index not Found')

    # delete file from disk
    file_type = fs_index_entry['file_type']
    file_id = str(fs_index_entry['_id'])
    filename = f"{file_id}.pdf"
    file_path = os.path.join(_PUBLIC_DIR, FILE_TYPE_PATH_MAP[file_type], filename)
    await aiofiles.os.remove(file_path)

    # delete file index database entry
    result = await get_database().get_collection('fs_index').delete_one({'chat_doc_uuid': doc_uuid})
    if not result.deleted_count:
        return ServiceResponse(success=False, status_code=404, msg='Error Deleting File Index Entry')

    return ServiceResponse(msg='OK')


async def get_fs_index_entry(chat_doc_uuid: str) -> ServiceResponse:
    fs_index_entry = await get_database().get_collection('fs_index').find_one({'chat_doc_uuid': chat_doc_uuid})
    if not fs_index_entry:
        return ServiceResponse(success=False, msg='File Index not Found', status_code=404)
    return ServiceResponse(data={'fs_index_entry': FSIndexFile.model_validate(fs_index_entry)})
