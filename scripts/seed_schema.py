# autopep8: off
import os
import sys
from pymongo import MongoClient
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
# autopep8: on


# main
client = MongoClient(f"mongodb://{os.environ['MDB_USERNAME']}:{os.environ['MDB_PASSWORD']}@127.0.0.1")
db = client.test_db

# users schema
users = db.users
seed_user = User(
    username='air_cairo',
    disp_name='Air Cairo',
    pass_hash='',
    user_role=UserRoles.AIRLINES,
    phone_number='+201001000000',
    email='test@example.com',
)
# users.insert_one(seed_user.dict())

# regulations schema

# manuals schema
manuals = db.manuals
seed_sections = [
    ManualSection(
        header='1.1 Organizational Structure',
        order=1,
        text='''
        The following organization chart depicts the company and the flight operations department
        organizational structure.
        They show the relationship between the various departments of the company and the associated
        subordination and reporting lines and control of flight operations and the management of safety
        and security outcomes.
        Director of Operations ensures that communication within his department and other
        departments are established in a way that guarantees the exchange of relevant operational
        information.
        ''',
        regulations_codes=[ManualRegulationCode(type=RegulationType.IOSA, cat_code='FLT', code='FLT 1.1.1')],
    ),
    ManualSection(
        header='1.2 Nominated Post Holders',
        order=2,
        text='''
        - The nominated post holders must have managerial competency and appropriate
        technical and operational qualifications;
        - Their contract of employment must allow them to work sufficient hours, in order to be
        able to satisfactorily perform the functions associated with the operation of
        AIRCAIRO, apart from any flying duties;
        - Nominated post holders and managers have the responsibility, and they are accountable,
        for ensuring:
            • Flight operations are conducted in accordance with the conditions and restrictions
            of the AOC and in compliance with the applicable regulations and standards of
            AIRCAIRO and other applicable rules and requirements (e.g., IOSA
            Requirements);
            • The management and supervision of all flight operations activities;
            • The management of safety and security in flight operations;
        - All required management Personnel and Post holders mentioned in the OM Part A
        should fulfill the qualifications required by the ECAR (part 121) and AIRCAIRO
        policies.
        NOTE: Nominat
        ''',
        regulations_codes=[
            ManualRegulationCode(type=RegulationType.IOSA, cat_code='FLT', code='FLT 1.1.2'),
            ManualRegulationCode(type=RegulationType.IOSA, cat_code='FLT', code='FLT 1.3.4'),
            ManualRegulationCode(type=RegulationType.IOSA, cat_code='FLT', code='FLT 1.5.2'),
        ],
    ),
]
seed_manual = Manual(
    name='Air Cairo FLT 3',
    chapters=[
        ManualChapter(name='Chapter 1 Organization and Responsibilities', order=1, sections=seed_sections),
    ],
)
# manuals.insert_one(seed_manual)
