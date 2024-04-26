from bson import ObjectId
from models.runtime import ServiceResponse
from database.mongo_driver import get_database
from models.logs import Log
from models.users import UserRole


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


async def increment_airline_reqest_count(airline_username: str) -> ServiceResponse:

    user = await get_database().get_collection("users").find_one({'username': airline_username})

    if user['user_role'] != UserRole.AIRLINES:
        return ServiceResponse()

    db_service_response = await get_database().get_collection("users").update_one({'username': airline_username}, 
                                                                         {"$inc": {"request_count": 1}})

    if not db_service_response.acknowledged:
        return ServiceResponse(
            success=False, msg="Failed to Increment Token Count for Airline", status_code=500
        )

    return ServiceResponse()

async def increment_airline_token_count(airline_username: str, input_token_count: int,output_token_count:int) -> ServiceResponse:

    user = await get_database().get_collection("users").find_one({'username': airline_username})

    if user['user_role'] != UserRole.AIRLINES:
        return ServiceResponse()

    db_service_response = await get_database().get_collection("users").update_one({'username': airline_username}, 
                                                                         {"$inc": {"input_token_count": input_token_count,
                                                                                   "output_token_count":output_token_count}})

    if not db_service_response.acknowledged:
        return ServiceResponse(
            success=False, msg="Failed to Increment Token Count for Airline", status_code=500
        )

    return ServiceResponse()