# autopep8: off
import json
import os
import sys
import pymongo
from dotenv import load_dotenv
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
# autopep8: on


# main
client = pymongo.MongoClient(f"mongodb://{os.environ['MDB_USERNAME']}:{os.environ['MDB_PASSWORD']}@127.0.0.1")
db = client.get_database(os.environ['IVDMS_DB'])

# users schema
seed_users = [
    User(
        username='cwael',
        disp_name='Captin Wael',
        pass_hash='86d74596bb4c2f6b63ae7c09c212a7ed824ab15371ec06a2126dffc3aaa191659478e432c458d5b6a7c0b21b5bf2120c91480c27e78cf94935135d8c022f42f7',
        user_role=UserRole.AUDITOR,
        phone_number='+201001000000',
        email='cwael@aerosync.com',
    ),
    User(
        username='eslam',
        disp_name='Eslam Admin',
        pass_hash='86d74596bb4c2f6b63ae7c09c212a7ed824ab15371ec06a2126dffc3aaa191659478e432c458d5b6a7c0b21b5bf2120c91480c27e78cf94935135d8c022f42f7',
        user_role=UserRole.ADMIN,
        phone_number='+201001000000',
        email='eslam@aerosync.com',
    ),
    User(
        username='safwat',
        disp_name='Safwat Admin',
        pass_hash='bee066ca744aa10dffa39924161a190c5193988779b7ec58694b2bc15e104c998164bf04500c8523005f36ea4fc660f8cb8cf476eea14285a8079f2a530fbb9f',
        user_role=UserRole.ADMIN,
        phone_number='+201001000000',
        email='safwat@aerosync.com',
    ),
    User(
        username='aelhennawy',
        disp_name='Amr Elhennawy',
        pass_hash='6204c03169cb87f6834c1dd0419e0a06d1dfca3b0df37fef6b7f2bf5baa016b03463c3906c8669e797ba49c67b3f9950dfc7248ce278f922fc0592e7044a3d32',
        user_role=UserRole.AUDITOR,
        phone_number='+201001000000',
        email='aelhennawy@aerosync.com',
    ),
]

# regulations schema
seed_regulations = [
    IOSARegulation(type=RegulationType.IOSA, name='IOSA Standards Manual (ISM) Ed 15', sections=[]),
    IOSARegulation(type=RegulationType.IOSA, name='IOSA Standards Manual (ISM) Ed 16-Revision2', sections=[])
]

# unstructured manuals schema
seed_unstructured_manuals = [
    UnstructuredManual(name='Example Manual 1', pages=[]),
    UnstructuredManual(
        name='Example Manual 2',
        pages=[
            'page1 content',
            'page2 content',
            'page3 content',
        ],
    )
]

# seed fs index
seed_fs_index_files = [
    FSIndexFile(
        username='cwael',
        datetime=datetime.now(),
        file_type=IndexFileType.AIRLINES_MANUAL,
        file_id='000000000000000000000000',
        filename='nesma_org_cos_rad.pdf',
        chat_doc_uuid=os.environ['INVALID_CHAT_DOC_UUID'],
        chat_doc_status=ChatDocStatus.PARSED,
    ),
    FSIndexFile(
        username='cwael',
        datetime=datetime.now(),
        file_type=IndexFileType.AIRLINES_MANUAL,
        file_id='000000000000000000000000',
        filename='nesma_org.pdf',
        chat_doc_uuid=os.environ['VALID_CHAT_DOC_UUID'],
        chat_doc_status=ChatDocStatus.PARSED,
    ),
]

# system logs schema
seed_log = Log(
    datetime=datetime.now(),
    level='DEBUG',
    source='seed_schema',
    description='seeding database',
)


def seed_routine():
    print('seeding users...')
    db.get_collection('users').insert_many([x.model_dump() for x in seed_users])
    print('creating users indexes...')
    db.get_collection('users').create_index('username', unique=True)
    db.get_collection('users').create_index('email', unique=True)

    print('seeding regulations index...')
    db.get_collection('regulations').insert_one(seed_regulations[0].model_dump())
    mdb_result = db.get_collection('regulations').insert_one(seed_regulations[1].model_dump())
    iosa_e16r2_id = mdb_result.inserted_id
    print('creating regulations indexes...')
    db.get_collection('regulations').create_index('type', unique=False)
    with open('data/iosa_flt.json', 'r') as f:
        file_content = f.read()
        section_json = json.loads(file_content)

        # write to the mongo database
        db.get_collection("regulations").find_one_and_update(
            {"_id": iosa_e16r2_id},
            {"$push": {"sections": section_json}},
        )

    print('seeding unstructured manuals...')
    db.get_collection('unstructured_manuals').insert_many([x.model_dump() for x in seed_unstructured_manuals])
    print('creating unstructured manuals indexes...')
    db.get_collection('unstructured_manuals').create_index('name', unique=True)

    print('seeding fs index...')
    db.get_collection('fs_index').insert_many([x.model_dump() for x in seed_fs_index_files])
    print('creating fs index indexes...')
    db.get_collection('fs_index').create_index('chat_doc_uuid', unique=True)
    db.get_collection('fs_index').create_index('username', unique=False)
    db.get_collection('fs_index').create_index('filename', unique=False)

    print('seeding logs...')
    db.get_collection('logs').insert_one(seed_log.model_dump())
    print('creating logs indexes...')
    db.get_collection('logs').create_index([('date', pymongo.DESCENDING)], unique=False)


seed_routine()
