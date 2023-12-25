# autopep8: off
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
        user_role=UserRoles.AUDITOR,
        phone_number='+201001000000',
        email='cwael@aerosync.com',
    ),
    User(
        username='eslam',
        disp_name='Eslam Admin',
        pass_hash='86d74596bb4c2f6b63ae7c09c212a7ed824ab15371ec06a2126dffc3aaa191659478e432c458d5b6a7c0b21b5bf2120c91480c27e78cf94935135d8c022f42f7',
        user_role=UserRoles.ADMIN,
        phone_number='+201001000000',
        email='eslam@aerosync.com',
    ),
]

# regulations schema
seed_regulations = [
    IOSARegulation(type=RegulationType.IOSA, name='IOSA Standards Manual (ISM) Ed 15', sections=[]),
    IOSARegulation(type=RegulationType.IOSA, name='IOSA Standards Manual (ISM) Ed 16-Revision2', sections=[
        IOSASection(
            name='Section 2 Flight Operations',
            code='FLT',
            applicability='addresses safety and security requirements for flight operations, and is applicable to an operator that uses two-pilot, multi-engine aircraft with a maximum certificated takeoff mass in excess of 5,700 kg (12,566 lbs.).',
            guidance='The definitions of technical terms used in this ISM Section 2, as well as the list of abbreviations and acronyms, are found in the IATA Reference Manual for Audit Programs (IRM).',
            order=1,
            items=[
                IOSAItem(
                    code='FLT 1.1.1',
                    guidance='Refer to the IRM for the definitions of Operations and Operator.',
                    constraint=Constrain(text='The Operator shall have a management system for the flight operations organization that ensures control of flight operations and the management of safety and security outcomes.'),
                ),
                IOSAItem(
                    code='FLT 1.1.2',
                    guidance='Refer to the IRM for the definitions of Accountability, Authority, Post Holder and Responsibility.',
                    constraint=Constrain(
                        text='The Operator shall have one or more designated managers in the flight operations organization that, if required, are post holders acceptable to the Authority, and have the responsibility for ensuring:',
                        children=[
                            Constrain(text='The management and supervision of all flight operations activities.'),
                            Constrain(text='The management of safety and security risks to flight operations.'),
                            Constrain(text='Flight operations are conducted in accordance with conditions and restrictions of the Air Operator Certificate (AOC), and in compliance with applicable regulations and standards of the Operator.'),
                        ],
                    ),
                ),
                IOSAItem(
                    code='FLT 1.3.4',
                    guidance='Refer to Guidance associated with ORG 1.3.3 located in ISM Section 1 regarding the need to coordinate and communicate with external entities.',
                    constraint=Constrain(
                        text='The Operator shall ensure pilot flight crew members complete an evaluation that includes a demonstration of knowledge of the operations approved as part of the Air Operator Certificate (AOC). Such evaluation shall include a demonstration of knowledge of:',
                        children=[
                            Constrain(text='Approaches authorized by the Authority.'),
                            Constrain(text='Ceiling and visibility requirements for takeoff, approach and landing.'),
                            Constrain(text='Allowance for inoperative ground components.'),
                            Constrain(text='Wind limitations (crosswind, tailwind and, if applicable, headwind).'),
                        ],
                    ),
                ),
                IOSAItem(
                    code='FLT 1.5.2',
                    guidance='Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.',
                    constraint=Constrain(text='The Operator shall have a selection process for management and non-management positions within the organization that require the performance of functions relevant to the safety or security of aircraft operations.'),
                ),
            ],
        ),
    ])
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
    db.get_collection('regulations').insert_many([x.model_dump() for x in seed_regulations])
    print('creating regulations indexes...')
    db.get_collection('regulations').create_index('type', unique=False)

    print('seeding unstructured manuals...')
    db.get_collection('unstructured_manuals').insert_many([x.model_dump() for x in seed_unstructured_manuals])
    print('creating unstructured manuals indexes...')
    db.get_collection('unstructured_manuals').create_index('name', unique=True)

    print('seeding logs...')
    db.get_collection('logs').insert_one(seed_log.model_dump())
    print('creating logs indexes...')
    db.get_collection('logs').create_index([('date', pymongo.DESCENDING)], unique=False)


seed_routine()
