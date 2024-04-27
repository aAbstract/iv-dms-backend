from bson import ObjectId
import json
import os
import aiofiles
import aiofiles.os
from datetime import datetime
from models.fs_index import (
    ChatDOCStatus,
    FILE_TYPE_PATH_MAP,
    FSIndexFile,
    FSIndexTree,
    IndexFileType,
)
from models.runtime import ServiceResponse
from database.mongo_driver import get_database, validate_bson_id
from PyPDF2 import PdfReader
import re
import lib.log as log_man
from lib.pdf import create_parts_metadata_file
from models.flow_reports import Airline
from lib.z_pdf_tree_parser import ZPDF
from uuid import uuid4
from models.users import UserRole

_PUBLIC_DIR = r"public"
_CACHE_FOLDER = r"data/cache/toc_trees"
WATER_MARKS = ["UNCONTROLLED IF PRINTED", "DRAFT"]


async def create_fs_index_entry(
    username: str,
    organization: str,
    airline_id: str,
    file_type: IndexFileType,
    filename: str,
    data: bytes,
) -> ServiceResponse:

    # check if index entry already exists
    fs_index = (
        await get_database()
        .get_collection("fs_index")
        .find_one({"$and": [{"username": username}, {"filename": filename}]})
    )
    file_ext = os.path.splitext(filename)[1]

    # validate airline
    if not airline_id:
        return ServiceResponse(
            success=False, msg="Airline ID can't be empty text", status_code=400
        )

    airline_bson_id = validate_bson_id(airline_id)
    if not airline_bson_id:
        return ServiceResponse(
            success=False, msg="Bad Airline ID", status_code=400
        )

    # get airline
    airline = (
        await get_database()
        .get_collection("airlines")
        .find_one({"_id": airline_bson_id})
    )

    if not airline:
        return ServiceResponse(
            success=False, msg="This airline ID doesn't exist", status_code=404
        )

    if airline["organization"] != organization:
        return ServiceResponse(
            success=False,
            msg="Your organization can't access this airline",
            status_code=403,
        )

    # over write if already existing
    if fs_index:

        fs_index['airline'] = airline_id
        fs_index['datetime'] = datetime.now()
        fs_index['doc_status'] = ChatDOCStatus.PARSING_FAILD
        fs_index['args'] = {}
        FSIndexFile.model_validate(fs_index)

        mdb_result = (
            await get_database()
            .get_collection("fs_index")
            .replace_one({"_id": fs_index['_id']}, fs_index)
        )

        file_id = str(fs_index['_id'])
        chat_doc_uuid = str(fs_index['doc_uuid'])

    else:

        chat_doc_uuid = str(uuid4())

        # create fs index entry in database
        fs_index_entry = FSIndexFile(
            username=username,
            datetime=datetime.now(),
            file_type=file_type,
            filename=filename,
            doc_uuid=chat_doc_uuid,
            doc_status=ChatDOCStatus.PARSING_FAILD,
            organization=organization,
            airline=airline_id,
        )

        mdb_result = (
            await get_database()
            .get_collection("fs_index")
            .insert_one(fs_index_entry.model_dump())
        )

        file_id = str(mdb_result.inserted_id)

    # save file to disk
    disk_filename = f"{file_id}{file_ext}"
    file_path = os.path.join(
        _PUBLIC_DIR, FILE_TYPE_PATH_MAP[file_type], disk_filename
    ).replace("\\", "/")
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(data)
    url_path = rf"/{FILE_TYPE_PATH_MAP[file_type]}/{disk_filename}".replace(
        "\\", "/")

    # if file is attachemnt, don't create a ZTree
    if file_type == IndexFileType.AIRLINES_ATTACHMENT:

        metrics = {"toc_headers_count": 0, "coverage_metric": 0.0}

        return ServiceResponse(
            data={
                "url_path": url_path,
                "file_id": file_id,
                "doc_uuid": chat_doc_uuid,
                "doc_status": ChatDOCStatus.PARSING_FAILD,
                "parsing_metrics": metrics,
            }
        )

    try:

        z_tree = ZPDF(file_path=file_path)
        z_tree.save_cache(chat_doc_uuid)

        metrics = z_tree.get_benchmark()
        status = ChatDOCStatus.PARSED

        metadata = {
            "toc_info": z_tree.get_cache_transformed(),
            "parsing_metrics": metrics,
        }

        await get_database().get_collection("fs_index").update_one(
            {"_id": ObjectId(file_id)},
            {"$set": {"args": metadata, "doc_status": status}},
        )

    except:
        status = ChatDOCStatus.PARSING_FAILD
        metrics = {"toc_headers_count": 0, "coverage_metric": 0.0}

        await get_database().get_collection("fs_index").update_one(
            {"_id": ObjectId(file_id)}, {"$set": {"doc_status": status}}
        )

    return ServiceResponse(
        data={
            "url_path": url_path,
            "file_id": file_id,
            "doc_uuid": chat_doc_uuid,
            "doc_status": status,
            "parsing_metrics": metrics,
        }
    )


