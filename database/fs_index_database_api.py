import os
import aiofiles
import aiofiles.os
from datetime import datetime
from models.fs_index import FSIndexFile, IndexFileType, FILE_TYPE_PATH_MAP
from models.runtime import ServiceResponse
from database.mongo_driver import get_database, validate_bson_id


_PUBLIC_DIR = 'public'


async def create_fs_index_entry(username: str, file_type: IndexFileType, filename: str, data: bytes) -> ServiceResponse:
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
        return ServiceResponse(success=False, msg='File Index Already Exists', status_code=409)

    # create fs index entry in database
    fs_index_entry = FSIndexFile(
        username=username,
        datetime=datetime.now(),
        file_type=file_type,
        filename=filename
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


async def delete_fs_index_entry(file_id: str) -> ServiceResponse:
    bson_id = validate_bson_id(file_id)
    if not bson_id:
        return ServiceResponse(success=False, msg='Bad File ID', status_code=400)

    # fetch entry from database
    fs_index_entry = await get_database().get_collection('fs_index').find_one({'_id': bson_id})
    if not fs_index_entry:
        return ServiceResponse(success=False, status_code=404, msg='File Index not Found')

    # delete file from disk
    file_type = fs_index_entry['file_type']
    filename = f"{file_id}.pdf"
    file_path = os.path.join(_PUBLIC_DIR, FILE_TYPE_PATH_MAP[file_type], filename)
    await aiofiles.os.remove(file_path)

    # delete file index database entry
    result = await get_database().get_collection('fs_index').delete_one({'_id': bson_id})
    if not result.deleted_count:
        return ServiceResponse(success=False, status_code=404, msg='Error Deleting File Index Entry')

    return ServiceResponse(msg='OK')
