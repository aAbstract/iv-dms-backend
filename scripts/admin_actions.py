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
import lib.crypto as crypto_man
from models.users import *
from scripts.scripts_config import *
# autopep8: on


print(f"Connecting to MDB database, SERVER_ADDR={SERVER_ADDR}")
client = pymongo.MongoClient(f"mongodb://{os.environ['MDB_USERNAME']}:{os.environ['MDB_PASSWORD']}@{SERVER_ADDR}")
db = client.get_database(os.environ['IVDMS_DB'])
print('Connected to MDB database')


def add_user_account(username: str, password: str, disp_name: str, user_role: UserRole, phone_number: str = '+201001000000'):
    pass_hash = crypto_man.hash_password(password)
    user = User(
        username=username,
        disp_name=disp_name,
        pass_hash=pass_hash,
        user_role=user_role,
        phone_number=phone_number,
        email=f"{username}@aerosync.com"
    )
    mdb_result = db.get_collection('users').insert_one(user.model_dump())
    user_id = str(mdb_result.inserted_id)
    print(f"Added user, user_id={user_id}")


readline.set_completer(Completer().complete)
readline.parse_and_bind("tab: complete")
code.interact(local=locals())
