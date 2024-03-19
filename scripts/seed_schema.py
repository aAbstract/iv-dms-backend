# autopep8: off
import json
import os
import sys
import pymongo
import shutil
from glob import glob
from uuid import uuid4
from dotenv import load_dotenv
import code
import json
import re
from parse_manual_RXI import create_parts_metadata_file as RXI_parser
from parse_manual_nesma import create_parts_metadata_file as nesma_parser
from subprocess import run


def load_root_path():
    file_dir = os.path.abspath(__file__)
    lv1_dir = os.path.dirname(file_dir)
    root_dir = os.path.dirname(lv1_dir)
    sys.path.append(root_dir)


load_root_path()
load_dotenv()
from models.users import *
from models.regulations import *
from models.manuals import *
from models.logs import *
from models.fs_index import *
from models.ai_tasks import *
from models.gpt_35t import *
from models.flow_reports import *

# autopep8: on

# seed manual files
# change these to python instead of python3 when using in your machine
# set back to pyhton3 for the linux dev server
commands = [
    "rm public/airlines_files/manuals/*.pdf",
    "python3 scripts/parse_iosa_section.py",
    "python3 scripts/parse_gacar.py",
]
# commands = [
#     "python scripts/parse_iosa_section.py",
#     "python scripts/parse_gacar.py",
# ]

for command in commands:
    os.system(command)

# main
client = pymongo.MongoClient(
    f"mongodb://{os.environ['MDB_USERNAME']}:{os.environ['MDB_PASSWORD']}@127.0.0.1"
)
client.drop_database(os.environ["IVDMS_DB"])

db = client.get_database(os.environ["IVDMS_DB"])

# users schema
seed_users = [
    User(
        username="cwael",
        disp_name="Captin Wael",
        pass_hash="86d74596bb4c2f6b63ae7c09c212a7ed824ab15371ec06a2126dffc3aaa191659478e432c458d5b6a7c0b21b5bf2120c91480c27e78cf94935135d8c022f42f7",
        user_role=UserRole.AUDITOR,
        phone_number="+201001000000",
        email="cwael@aerosync.com",
        organization="AeroSync",
    ),
    User(
        username="eslam",
        disp_name="Eslam Admin",
        pass_hash="86d74596bb4c2f6b63ae7c09c212a7ed824ab15371ec06a2126dffc3aaa191659478e432c458d5b6a7c0b21b5bf2120c91480c27e78cf94935135d8c022f42f7",
        user_role=UserRole.ADMIN,
        phone_number="+201001000000",
        email="eslam@aerosync.com",
        organization="AeroSync",
    ),
    User(
        username="safwat",
        disp_name="Safwat Admin",
        pass_hash="bee066ca744aa10dffa39924161a190c5193988779b7ec58694b2bc15e104c998164bf04500c8523005f36ea4fc660f8cb8cf476eea14285a8079f2a530fbb9f",
        user_role=UserRole.ADMIN,
        phone_number="+201001000000",
        email="safwat@aerosync.com",
        organization="AeroSync",
    ),
    User(
        username="aelhennawy",
        disp_name="Amr Elhennawy",
        pass_hash="6204c03169cb87f6834c1dd0419e0a06d1dfca3b0df37fef6b7f2bf5baa016b03463c3906c8669e797ba49c67b3f9950dfc7248ce278f922fc0592e7044a3d32",
        user_role=UserRole.AUDITOR,
        phone_number="+201001000000",
        email="aelhennawy@aerosync.com",
        organization="AeroSync",
    ),
    User(
        username="sam",
        disp_name="Sam Jackson",
        pass_hash="86d74596bb4c2f6b63ae7c09c212a7ed824ab15371ec06a2126dffc3aaa191659478e432c458d5b6a7c0b21b5bf2120c91480c27e78cf94935135d8c022f42f7",
        user_role=UserRole.AIRLINES,
        phone_number="+201193458172",
        email="sam@aerosync.com",
        organization="AeroSync",
    ),
    User(
        username="mahmoud",
        disp_name="Mahmoud Gabr",
        pass_hash="86d74596bb4c2f6b63ae7c09c212a7ed824ab15371ec06a2126dffc3aaa191659478e432c458d5b6a7c0b21b5bf2120c91480c27e78cf94935135d8c022f42f7",
        user_role=UserRole.ADMIN,
        phone_number="+201279227552",
        email="mahmoudGabr@aerosync.com",
        organization="AeroSync",
    ),
]