async def delete_fs_index_entry(fs_index: str, organization: str) -> ServiceResponse:

    bson_id = validate_bson_id(fs_index)
    if not bson_id:
        return ServiceResponse(success=False, msg="Bad flow report ID", status_code=400)

    # fetch entry from database
    fs_index_entry = (
        await get_database().get_collection("fs_index").find_one({"_id": bson_id})
    )
    if not fs_index_entry:
        return ServiceResponse(
            success=False, status_code=404, msg="File Index not Found"
        )

    if fs_index_entry["organization"] != organization:
        return ServiceResponse(
            success=False,
            status_code=403,
            msg="Your organization can't access this file",
        )

    # delete file from disk
    file_ext = os.path.splitext(fs_index_entry["filename"])[1]
    file_type = fs_index_entry["file_type"]
    file_id = str(fs_index_entry["_id"])
    filename = f"{file_id}{file_ext}"
    file_path = os.path.join(
        _PUBLIC_DIR, FILE_TYPE_PATH_MAP[file_type], filename)
    await aiofiles.os.remove(file_path)

    # delete file index database entry
    result = (
        await get_database().get_collection("fs_index").delete_one({"_id": bson_id})
    )
    if not result.deleted_count:
        return ServiceResponse(
            success=False, status_code=404, msg="Error Deleting File Index Entry"
        )

    return ServiceResponse(msg="OK")


async def rename_fs_index_entry(
    fs_index: str, organization: str, file_name: str
) -> ServiceResponse:
    bson_id = validate_bson_id(fs_index)
    if not bson_id:
        return ServiceResponse(success=False, msg="Bad flow report ID", status_code=400)

    # fetch entry from database
    fs_index_entry = (
        await get_database().get_collection("fs_index").find_one({"_id": bson_id})
    )
    if not fs_index_entry:
        return ServiceResponse(
            success=False, status_code=404, msg="File Index not Found"
        )

    if fs_index_entry["organization"] != organization:
        return ServiceResponse(
            success=False,
            status_code=403,
            msg="Your organization can't access this file",
        )

    if not file_name:
        return ServiceResponse(
            success=False,
            status_code=400,
            msg="You can't rename the file to an empty name",
        )

    # rename fs index filename attribute
    result = (
        await get_database()
        .get_collection("fs_index")
        .update_one({"_id": bson_id}, {"$set": {"filename": file_name}})
    )

    if not result.acknowledged:
        return ServiceResponse(
            success=False, status_code=404, msg="Error renaming File Index Entry"
        )

    return ServiceResponse(msg="OK")


