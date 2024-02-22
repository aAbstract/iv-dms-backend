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
from database.mongo_driver import get_database
from PyPDF2 import PdfReader
import re
import lib.log as log_man


_PUBLIC_DIR = "public"


async def create_fs_index_entry(
    username: str,
    organization: str,
    file_type: IndexFileType,
    filename: str,
    data: bytes,
    chat_doc_uuid: str = "00000000-0000-0000-0000-000000000000",
) -> ServiceResponse:
    # check if index entry already exists

    fs_index = (
        await get_database()
        .get_collection("fs_index")
        .find_one({"$and": [{"username": username}, {"filename": filename}]})
    )

    file_ext = os.path.splitext(filename)[1]
    if fs_index:
        file_id = str(fs_index["_id"])
        disk_filename = f"{file_id}{file_ext}"
        file_type = fs_index["file_type"]
        url_path = f"/{FILE_TYPE_PATH_MAP[file_type]}/{disk_filename}"
        return ServiceResponse(
            data={
                "url_path": url_path,
                "file_id": file_id,
            }
        )

    # create fs index entry in database
    fs_index_entry = FSIndexFile(
        username=username,
        datetime=datetime.now(),
        file_type=file_type,
        filename=filename,
        doc_uuid=chat_doc_uuid,
        doc_status=(
            ChatDOCStatus.PARSING
            if file_type == IndexFileType.AIRLINES_MANUAL
            else ChatDOCStatus.PARSED
        ),
        organization=organization,
    )
    mdb_result = (
        await get_database()
        .get_collection("fs_index")
        .insert_one(fs_index_entry.model_dump())
    )
    file_id = str(mdb_result.inserted_id)

    # save file to disk
    disk_filename = f"{file_id}{file_ext}"
    file_path = os.path.join(_PUBLIC_DIR, FILE_TYPE_PATH_MAP[file_type], disk_filename)
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(data)
    url_path = f"/{FILE_TYPE_PATH_MAP[file_type]}/{disk_filename}"

    return ServiceResponse(
        data={
            "url_path": url_path,
            "file_id": file_id,
        }
    )


