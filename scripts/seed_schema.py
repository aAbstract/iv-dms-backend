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
db = client.test_db

# users schema
seed_user = User(
    username='cwael',
    disp_name='Captin Wael',
    pass_hash='86d74596bb4c2f6b63ae7c09c212a7ed824ab15371ec06a2126dffc3aaa191659478e432c458d5b6a7c0b21b5bf2120c91480c27e78cf94935135d8c022f42f7',
    user_role=UserRoles.AUDITOR,
    phone_number='+201001000000',
    email='test@example.com',
)

# regulations schema
seed_iosa_regulation = IOSARegulation(type=RegulationType.IOSA, disp_name='IOSA Standards Manual (ISM) Ed 16-Revision2', sections=[
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
regulations_index = {
    'iosa_ism_e16r2': seed_iosa_regulation.dict(),
}

# manuals schema
# seed_sections = [
#     ManualSection(
#         header='1.1 Organizational Structure',
#         order=1,
#         text='''
#         The following organization chart depicts the company and the flight operations department
#         organizational structure.
#         They show the relationship between the various departments of the company and the associated
#         subordination and reporting lines and control of flight operations and the management of safety
#         and security outcomes.
#         Director of Operations ensures that communication within his department and other
#         departments are established in a way that guarantees the exchange of relevant operational
#         information.
#         ''',
#         regulations_codes=[ManualRegulationCode(type=RegulationType.IOSA, cat_code='FLT', code='FLT 1.1.1')],
#     ),
#     ManualSection(
#         header='1.2 Nominated Post Holders',
#         order=2,
#         text='''
#         - The nominated post holders must have managerial competency and appropriate
#         technical and operational qualifications;
#         - Their contract of employment must allow them to work sufficient hours, in order to be
#         able to satisfactorily perform the functions associated with the operation of
#         AIRCAIRO, apart from any flying duties;
#         - Nominated post holders and managers have the responsibility, and they are accountable,
#         for ensuring:
#             • Flight operations are conducted in accordance with the conditions and restrictions
#             of the AOC and in compliance with the applicable regulations and standards of
#             AIRCAIRO and other applicable rules and requirements (e.g., IOSA
#             Requirements);
#             • The management and supervision of all flight operations activities;
#             • The management of safety and security in flight operations;
#         - All required management Personnel and Post holders mentioned in the OM Part A
#         should fulfill the qualifications required by the ECAR (part 121) and AIRCAIRO
#         policies.
#         NOTE: Nominat
#         ''',
#         regulations_codes=[
#             ManualRegulationCode(type=RegulationType.IOSA, cat_code='FLT', code='FLT 1.1.2'),
#             ManualRegulationCode(type=RegulationType.IOSA, cat_code='FLT', code='FLT 1.3.4'),
#             ManualRegulationCode(type=RegulationType.IOSA, cat_code='FLT', code='FLT 1.5.2'),
#         ],
#     ),
# ]
# seed_manual = Manual(
#     name='Air Cairo FLT 3',
#     chapters=[
#         ManualChapter(name='Chapter 1 Organization and Responsibilities', order=1, sections=seed_sections),
#     ],
# )

# system logs schema
seed_log = Log(
    date=datetime.now(),
    level='DEBUG',
    source='seed_schema',
    description='seeding database',
)


def seed_routine():
    print('seeding user...')
    db.users.insert_one(seed_user.dict())
    print('creating user indexes...')
    db.users.create_index([('username', pymongo.ASCENDING)], unique=True)
    db.users.create_index([('email', pymongo.ASCENDING)], unique=True)

    print('seeding regulations index...')
    db.regulations.insert_one(regulations_index)

    # print('seeding example manual...')
    # db.manuals.insert_one(seed_manual.dict())

    # # TODO: seed simple manual
    # # TODO: seed compliance report

    # print('seeding example log...')
    # db.logs.insert_one(seed_log.dict())


seed_routine()