async def list_fs_index(organization: str, username: str) -> ServiceResponse:

    # Construct Query
    query = [{"organization": organization}, {"file_type": "AIRLINES_MANUAL"}]

    if username:
        user = await get_database().get_collection("users").find_one({"username": username})

        if not user:
            return ServiceResponse(success=False, msg="This Username Doesn't exist", status_code=404)

        if user['user_role'] == UserRole.AIRLINES:
            query.append({'airline': user['airline']})

    fs_index_entries = [
        fs_index
        async for fs_index in get_database()
        .get_collection("fs_index")
        .find(
            {
                "$and": query
            },
            {"args": 0},
        )
    ]

    # TODO-GALAL: optimize this on database level
    # filter unique doc_uuids
    uuids_set = set()
    filtred = []
    for x in fs_index_entries:
        doc_uuid = x["doc_uuid"]
        if doc_uuid not in uuids_set:
            uuids_set.add(doc_uuid)
            filtred.append(x)

    for fs_index in range(len(filtred)):
        filtred[fs_index]["_id"] = str(filtred[fs_index]["_id"])
        filtred[fs_index][
            "url_path"
        ] = f"/airlines_files/manuals/{filtred[fs_index]['_id']}.pdf"
        if filtred[fs_index].get("airline"):
            airline = (
                await get_database()
                .get_collection("airlines")
                .find_one({"_id": ObjectId(filtred[fs_index]["airline"])})
            )

            if not airline:
                return ServiceResponse(
                    success=False,
                    msg="Airline id couldn't be found",
                    status_code=400,
                )
            if airline["organization"] != organization:
                return ServiceResponse(
                    success=False,
                    msg="Your organization can't access this airline",
                    status_code=400,
                )
            airline["id"] = str(airline["_id"])
            del airline["_id"]
            filtred[fs_index]["airline"] = airline
        else:
            filtred[fs_index]["airline"] = "No Airline Assigned"
    return ServiceResponse(data={"fs_index_entries": filtred})


async def get_fs_index_entry(chat_doc_uuid: str, organization: str) -> ServiceResponse:
    fs_index_entry = (
        await get_database()
        .get_collection("fs_index")
        .find_one({"doc_uuid": chat_doc_uuid})
    )
    if not fs_index_entry:
        return ServiceResponse(
            success=False, msg="File Index not Found", status_code=404
        )

    if fs_index_entry["organization"] != organization:
        return ServiceResponse(
            success=False,
            status_code=403,
            msg="Your organization can't access this file",
        )

    return ServiceResponse(
        data={"fs_index_entry": FSIndexFile.model_validate(fs_index_entry)}
    )


async def get_user_manuals(username: str) -> ServiceResponse:
    files = (
        await get_database()
        .get_collection("fs_index")
        .find(
            {
                "$and": [
                    {"username": username},
                    {"file_type": IndexFileType.AIRLINES_MANUAL},
                ]
            },
            {
                "_id": 0,
                "id": {"$toString": "$_id"},
                "username": 1,
                "datetime": 1,
                "file_type": 1,
                "filename": 1,
                "doc_uuid": 1,
                "doc_status": 1,
            },
        )
        .sort({"datetime": -1})
        .to_list(length=None)
    )

    for file in files:
        file["url_path"] = f"/airlines_files/manuals/{file['id']}.pdf"

    return ServiceResponse(data={"files": files})


async def get_pages_from_sections(
    organization: str, pages_mapper: dict[str, list[str]]
) -> ServiceResponse:

    # fetch entry from database
    fs_indices = (
        await get_database()
        .get_collection("fs_index")
        .find(
            {
                "organization": organization,
                "doc_uuid": {"$in": [x for x in pages_mapper.keys()]},
            },
            {"_id": 1, "doc_uuid": 1, "file_type": 1},
        )
        .to_list(length=None)
    )

    if not fs_indices:
        return ServiceResponse(success=False, status_code=404, msg="FS Index not Found")

    # Get all the text
    all_pages_text = ""
    for fs_index in fs_indices:
        try:
            fs_index_id = str(fs_index["_id"])
            file_type = fs_index["file_type"]
            doc_uuid = fs_index["doc_uuid"]

            file_path = os.path.join(
                _PUBLIC_DIR, FILE_TYPE_PATH_MAP[file_type], fs_index_id + ".pdf"
            ).replace("\\", "/")
            cache_path = os.path.join(_CACHE_FOLDER, rf"{doc_uuid}.json").replace(
                "\\", "/"
            )

            # Check if Cache exists
            if os.path.exists(cache_path):
                # Retrive Cache and instantiate ZTree
                with open(cache_path, "r") as f:
                    cache = json.loads(f.read())
                    z_pdf_tree = ZPDF(file_path=file_path, cache=cache)

            else:
                z_pdf_tree = ZPDF(file_path=file_path)
                z_pdf_tree.save_cache(doc_uuid)

            for text in z_pdf_tree.extract_text(list(set(pages_mapper[doc_uuid]))):
                all_pages_text += "\n" + text.strip() + "\n"
        except:
            pass

    if not all_pages_text:
        return ServiceResponse(
            success=False, status_code=404, msg="No Text Was Selected"
        )

    for water_mark in WATER_MARKS:
        all_pages_text = all_pages_text.replace(water_mark, " ")

    return ServiceResponse(data={"text": all_pages_text})