async def delete_fs_index_entry(doc_uuid: str, organization: str) -> ServiceResponse:
    # fetch entry from database
    fs_index_entry = (
        await get_database().get_collection("fs_index").find_one({"doc_uuid": doc_uuid})
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
    file_path = os.path.join(_PUBLIC_DIR, FILE_TYPE_PATH_MAP[file_type], filename)
    await aiofiles.os.remove(file_path)

    # delete file index database entry
    result = (
        await get_database()
        .get_collection("fs_index")
        .delete_one({"doc_uuid": doc_uuid})
    )
    if not result.deleted_count:
        return ServiceResponse(
            success=False, status_code=404, msg="Error Deleting File Index Entry"
        )

    return ServiceResponse(msg="OK")


async def rename_fs_index_entry(
    doc_uuid: str, organization: str, new_name: str
) -> ServiceResponse:
    # fetch entry from database
    fs_index_entry = (
        await get_database().get_collection("fs_index").find_one({"doc_uuid": doc_uuid})
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

    if not new_name:
        return ServiceResponse(
            success=False,
            status_code=400,
            msg="You can't rename the file to and empty name",
        )

    # rename fs index filename attribute
    result = (
        await get_database()
        .get_collection("fs_index")
        .update_one({"doc_uuid": doc_uuid}, {"$set": {"filename": new_name}})
    )

    if not result.acknowledged:
        return ServiceResponse(
            success=False, status_code=404, msg="Error renaming File Index Entry"
        )

    return ServiceResponse(msg="OK")


async def list_fs_index(organization: str) -> ServiceResponse:
    fs_index_entries = [
        fs_index
        async for fs_index in get_database()
        .get_collection("fs_index")
        .find(
            {"$and": [{"organization": organization}, {"file_type": "AIRLINES_MANUAL"}]}
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

    return ServiceResponse(data={"fs_index_entries": filtred})


async def get_fs_index_entry(chat_doc_uuid: str) -> ServiceResponse:
    fs_index_entry = (
        await get_database()
        .get_collection("fs_index")
        .find_one({"doc_uuid": chat_doc_uuid})
    )
    if not fs_index_entry:
        return ServiceResponse(
            success=False, msg="File Index not Found", status_code=404
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


async def get_pages(organization: str, pages: list[tuple[str, int]]) -> ServiceResponse:
    # fetch entry from database
    fs_indices = (
        await get_database()
        .get_collection("fs_index")
        .find(
            {
                "organization": organization,
                "doc_uuid": {"$in": [x[0] for x in pages]},
            },
            {
                "_id": 1,
                "doc_uuid": 1,
            },
        )
        .to_list(length=None)
    )
    if not fs_indices:
        return ServiceResponse(
            success=False, status_code=404, msg="File Index not Found"
        )
    temp_index = {
        x["doc_uuid"]: PdfReader(
            os.path.join(
                _PUBLIC_DIR,
                FILE_TYPE_PATH_MAP[IndexFileType.AIRLINES_MANUAL],
                str(x["_id"]) + ".pdf",
            )
        )
        for x in fs_indices
    }

    all_pages_text = ""
    for doc_uuid, page_number in pages:
        pdf_reader = temp_index[doc_uuid]
        all_pages_text += pdf_reader.pages[page_number - 1].extract_text()

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

                temp_chapter = FSIndexTree.model_validate(temp_chapter).model_dump()
                all_chapters.append(dict(temp_chapter))
                temp_chapter = {"children": [], "pages": []}

            temp_chapter["name"] = i
            temp_chapter["pages"].append(int(i.split()[-1].strip()))

        elif re.compile(r"(\d+)\.(\d+)(.?)").fullmatch(i.split()[0]) and re.compile(
            r"\d+"
        ).fullmatch(i.split()[-1].strip()):

            if temp_section.get("name") != None:

                if len(temp_sub_section) > 1:
                    max_page = max(temp_sub_section, key=lambda x: x.get("pages", 0)[0])
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
            max_page = max(temp_sub_section, key=lambda x: x.get("pages", 0)[0])
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


async def get_all_tree_db(organization: str) -> ServiceResponse:
    fs_index_entries = [
        fs_index
        async for fs_index in get_database()
        .get_collection("fs_index")
        .find(
            {
                "$and": [
                    {"organization": organization},
                    {"file_type": "AIRLINES_MANUAL"},
                ]
            },
            projection={
                "_id": 0,
                "doc_uuid": 1,
                "label": "$filename",
                "parent": 1,
                "children": "$args",
            },
        )
    ]

    uuids_set = set()
    filtered = []

    # filteration
    for x in fs_index_entries:
        doc_uuid = x["doc_uuid"]
        if (doc_uuid not in uuids_set) and (x["children"].get("toc_info") != None):

            if len(x["children"]["toc_info"]) < 1:
                continue

            x["children"] = x["children"]["toc_info"]

            if any([obj["label"] == x["parent"] for obj in filtered]):

                new_min = min(
                    [obj for obj in filtered if obj["label"] == x["parent"]][0][
                        "pages"
                    ][0],
                    x["children"][0]["pages"][0],
                )
                new_max = max(
                    [obj for obj in filtered if obj["label"] == x["parent"]][0][
                        "pages"
                    ][-1],
                    x["children"][-1]["pages"][-1],
                )

                [obj for obj in filtered if obj["label"] == x["parent"]][0]["pages"] = [
                    new_min,
                    new_max,
                ]

                [obj for obj in filtered if obj["label"] == x["parent"]][0][
                    "children"
                ].append(
                    {
                        "doc_uuid": x["doc_uuid"],
                        "label": x["label"],
                        "key": x["parent"].split(".pdf")[0]
                        + "."
                        + x["label"].split(".")[0],
                        "children": x["children"],
                    }
                )

            else:

                filtered.append(
                    {
                        "label": x["parent"],
                        "pages": [
                            x["children"][0]["pages"][0],
                            x["children"][-1]["pages"][-1],
                        ],
                        "key": x["parent"].split(".pdf")[0],
                        "children": [
                            {
                                "doc_uuid": x["doc_uuid"],
                                "label": x["label"].split(".pdf")[0],
                                "key": x["parent"].split(".pdf")[0]
                                + "."
                                + x["label"].split(".pdf")[0],
                                "children": x["children"],
                            }
                        ],
                    }
                )

            uuids_set.add(doc_uuid)
            # FSIndexTree.model_validate(x)
            # filtered.append(x)

    return ServiceResponse(data={"checkins": filtered})
