import os
import lib.log as log_man
import motor.motor_asyncio as maio
from pymongo.server_api import ServerApi
from bson import ObjectId


mdb_client: maio.AsyncIOMotorClient | None = None


async def mongodb_connect():
    func_id = 'mongodb_connect'
    global mdb_client
    connection_string = f"mongodb://{os.environ['MDB_USERNAME']}:{os.environ['MDB_PASSWORD']}@127.0.0.1"
    mdb_client = maio.AsyncIOMotorClient(connection_string, server_api=ServerApi('1'), serverSelectionTimeoutMS=3000)
    await log_man.add_log(func_id, 'INFO', 'connecting to mongodb server')
    try:
        await mdb_client.get_database('admin').command('ping')
        await log_man.add_log(func_id, 'INFO', 'connected to mongodb server successfully')
    except Exception as e:
        await log_man.add_log(func_id, 'ERROR', f"error connecting to mongodb server: {e}")


def get_database() -> maio.core.AgnosticDatabase | None:
    if mdb_client:
        return mdb_client.get_database(os.environ['IVDMS_DB'])
    return None


def validate_bson_id(bson_id: str) -> ObjectId | None:
    try:
        return ObjectId(bson_id)
    except:
        return None