async def get_pages(organization: str, pages: dict[str, set[int]]) -> ServiceResponse:
    # fetch entry from database
    fs_indices = (
        await get_database()
        .get_collection("fs_index")
        .find(
            {
                "organization": organization,
                "doc_uuid": {"$in": [x for x in pages.keys()]},
            },
            {
                "_id": 1,
                "doc_uuid": 1,
            },
        )
        .to_list(length=None)
    )
    if not fs_indices:
        return ServiceResponse(success=False, status_code=404, msg="FS Index not Found")

    all_pages_text = ""

    for fs_index in fs_indices:
        pdf_reader = PdfReader(
            os.path.join(
                _PUBLIC_DIR,
                FILE_TYPE_PATH_MAP[IndexFileType.AIRLINES_MANUAL],
                str(fs_index["_id"]) + ".pdf",
            )
        )

        # iterate over each page and extract the text
        for page in pages[fs_index["doc_uuid"]]:
            if page > len(pdf_reader.pages) or page <= 0:
                return ServiceResponse(
                    success=False,
                    status_code=404,
                    msg=f"Page Number is our of range for Document {fs_index['doc_uuid']} page {page}",
                )
            all_pages_text += pdf_reader.pages[page - 1].extract_text()
    all_pages_text = all_pages_text.replace("UNCONTROLLED IF PRINTED", " ")
    return ServiceResponse(data={"text": all_pages_text})


async def get_tree_structure(text: str) -> ServiceResponse:
    # temp variables
    # temp chapter to hold current selected chapter
    lines = text.split("\n")

    temp_chapter = {"children": []}
    # list to hold everythin
    all_chapters = []
    # temp section to hold current selected section
    temp_section = {"children": []}
    # temp sub sections to hold current selected sub sections
    temp_sub_section = []

    temp_chapter = {"children": [], "pages": []}
    all_chapters = []
    temp_section = {"children": [], "pages": []}
    temp_sub_section = []

    for i in lines:
        # 1 char + space + 1 char
        if len(i.split()) < 2:
            continue

        if i.split()[0].startswith("Chapter") and re.compile(r"\d+").fullmatch(
            i.split()[-1].strip()
        ):

            if temp_chapter.get("name") != None:
                if len(temp_section["pages"]) > 1:
                    max_page = max(temp_section["pages"])
                    temp_chapter["pages"].append(max_page)
                temp_chapter["children"].append(dict(temp_section))

                temp_chapter = FSIndexTree.model_validate(
                    temp_chapter).model_dump()
                all_chapters.append(dict(temp_chapter))
                temp_chapter = {"children": [], "pages": []}

            temp_chapter["name"] = i
            temp_chapter["pages"].append(int(i.split()[-1].strip()))

        elif re.compile(r"(\d+)\.(\d+)(.?)").fullmatch(i.split()[0]) and re.compile(
            r"\d+"
        ).fullmatch(i.split()[-1].strip()):

            if temp_section.get("name") != None:

                if len(temp_sub_section) > 1:
                    max_page = max(temp_sub_section,
                                   key=lambda x: x.get("pages", 0)[0])
                    temp_section["pages"].append(max_page["pages"][0])

                temp_section["children"] = temp_sub_section
                temp_chapter["children"].append(dict(temp_section))
                temp_sub_section = []
                temp_section = {"children": [], "pages": []}

            temp_section["name"] = " ".join(i.split()[:-2])
            temp_section["pages"].append(int(i.split()[-1].strip()))

        elif re.compile(r"(\d+)\.(\d+)\.(\d+)(.?)").fullmatch(
            i.split()[0]
        ) and re.compile(r"\d+").fullmatch(i.split()[-1].strip()):

            temp_sub_section.append(
                {
                    "name": " ".join(i.split()[:-2]),
                    "pages": [int(i.split()[-1].strip())],
                }
            )

    if temp_section.get("name") != None:

        if temp_sub_section != []:
            max_page = max(temp_sub_section,
                           key=lambda x: x.get("pages", 0)[0])
            temp_section["pages"].append(max_page["pages"][0])

        temp_section["children"] = temp_sub_section

    if temp_chapter.get("name") != None:
        if temp_section["pages"] != []:
            max_page = max(temp_section["pages"])
            temp_chapter["pages"].append(max_page)

        temp_chapter["children"].append(dict(temp_section))

        temp_chapter = FSIndexTree.model_validate(temp_chapter).model_dump()
        all_chapters.append(dict(temp_chapter))

    return ServiceResponse(data={"tree": all_chapters})


