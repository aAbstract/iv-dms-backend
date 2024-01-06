from models.runtime import ServiceResponse
from database.mongo_driver import get_database
from models.logs import Log


async def get_logs(length: int) -> ServiceResponse:
    logs = await get_database().get_collection('logs').find({}, {
        '_id': 0,
        'id': {'$toString': '$_id'},
        'datetime': 1,
        'level': 1,
        'source': 1,
        'description': 1,
    }).sort({'datetime': -1}).to_list(length=length if length >= 0 else None)
    logs = [Log.model_validate(x) for x in logs]
    return ServiceResponse(data={'logs': logs})
