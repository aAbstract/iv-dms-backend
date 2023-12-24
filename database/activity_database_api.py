from models.runtime import ServiceResponse
from database.mongo_driver import get_database


async def get_logs(length: int) -> ServiceResponse:
    logs = await get_database().get_collection('logs').find({}, {'_id': 0}).sort({'date': -1}).to_list(length=length)
    return ServiceResponse(data={'logs': logs})