# regulations schema
seed_regulations = [
    IOSARegulation(
        type=RegulationType.IOSA,
        name="IOSA Standards Manual (ISM) Ed 16-Revision2",
        effective_date=datetime.strptime("1 Nov 2023", "%d %b %Y"),
        sections=[],
    )
]

# unstructured manuals schema
seed_unstructured_manuals = [
    UnstructuredManual(name="Example Manual 1", pages=[]),
    UnstructuredManual(
        name="Example Manual 2",
        pages=[
            "page1 content",
            "page2 content",
            "page3 content",
        ],
    ),
]

# seed fs index
seed_fs_index_files = [
    FSIndexFile(
        username="cwael",
        datetime=datetime.now(),
        file_type=IndexFileType.AIRLINES_MANUAL,
        filename="nesma_org_cos_rad.pdf",
        doc_uuid=os.environ["INVALID_CHAT_DOC_UUID"],
        doc_status=ChatDOCStatus.PARSING_FAILD,
        organization="AeroSync",
    ),
    FSIndexFile(
        username="cwael",
        datetime=datetime.now(),
        file_type=IndexFileType.AIRLINES_MANUAL,
        filename="nesma_org.pdf",
        doc_uuid=os.environ["VALID_CHAT_DOC_UUID"],
        doc_status=ChatDOCStatus.PARSING_FAILD,
        organization="AeroSync",
    ),
    FSIndexFile(
        username="cwael",
        datetime=datetime.now(),
        file_type=IndexFileType.AIRLINES_MANUAL,
        filename="nesma_oma.pdf",
        doc_uuid=os.environ["COMPLETE_CHAT_DOC_UUID"],
        doc_status=ChatDOCStatus.PARSED,
        organization="AeroSync",
    ),
    FSIndexFile(
        username="safwat",
        datetime=datetime.now(),
        file_type=IndexFileType.AIRLINES_MANUAL,
        filename="nesma_org_cos_rad.pdf",
        doc_uuid=os.environ["INVALID_CHAT_DOC_UUID"],
        doc_status=ChatDOCStatus.PARSING_FAILD,
        organization="AeroSync",
    ),
    FSIndexFile(
        username="safwat",
        datetime=datetime.now(),
        file_type=IndexFileType.AIRLINES_MANUAL,
        filename="nesma_org.pdf",
        doc_uuid=os.environ["VALID_CHAT_DOC_UUID"],
        doc_status=ChatDOCStatus.PARSING_FAILD,
        organization="AeroSync",
    ),
    FSIndexFile(
        username="safwat",
        datetime=datetime.now(),
        file_type=IndexFileType.AIRLINES_MANUAL,
        filename="nesma_oma.pdf",
        doc_uuid=os.environ["COMPLETE_CHAT_DOC_UUID"],
        doc_status=ChatDOCStatus.PARSED,
        organization="AeroSync",
    ),
    FSIndexFile(
        username="aelhennawy",
        datetime=datetime.now(),
        file_type=IndexFileType.AIRLINES_MANUAL,
        filename="nesma_org_cos_rad.pdf",
        doc_uuid=os.environ["INVALID_CHAT_DOC_UUID"],
        doc_status=ChatDOCStatus.PARSING_FAILD,
        organization="AeroSync",
    ),
    FSIndexFile(
        username="aelhennawy",
        datetime=datetime.now(),
        file_type=IndexFileType.AIRLINES_MANUAL,
        filename="nesma_org.pdf",
        doc_uuid=os.environ["VALID_CHAT_DOC_UUID"],
        doc_status=ChatDOCStatus.PARSING_FAILD,
        organization="AeroSync",
    ),
    FSIndexFile(
        username="aelhennawy",
        datetime=datetime.now(),
        file_type=IndexFileType.AIRLINES_MANUAL,
        filename="nesma_oma.pdf",
        doc_uuid=os.environ["COMPLETE_CHAT_DOC_UUID"],
        doc_status=ChatDOCStatus.PARSED,
        organization="AeroSync",
    ),
]

# seed ai tasks schema
seed_ai_tasks = [
    AITask(
        username="cwael",
        start_datetime=datetime.now(),
        end_datetime=datetime.now(),
        task_type=AITaskType.COMPLIANCE_CHECK,
        task_status=AITaskStatus.FINISHED,
        json_res=JsonResponse(),
    ),
    AITask(
        username="safwat",
        start_datetime=datetime.now(),
        end_datetime=datetime.now(),
        task_type=AITaskType.COMPLIANCE_CHECK,
        task_status=AITaskStatus.FINISHED,
        json_res=JsonResponse(),
    ),
]

