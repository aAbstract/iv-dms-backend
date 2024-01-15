from models.runtime import ServiceResponse
from database.mongo_driver import get_database
from models.logs import Log
from models.users import User

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
    return ServiceResponse(data={"logs": logs})


async def get_activity(user_name: str) -> ServiceResponse:

    user = await get_database().get_collection("users").find_one({"username": user_name})
    if not user:
        return ServiceResponse(success=False, msg="User Name not Found", status_code=404)

    user = User.model_validate(user)
    return ServiceResponse(data={"activity": user.activity})


async def increment_activity(user_name: str, api_type: str) -> ServiceResponse:

    user = await get_database().get_collection("users").find_one({"username": user_name})
    if not user:
        return ServiceResponse(success=False, msg="User Name not Found", status_code=404)

    user = User.model_validate(user).model_dump()

    # increment
    user['activity'][api_type] += 1
    user = await get_database().get_collection("users").update_one({"username": user_name},{"$set": user})

    if not user:
        return ServiceResponse(success=False, msg="Failed to increment", status_code=404)

    return ServiceResponse(success= True)