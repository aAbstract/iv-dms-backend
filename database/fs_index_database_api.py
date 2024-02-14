import os
import aiofiles
import aiofiles.os
from datetime import datetime
from models.fs_index import (ChatDOCStatus, FILE_TYPE_PATH_MAP, FSIndexFile, FSIndexTree,
    IndexFileType)
from models.runtime import ServiceResponse
from database.mongo_driver import get_database
from PyPDF2 import PdfReader
import re
import lib.log as log_man


_PUBLIC_DIR = 'public'


async def create_fs_index_entry(username: str, organization:str, file_type: IndexFileType, filename: str, data: bytes, chat_doc_uuid: str = '00000000-0000-0000-0000-000000000000') -> ServiceResponse:
    # check if index entry already exists
    fs_index = await get_database().get_collection('fs_index').find_one({
        '$and': [
            {'username': username},
            {'filename': filename}
        ]
    })

    file_ext = os.path.splitext(filename)[1]
    if fs_index:
        file_id = str(fs_index['_id'])
        disk_filename = f"{file_id}{file_ext}"
        file_type = fs_index['file_type']
        url_path = f"/{FILE_TYPE_PATH_MAP[file_type]}/{disk_filename}"
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
        doc_uuid=chat_doc_uuid,
        doc_status=ChatDOCStatus.PARSING if file_type == IndexFileType.AIRLINES_MANUAL else ChatDOCStatus.PARSED,
        organization=organization
    )
    mdb_result = await get_database().get_collection('fs_index').insert_one(fs_index_entry.model_dump())
    file_id = str(mdb_result.inserted_id)

    # save file to disk
    disk_filename = f"{file_id}{file_ext}"
    file_path = os.path.join(_PUBLIC_DIR, FILE_TYPE_PATH_MAP[file_type], disk_filename)
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(data)
    url_path = f"/{FILE_TYPE_PATH_MAP[file_type]}/{disk_filename}"

    return ServiceResponse(data={
        'url_path': url_path,
        'file_id': file_id,
    })


async def delete_fs_index_entry(doc_uuid: str, organization:str) -> ServiceResponse:
    # fetch entry from database
    fs_index_entry = await get_database().get_collection('fs_index').find_one({'doc_uuid': doc_uuid})
    if not fs_index_entry:
        return ServiceResponse(success=False, status_code=404, msg='File Index not Found')
    
    if fs_index_entry['organization'] != organization:
        return ServiceResponse(success=False,status_code=403,msg="Your organization can't access this file")

    # delete file from disk
    file_ext = os.path.splitext(fs_index_entry['filename'])[1]
    file_type = fs_index_entry['file_type']
    file_id = str(fs_index_entry['_id'])
    filename = f"{file_id}{file_ext}"
    file_path = os.path.join(_PUBLIC_DIR, FILE_TYPE_PATH_MAP[file_type], filename)
    await aiofiles.os.remove(file_path)

    # delete file index database entry
    result = await get_database().get_collection('fs_index').delete_one({'doc_uuid': doc_uuid})
    if not result.deleted_count:
        return ServiceResponse(success=False, status_code=404, msg='Error Deleting File Index Entry')

    return ServiceResponse(msg='OK')

async def list_fs_index(organization:str) -> ServiceResponse:
    fs_index_entries = [
            fs_index
            async for fs_index in get_database()
            .get_collection("fs_index")
            .find({"organization": organization})
        ]

    for fs_index in range(len(fs_index_entries)):
        fs_index_entries[fs_index]["_id"] = str(fs_index_entries[fs_index]["_id"])

    return ServiceResponse(data={"fs_index_entries":fs_index_entries})

async def get_fs_index_entry(chat_doc_uuid: str) -> ServiceResponse:
    fs_index_entry = await get_database().get_collection('fs_index').find_one({'doc_uuid': chat_doc_uuid})
    if not fs_index_entry:
        return ServiceResponse(success=False, msg='File Index not Found', status_code=404)
    return ServiceResponse(data={'fs_index_entry': FSIndexFile.model_validate(fs_index_entry)})

async def get_user_manuals(username: str) -> ServiceResponse:
    files = await get_database().get_collection('fs_index').find(
        {
            '$and': [
                {'username': username},
                {'file_type': IndexFileType.AIRLINES_MANUAL},
            ]
        },
        {
            '_id': 0,
            'id': {'$toString': '$_id'},
            'username': 1,
            'datetime': 1,
            'file_type': 1,
            'filename': 1,
            'doc_uuid': 1,
            'doc_status': 1,
        }).sort({'datetime': -1}).to_list(length=None)

    for file in files:
        file['url_path'] = f"/airlines_files/manuals/{file['id']}.pdf"

    return ServiceResponse(data={'files': files})

