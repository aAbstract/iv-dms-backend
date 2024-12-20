from datetime import datetime
from models.ai_tasks import *
from models.runtime import ServiceResponse
from models.httpio import JsonResponse
from database.mongo_driver import get_database, validate_bson_id


async def get_ai_task_status(task_id: str, username: str) -> ServiceResponse:
    bson_id = validate_bson_id(task_id)
    if not bson_id:
        return ServiceResponse(success=False, msg='Bad Task ID', status_code=400)

    ai_task = await get_database().get_collection('ai_tasks').find_one({'_id': bson_id, 'username': username})
    if not ai_task:
        return ServiceResponse(success=False, status_code=404, msg='AI Task not Found')

    return ServiceResponse(data={
        'ai_task_status': ai_task['task_status'],
        'json_res': ai_task['json_res'],
    })


async def set_ai_task_status(task_id: str, new_status: AITaskStatus) -> ServiceResponse:
    bson_id = validate_bson_id(task_id)
    if not bson_id:
        return ServiceResponse(success=False, msg='Bad Task ID', status_code=400)

    mdb_result = await get_database().get_collection('ai_tasks').update_one({'_id': bson_id}, {'$set': {'task_status': new_status}})
    if mdb_result.modified_count != 1:
        return ServiceResponse(success=False, status_code=409, msg='Can not Change this AI Task State')

    return ServiceResponse(msg='OK')


async def set_ai_task_resp(task_id: str, res: JsonResponse) -> ServiceResponse:
    bson_id = validate_bson_id(task_id)
    if not bson_id:
        return ServiceResponse(success=False, msg='Bad Task ID', status_code=400)

    mdb_result = await get_database().get_collection('ai_tasks').update_one({'_id': bson_id}, {'$set': {'json_res': res.model_dump()}})
    if mdb_result.modified_count != 1:
        return ServiceResponse(success=False, status_code=409, msg='Can not Change this AI Task JSON Response')

    return ServiceResponse(msg='OK')


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


async def create_ai_task(username: str, task_type: AITaskType) -> ServiceResponse:
    task = AITask(
        username=username,
        start_datetime=datetime.now(),
        end_datetime=None,
        task_type=task_type,
        task_status=AITaskStatus.IN_PROGRESS,
        json_res=JsonResponse(),
    )

    mdb_result = await get_database().get_collection('ai_tasks').insert_one(task.model_dump())
    task_id = str(mdb_result.inserted_id)
    return ServiceResponse(data={'ai_task_id': task_id})