# chat contexts
seed_gpt35t_context = GPT35TContext(
    username="cwael",
    datetime=datetime.now(),
    conversation=[
        GPT35TMessage(
            role=GPT35ContextRole.SYSTEM,
            content="You are an aviation professionals",
        ),
        GPT35TMessage(
            role=GPT35ContextRole.USER,
            content="Audit ISARPs: NONE Againest INPUT_TEXT: NONE",
        ),
        GPT35TMessage(
            role=GPT35ContextRole.ASSISTANT,
            content="Dummy GPT35-TURBO-1106 Response",
        ),
        GPT35TMessage(
            role=GPT35ContextRole.USER,
            content="Ehannce these audit results",
        ),
        GPT35TMessage(
            role=GPT35ContextRole.ASSISTANT,
            content="Dummy GPT35-TURBO-1106 Response",
        ),
    ],
    organization="AeroSync",
)

# system logs schema
seed_log = Log(
    datetime=datetime.now(),
    level="DEBUG",
    source="seed_schema",
    description="seeding database",
)

seed_flow_reports = [
    FlowReport(
        title="Test flow report",
        regulation_id="",
        code="FLT 1",
        sub_sections=[
            ReportSubSectionWritten(
                title="Section 1",
                checklist_items=[
                    ReportItem(
                        page=105,
                        code="FLT 1.2.1",
                        comments="FLT 1.2.1 Seed Comment",
                        checkins=[],
                    )
                ],
            )
        ],
        status=FlowReportStatus.INPROGRESS,
        organization="AeroSync",
        airline="",
        creator="cwael",
        user_changes=[
            UserChange(
                user_name="cwael",
                user_comment="",
                change_type=UserChangeType.CREATE,
            )
        ],
    )
]

seed_airlines = [
    Airline(name="Riyadh Air", organization="AeroSync"),
    Airline(name="Nesma Air", organization="AeroSync"),
    Airline(name="Air Cairo", organization="AeroSync"),
    Airline(name="AeroSync", organization="AeroSync"),
]


