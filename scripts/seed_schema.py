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
    IOSARegulation(type=RegulationType.IOSA, name='IOSA Standards Manual (ISM) Ed 15', sections=[
        IOSASection(
            name="Section 2 Flight Operations",
            code="FLT",
            applicability="addresses safety and security requirements for flight operations, and is applicable to an operator that uses two-pilot, multi-engine aircraft with a maximum certificated takeoff mass in excess of 5,700 kg (12,566 lbs.).",
            guidance="The definitions of technical terms used in this ISM Section 2, as well as the list of abbreviations and acronyms, are found in the IATA Reference Manual for Audit Programs (IRM).",
            order=2,
            items=[
                IOSAItem(
                    code='FLT 1.1.1',
                    guidance='Refer to the IRM for the definitions of Operations and Operator.',
                    iosa_map=['1 Management and Control', '1.1 Management System Overview'],
                    paragraph='',
                    constraints=[
                        Constrain(text='The Operator shall have a management system for the flight operations organization that ensures control of flight operations and the management of safety and security outcomes.'),
                        Constrain(text='Sample Constain'),
                    ],
                ),
                IOSAItem(
                    code='FLT 1.1.2',
                    guidance='Refer to the IRM for the definitions of Accountability, Authority, Post Holder and Responsibility.',
                    iosa_map=['1 Management and Control', '1.1 Management System Overview'],
                    paragraph='',
                    constraints=[Constrain(
                        text='The Operator shall have one or more designated managers in the flight operations organization that, if required, are post holders acceptable to the Authority, and have the responsibility for ensuring:',
                        children=[
                            Constrain(text='The management and supervision of all flight operations activities.'),
                            Constrain(text='The management of safety and security risks to flight operations.'),
                            Constrain(text='Flight operations are conducted in accordance with conditions and restrictions of the Air Operator Certificate (AOC), and in compliance with applicable regulations and standards of the Operator.'),
                        ],
                    )],
                ),
                IOSAItem(
                    code='FLT 1.3.4',
                    guidance='Refer to Guidance associated with ORG 1.3.3 located in ISM Section 1 regarding the need to coordinate and communicate with external entities.',
                    iosa_map=['1 Management and Control', '1.3 Accountability, Authorities and Responsibilities'],
                    paragraph='',
                    constraints=[
                        Constrain(
                            text='The Operator shall ensure pilot flight crew members complete an evaluation that includes a demonstration of knowledge of the operations approved as part of the Air Operator Certificate (AOC). Such evaluation shall include a demonstration of knowledge of:',
                            children=[
                                Constrain(text='Approaches authorized by the Authority.'),
                                Constrain(text='Ceiling and visibility requirements for takeoff, approach and landing.'),
                                Constrain(text='Allowance for inoperative ground components.'),
                                Constrain(text='Wind limitations (crosswind, tailwind and, if applicable, headwind).'),
                            ],
                        ),
                        Constrain(
                            text='Sample Constrain',
                            children=[
                                Constrain(text='item 1'),
                                Constrain(text='item 2'),
                                Constrain(text='item 3'),
                                Constrain(text='item 4'),
                            ],
                        ),
                    ],
                ),
                IOSAItem(
                    code='FLT 1.5.2',
                    guidance='Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.',
                    iosa_map=['1 Management and Control', '1.5 Provision of Resources'],
                    paragraph='',
                    constraints=[Constrain(text='The Operator shall have a selection process for management and non-management positions within the organization that require the performance of functions relevant to the safety or security of aircraft operations.')],
                ),
                IOSAItem(
                    code='FLT 2.1.35',
                    guidance='',
                    iosa_map=[],
                    paragraph='',
                    constraints=[
                        Constrain(
                            text='The Operator shall have an initial training program for instructors, evaluators and line check airmen,to include:',
                            children=[
                                Constrain(
                                    text='An instructor course that addresses as a minimum',
                                    children=[
                                        Constrain(text='The fundamentals of teaching and evaluation'),
                                        Constrain(text='Lesson plan management'),
                                        Constrain(text='Briefing and debriefing'),
                                        Constrain(text='Human performance issues'),
                                        Constrain(text='Company policies and procedures'),
                                        Constrain(text='Simulator serviceability and training in simulator operation'),
                                        Constrain(text='If the Operator conducts training flights, dangers associated with simulating system failures in flight'),
                                        Constrain(text='As applicable, the simulated or actual weather and environmental conditions necessary to conduct each simulator or aircraft training/evaluation session to be administered'),
                                    ],
                                )
                            ],
                        ),
                        Constrain(text='The Operator shall have a management system for the flight operations organization that ensures control of flight operations and the management of safety and security outcomes.'),
                    ],
                ),
                IOSAItem(
                    code='FLT 2.1.21',
                    guidance='',
                    iosa_map=[],
                    paragraph='',
                    constraints=[Constrain(text='The Operator shall have sufficient instructors, evaluators, line check airmen and support personnel to administer the training and evaluation programs in accordance with requirements of the Operator and/or the State, as applicable.')],
                ),
                IOSAItem(
                    code="FLT 3.1.1",
                    guidance="Refer to the IRM for the definitions of Operations and Operator.",
                    iosa_map=["3 Line Operations", "3.1 Common Language"],
                    paragraph='',
                    constraints=[
                        Constrain(
                            text="The Operator shall ensure the designation of a common language(s) for use by all flight crew members for communication:",
                            children=[
                                Constrain(text="On the flight deck during line operations"),
                                Constrain(text="If the Operator conducts passenger flights with cabin crew, between the flight crew and cabin crew during line operations"),
                                Constrain(text="During flight crew training and evaluation activities"),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        IOSASection(
            name='Section 3 Operational Control and Flight Dispatch',
            code='DSP',
            applicability='addresses the requirements for operational control of flights conducted by multi-engine aircraft and is applicable to an operator that conducts such flights, whether operational control functions are conducted by the operator or conducted for the operator by an external organization (outsourced).',
            guidance='For the purposes of this section authority is defined as the delegated power or right to command or direct, to make specific decisions, to grant permission and/or provide approval, or to control or modify a process.',
            order=3,
            items=[
                IOSAItem(
                    code='DSP 1.1.1',
                    guidance='',
                    iosa_map=['1 Management and Control', '1.1 Management System Overview'],
                    paragraph='',
                    constraints=[],
                ),
                IOSAItem(
                    code='DSP 1.1.2',
                    guidance='',
                    iosa_map=['1 Management and Control', '1.1 Management System Overview'],
                    paragraph='',
                    constraints=[],
                ),
                IOSAItem(
                    code='DSP 1.1.3',
                    guidance='',
                    iosa_map=['1 Management and Control', '1.1 Management System Overview'],
                    paragraph='',
                    constraints=[],
                ),
                IOSAItem(
                    code='DSP 1.1.4',
                    guidance='',
                    iosa_map=['1 Management and Control', '1.1 Management System Overview'],
                    paragraph='',
                    constraints=[],
                ),
            ],
        ),
    ]),
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
        doc_uuid=os.environ['INVALID_CHAT_DOC_UUID'],
        doc_status=ChatDOCStatus.PARSED,
    ),
    FSIndexFile(
        username='cwael',
        datetime=datetime.now(),
        file_type=IndexFileType.AIRLINES_MANUAL,
        file_id='000000000000000000000000',
        filename='nesma_org.pdf',
        doc_uuid=os.environ['VALID_CHAT_DOC_UUID'],
        doc_status=ChatDOCStatus.PARSED,
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
    db.get_collection('fs_index').create_index('doc_uuid', unique=True)
    db.get_collection('fs_index').create_index('username', unique=False)
    db.get_collection('fs_index').create_index('filename', unique=False)

    print('seeding logs...')
    db.get_collection('logs').insert_one(seed_log.model_dump())
    print('creating logs indexes...')
    db.get_collection('logs').create_index([('date', pymongo.DESCENDING)], unique=False)


seed_routine()
