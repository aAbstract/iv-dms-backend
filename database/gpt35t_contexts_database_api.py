from datetime import datetime
from models.runtime import ServiceResponse
from models.gpt_35t import GPT35TMessage, GPT35TContext
from database.mongo_driver import get_database, validate_bson_id


async def create_gpt35t_context(username: str, conversation: list[GPT35TMessage]) -> ServiceResponse:
    gpt35t_context = GPT35TContext(
        username=username,
        datetime=datetime.now(),
        conversation=conversation,
    )

    mdb_result = await get_database().get_collection('gpt35t_contexts').insert_one(gpt35t_context.model_dump())
    context_id = str(mdb_result.inserted_id)
    return ServiceResponse(data={'context_id': context_id})


async def get_gpt35t_context(context_id: str) -> ServiceResponse:
    bson_id = validate_bson_id(context_id)
    if not bson_id:
        return ServiceResponse(success=False, msg='Bad Context ID', status_code=400)

    gpt35t_context = await get_database().get_collection('gpt35t_contexts').find_one({'_id': bson_id}, {
        '_id': 0,
        'id': {'$toString': '$_id'},
        'username': 1,
        'datetime': 1,
        'conversation': 1,
    })
    if not gpt35t_context:
        return ServiceResponse(success=False, status_code=404, msg='GPT-3.5-TURBO Not Found')

    gpt35t_context = GPT35TContext.model_validate(gpt35t_context)
    return ServiceResponse(data={'gpt35t_context': gpt35t_context})


async def update_gpt35t_context(context_id: str, new_conversation: list[GPT35TMessage]) -> ServiceResponse:
    if len(new_conversation) == 0:
        return ServiceResponse(msg='OK')

    bson_id = validate_bson_id(context_id)
    if not bson_id:
        return ServiceResponse(success=False, msg='Bad Context ID', status_code=400)

    update_result = await get_database().get_collection('gpt35t_contexts').update_one({'_id': bson_id}, {
        '$set': {'conversation': [x.model_dump() for x in new_conversation]}
    })
    if update_result.modified_count != 1:
        return ServiceResponse(success=False, status_code=409, msg='Can not Update this Context')
    return ServiceResponse(msg='OK')