async def get_all_tree_db(organization: str, airline_id: str | None, username: str) -> ServiceResponse:
    query = {
        "$and": [
            {"organization": organization},
            {"file_type": "AIRLINES_MANUAL"},
        ]
    }

    # validate airline
    if username:
        user = await get_database().get_collection("users").find_one({"username": username})

        if not user:
            return ServiceResponse(success=False, msg="This Username Doesn't exist", status_code=404)

        # is the user an airline user
        if user['user_role'] == UserRole.AIRLINES:
            query["$and"].append({"airline": str(user['airline'])})
            
        # This is a normal user
        else:

            if airline_id:
                # validate airline
                airline_id = validate_bson_id(airline_id)
                if not airline_id:
                    return ServiceResponse(success=False, msg="Bad Airline ID", status_code=400)

                # get airline
                airline = (
                    await get_database()
                    .get_collection("airlines")
                    .find_one({"_id": airline_id})
                )

                if not airline:
                    return ServiceResponse(
                        success=False, msg="This airline ID doesn't exist", status_code=404
                    )

                if airline["organization"] != organization:
                    return ServiceResponse(
                        success=False,
                        msg="Your organization can't access this airline",
                        status_code=403,
                    )

                query["$and"].append({"airline": str(airline_id)})

    fs_index_entries = [
        fs_index
        async for fs_index in get_database()
        .get_collection("fs_index")
        .find(
            query,
            projection={
                "_id": 0,
                "doc_uuid": 1,
                "doc_status": 1,
                "label": "$filename",
                "children": "$args",
                "airline": "$airline",
            },
        )
    ]

    # TODO-GALAL DO assign the doc_uuid to the children of a chapter in the scripts instead of here
    def populate_docuuid(uuid, children_list):
        for child in children_list:
            child["doc_uuid"] = uuid
            if child.get("children") != None:
                for sub1_child in child["children"]:
                    sub1_child["doc_uuid"] = uuid
                    if sub1_child.get("children") != None:
                        for sub2_child in sub1_child["children"]:
                            sub2_child["doc_uuid"] = uuid
                            if sub2_child.get("children") != None:
                                for sub3_child in sub2_child["children"]:
                                    sub3_child["doc_uuid"] = uuid
                                    if sub3_child.get("children") != None:
                                        for sub4_child in sub3_child["children"]:
                                            sub4_child["doc_uuid"] = uuid
                                            if sub4_child.get("children") != None:
                                                # TODO: This might never happen so check the manuals
                                                # if there is a nested five level section
                                                for sub5_child in sub4_child[
                                                    "children"
                                                ]:
                                                    sub5_child["doc_uuid"] = uuid

    uuids_set = set()
    filtered = []

    # filteration
    for x in fs_index_entries:
        doc_uuid = x["doc_uuid"]
        if (doc_uuid not in uuids_set) and (x["doc_status"] == ChatDOCStatus.PARSED):

            if len(x["children"]["toc_info"]) < 1:
                continue

            x["children"] = x["children"]["toc_info"]

            if any([obj["label"] == x["label"] for obj in filtered]):

                populate_docuuid(doc_uuid, x["children"])

                [obj for obj in filtered if obj["label"] == x["label"]][0][
                    "children"
                ].append(x["children"])

            else:
                populate_docuuid(doc_uuid, x["children"])

                # validate airline
                airline_id = validate_bson_id(x["airline"])
                if not airline_id:
                    return ServiceResponse(
                        success=False, msg="Bad Airline ID", status_code=400
                    )

                # get airline
                airline = (
                    await get_database()
                    .get_collection("airlines")
                    .find_one({"_id": airline_id})
                )

                if not airline:
                    return ServiceResponse(
                        success=False,
                        msg="This airline ID doesn't exist",
                        status_code=404,
                    )

                filtered.append(
                    {
                        "label": x["label"],
                        "key": x["label"].split(".pdf")[0],
                        "airline_id": x["airline"],
                        "airline": airline["name"],
                        "children": x["children"],
                    }
                )

            uuids_set.add(doc_uuid)
            # FSIndexTree.model_validate(x)
            # filtered.append(x)

    return ServiceResponse(data={"checkins": filtered})


