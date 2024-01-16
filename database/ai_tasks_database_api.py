from models.ai_tasks import AITask
from models.runtime import ServiceResponse
from database.mongo_driver import get_database, validate_bson_id


async def get_ai_task_status(task_id: str, username: str) -> ServiceResponse:
    bson_id = validate_bson_id(task_id)
    if not bson_id:
        return ServiceResponse(success=False, msg='Bad Task ID', status_code=400)

    ai_task = await get_database().get_collection('ai_tasks').find_one({'_id': bson_id, 'username': username})
    if not ai_task:
        return ServiceResponse(success=False, status_code=404, msg='AI Task not Found')

    return ServiceResponse(data={'ai_task_status': ai_task['task_status']})


async def get_all_ai_tasks(username: str) -> ServiceResponse:
    ai_tasks = await get_database().get_collection('ai_tasks').find({'username': username}, {
        '_id': 0,
        'id': {'$toString': '$_id'},
        'start_datetime': 1,
        'end_datetime': 1,
        'task_type': 1,
        'task_status': 1,
    }).to_list(length=None)
    if not ai_tasks:
        return ServiceResponse(success=False, status_code=404, msg='No AI Tasks Found for this User')

    return ServiceResponse(data={'ai_tasks': ai_tasks})