async def get_pages(organization:str,pages: str, doc_uuid: str) -> ServiceResponse:

    # fetch entry from database
    fs_index_entry = await get_database().get_collection('fs_index').find_one({'doc_uuid': doc_uuid})
    
    if not fs_index_entry:
        return ServiceResponse(success=False, status_code=404, msg='File Index not Found')

    if fs_index_entry['organization'] != organization:
        return ServiceResponse(success=False,status_code=403,msg="Your organization can't access this file")
    
    file_path = os.path.join(_PUBLIC_DIR, FILE_TYPE_PATH_MAP[IndexFileType.AIRLINES_MANUAL], str(fs_index_entry['_id'])+".pdf")

    if(not os.path.exists(file_path)):
        await log_man.add_log("get_pages", 'ERROR', f"Missing file with fs index: ChatDocID={doc_uuid},File ID= {fs_index_entry['_id']+'.pdf'}, organization={organization}")
        return ServiceResponse(success=False,status_code=400,msg="System File doesn't exist")

    all_pages = []

    reader = PdfReader(file_path)
    for i in pages:
        page = reader.pages[i-1]
        all_pages.append(page.extract_text())

    all_pages = " ".join(all_pages)

    return ServiceResponse(data={"text":all_pages})

async def get_tree_structure(text:str) -> ServiceResponse:
    # temp variables
    # temp chapter to hold current selected chapter
    lines = text.split("\n")

    temp_chapter = {"children":[]}
    # list to hold everythin
    all_chapters =[]
    # temp section to hold current selected section
    temp_section = {"children":[]}
    # temp sub sections to hold current selected sub sections
    temp_sub_section = []

    temp_chapter = {"children":[],"pages":[]}
    all_chapters =[]
    temp_section = {"children":[],"pages":[]}
    temp_sub_section = []

    for i in lines:
        # 1 char + space + 1 char
        if len(i.split())<2: 
            continue

        if i.split()[0].startswith("Chapter")  and re.compile(r"\d+").fullmatch(i.split()[-1].strip()):
            
            if(temp_chapter.get('name') != None):                        
                if(len(temp_section['pages']) > 1):
                    max_page = max(temp_section["pages"])
                    temp_chapter['pages'].append(max_page)
                temp_chapter['children'].append(dict(temp_section))

                temp_chapter = FSIndexTree.model_validate(temp_chapter).model_dump()
                all_chapters.append(dict(temp_chapter))
                temp_chapter = {"children":[],"pages":[]}


            temp_chapter['name'] = i
            temp_chapter['pages'].append(int(i.split()[-1].strip()))

        elif re.compile(r"(\d+)\.(\d+)(.?)").fullmatch(i.split()[0]) and re.compile(r"\d+").fullmatch(i.split()[-1].strip()):

            if(temp_section.get('name') != None):
                
                if(len(temp_sub_section) > 1):
                    max_page = max(temp_sub_section, key=lambda x: x.get("pages", 0)[0])
                    temp_section['pages'].append(max_page['pages'][0])

                temp_section['children'] = temp_sub_section
                temp_chapter['children'].append(dict(temp_section))
                temp_sub_section = []
                temp_section = {"children":[],"pages":[]}
            
            temp_section["name"] = " ".join(i.split()[:-2])
            temp_section['pages'].append(int(i.split()[-1].strip()))

        elif re.compile(r"(\d+)\.(\d+)\.(\d+)(.?)").fullmatch(i.split()[0]) and re.compile(r"\d+").fullmatch(i.split()[-1].strip()):

            temp_sub_section.append({"name":" ".join(i.split()[:-2]),"pages":[int(i.split()[-1].strip())]})
    

    if(temp_section.get('name') != None):
        
        if(temp_sub_section != []):
            max_page = max(temp_sub_section, key=lambda x: x.get("pages", 0)[0])
            temp_section['pages'].append(max_page['pages'][0])

        temp_section['children'] = temp_sub_section

    if(temp_chapter.get('name') != None):                        
        if(temp_section['pages'] != []):
            max_page = max(temp_section["pages"])
            temp_chapter['pages'].append(max_page)
        
        temp_chapter['children'].append(dict(temp_section))

        temp_chapter = FSIndexTree.model_validate(temp_chapter).model_dump()
        all_chapters.append(dict(temp_chapter))
        
    return ServiceResponse(data={'tree': all_chapters})