def seed_routine():
    print("seeding users...")
    db.get_collection("users").insert_many([x.model_dump() for x in seed_users])
    print("creating users indexes...")
    db.get_collection("users").create_index("username", unique=True)
    db.get_collection("users").create_index("email", unique=True)

    print("seeding regulations index...")
    mdb_result = db.get_collection("regulations").insert_one(
        seed_regulations[0].model_dump()
    )
    iosa_e16r2_id = mdb_result.inserted_id
    print("creating regulations indexes...")
    db.get_collection("regulations").create_index("type", unique=False)

    reg_sm_data = []
    iosa_sections_files = [
        x for x in glob("data/parsed_iosa/iosa_*.json") if "map" not in x
    ]
    for iosa_section_file in iosa_sections_files:
        with open(iosa_section_file, "r") as f:
            file_content = f.read()
            section_json = json.loads(file_content)
            # write to the mongo database
            db.get_collection("regulations").find_one_and_update(
                {"_id": iosa_e16r2_id},
                {"$push": {"sections": section_json}},
            )

    with open(r"data/gacar/GACAR.json", "r") as f:
        file_content = f.read()
        section_json = json.loads(file_content)
        section_json['effective_date'] = datetime.strptime("1 Nov 2023", "%d %b %Y")
        gacar_id = db.get_collection("regulations").insert_one(IOSARegulation.model_validate(section_json).model_dump()).inserted_id
            
    with open(r"data/gacar/GACAR_map.json", "r") as f:
        file_content = f.read()
        section_json = json.loads(file_content)
        for gacar_map in section_json:
            gacar_map["regulation_id"] = gacar_id
            db.get_collection("regulations_source_maps").insert_one(gacar_map)

    print("seeding unstructured manuals...")
    db.get_collection("unstructured_manuals").insert_many(
        [x.model_dump() for x in seed_unstructured_manuals]
    )
    print("creating unstructured manuals indexes...")
    db.get_collection("unstructured_manuals").create_index("name", unique=True)

    print("seeding fs index...")
    # TODO-GALAL add the rest of the oma chapters here
    fs_index_chat_doc_ids = {
        "nesma_oma_ch15.pdf": "e1fb39f6-9c86-4b58-8ccb-0aebb1dbf075",
        "nesma_oma_ch12.pdf": "79a57df5-5047-413f-9b88-68abc13b98a5",
        "nesma_oma_ch1.pdf": "3de78336-42a9-4920-a916-91a4144db589",
    }

    # # # RXI
    for file_path in glob(r"data/RXI/*.pdf"):
        filename = re.split(r"[\\|/]", file_path)[-1]

        fs_index_entry = FSIndexFile(
            username="cwael",
            datetime=datetime.now(),
            file_type=IndexFileType.AIRLINES_MANUAL,
            filename=filename,
            doc_uuid=(
                fs_index_chat_doc_ids[filename]
                if fs_index_chat_doc_ids.get(filename) != None
                else str(uuid4())
            ),
            doc_status=ChatDOCStatus.PARSED,
            organization="AeroSync",
            args={"toc_info": RXI_parser(file_path)},
        )

        mdb_result = db.get_collection("fs_index").insert_one(
            fs_index_entry.model_dump()
        )

        file_id = str(mdb_result.inserted_id)
        dst_path = f"public/airlines_files/manuals/{file_id}.pdf"
        shutil.copy2(file_path, dst_path)
        print(f"file map {file_path} -> {dst_path}")

    # # Nesma
    for file_path in glob(r"data/nesma/*.pdf"):
        filename = re.split(r"[\\|/]", file_path)[-1]

        fs_index_entry = FSIndexFile(
            username="cwael",
            datetime=datetime.now(),
            file_type=IndexFileType.AIRLINES_MANUAL,
            filename=filename,
            doc_uuid=(
                fs_index_chat_doc_ids[filename]
                if fs_index_chat_doc_ids.get(filename) != None
                else str(uuid4())
            ),
            doc_status=ChatDOCStatus.PARSED,
            organization="AeroSync",
            args={"toc_info": nesma_parser(file_path)},
        )

        mdb_result = db.get_collection("fs_index").insert_one(
            fs_index_entry.model_dump()
        )

        file_id = str(mdb_result.inserted_id)
        dst_path = f"public/airlines_files/manuals/{file_id}.pdf"
        shutil.copy2(file_path, dst_path)
        print(f"file map {file_path} -> {dst_path}")

    # db.get_collection("fs_index").insert_many(
    #     [x.model_dump() for x in seed_fs_index_files]
    # )

    print("creating fs index indexes...")
    db.get_collection("fs_index").create_index("doc_uuid", unique=False)
    db.get_collection("fs_index").create_index("username", unique=False)
    db.get_collection("fs_index").create_index("filename", unique=False)

    print("seeding ai tasks...")
    db.get_collection("ai_tasks").insert_many([x.model_dump() for x in seed_ai_tasks])
    print("creating ai tasks indexes...")
    db.get_collection("ai_tasks").create_index("username", unique=False)

    print("seeding chat contexts...")
    db.get_collection("gpt35t_contexts").insert_one(seed_gpt35t_context.model_dump())
    db.get_collection("gpt35t_contexts").create_index("username", unique=False)

    print("seeding logs...")
    db.get_collection("logs").insert_one(seed_log.model_dump())
    print("creating logs indexes...")
    db.get_collection("logs").create_index([("date", pymongo.DESCENDING)], unique=False)

    # seed regulations source map
    reg_sm_files = [x for x in glob("data/parsed_iosa/iosa_*_map.json")]
    for sm_file in reg_sm_files:
        with open(sm_file, "r") as f:
            json_obj = json.loads(f.read())
            for x in json_obj:
                x["regulation_id"] = iosa_e16r2_id
            reg_sm_data += json_obj

    print("seeding regulations source maps...")
    db.get_collection("regulations_source_maps").insert_many(reg_sm_data)
    print("creating regulations source maps indexes...")
    db.get_collection("regulations_source_maps").create_index("code", unique=True)

    print("seeding airlines...")
    for airline in seed_airlines:
        airline_id = (
            db.get_collection("airlines").insert_one(airline.model_dump()).inserted_id
        )
    print("creating airlines indexes...")
    db.get_collection("airlines").create_index("organization", unique=False)

    print("seeding flow reports...")
    for report in seed_flow_reports:
        report = report.model_dump()
        report["regulation_id"] = str(iosa_e16r2_id)
        report["sub_sections"][0]["checklist_items"][0]["checkins"] = []
        report["airline"] = str(airline_id)
        db.get_collection("flow_reports").insert_one(report)
    print("creating flow report indices...")
    db.get_collection("flow_reports").create_index("organization", unique=False)
    db.get_collection("flow_reports").create_index("creator", unique=False)


seed_routine()