async def get_keys_from_toc_tree(
    doc_uuid: str, pages: list[int], organization: str
) -> ServiceResponse:

    fs_index = (
        await get_database().get_collection("fs_index").find_one({"doc_uuid": doc_uuid})
    )
    if not fs_index:
        return ServiceResponse(
            success=False, msg="File Index not Found", status_code=404
        )

    if fs_index["organization"] != organization:
        return ServiceResponse(
            success=False,
            status_code=403,
            msg="Your organization can't access this file",
        )

    if fs_index["args"].get("toc_info") == None:
        return ServiceResponse(
            success=False,
            status_code=400,
            msg=f"Document with doc_uuid {doc_uuid} does not have a toc tree",
        )

    manual_refrences = {}

    def check_if_contains_page(db_page_list):
        if len(db_page_list) == 1:
            for page in pages:
                if page == db_page_list[0]:
                    return True
            return False
        elif len(db_page_list) == 2:
            for page in pages:
                if page >= min(db_page_list) and page <= max(db_page_list):
                    return True
            return False
        else:
            return False

    def add_key(key, value, label):
        manual_refrences[key] = {
            "pages": value,
            "label": label,
            "doc_uuid": doc_uuid,
        }

    for child in fs_index["args"]["toc_info"]:
        if child.get("children") != []:
            for sub1_child in child["children"]:
                if sub1_child.get("children") != []:
                    for sub2_child in sub1_child["children"]:
                        if sub2_child.get("children") != []:
                            for sub3_child in sub2_child["children"]:
                                if sub3_child.get("children") != []:
                                    for sub4_child in sub3_child["children"]:
                                        if sub4_child.get("children") != []:
                                            for sub5_child in sub4_child["children"]:
                                                if sub5_child.get("children") != []:
                                                    for sub6_child in sub5_child[
                                                        "children"
                                                    ]:
                                                        if check_if_contains_page(
                                                            sub6_child["pages"]
                                                        ):
                                                            add_key(
                                                                sub6_child["key"],
                                                                sub6_child["pages"],
                                                                sub6_child["label"],
                                                            )
                                                else:
                                                    if check_if_contains_page(
                                                        sub5_child["pages"]
                                                    ):

                                                        add_key(
                                                            sub5_child["key"],
                                                            sub5_child["pages"],
                                                            sub5_child["label"],
                                                        )
                                        else:
                                            if check_if_contains_page(
                                                sub4_child["pages"]
                                            ):

                                                add_key(
                                                    sub4_child["key"],
                                                    sub4_child["pages"],
                                                    sub4_child["label"],
                                                )
                                else:
                                    if check_if_contains_page(sub3_child["pages"]):

                                        add_key(
                                            sub3_child["key"],
                                            sub3_child["pages"],
                                            sub3_child["label"],
                                        )

                        else:
                            if check_if_contains_page(sub2_child["pages"]):

                                add_key(
                                    sub2_child["key"],
                                    sub2_child["pages"],
                                    sub2_child["label"],
                                )
                else:
                    if check_if_contains_page(sub1_child["pages"]):

                        add_key(
                            sub1_child["key"], sub1_child["pages"], sub1_child["label"]
                        )
        else:
            if check_if_contains_page(child["pages"]):

                add_key(
                    child["key"],
                    child["pages"],
                    child["label"],
                )

    if manual_refrences == {}:
        return ServiceResponse(
            success=False,
            status_code=400,
            msg=f"Pages {' '.join(pages)} were not found in {doc_uuid}",
        )

    return ServiceResponse(data=manual_refrences)
