from models.runtime import ServiceResponse
from database.mongo_driver import get_database, validate_bson_id
from models.manuals import UnstructuredManual, UnstructuredManualMetaData


async def get_manual_page(manual_id: str, page_order: int) -> ServiceResponse:
    bson_id = validate_bson_id(manual_id)
    if not bson_id:
        return ServiceResponse(success=False, msg='Bad Manual ID', status_code=400)

    manual = await get_database().get_collection('unstructured_manuals').find_one({'_id': bson_id})
    if not manual:
        return ServiceResponse(success=False, msg='Manual not Found', status_code=404)

    manual = UnstructuredManual.model_validate(manual)
    return ServiceResponse(data={'page': manual.pages[page_order]})


async def get_manual_meta_data(manual_id: str) -> ServiceResponse:
    bson_id = validate_bson_id(manual_id)
    if not bson_id:
        return ServiceResponse(success=False, msg='Bad Manual ID', status_code=400)

    mdb_query = [
        {'$match': {'_id': bson_id}},
        {
            '$project': {
                'id': {'$toString': '$_id'},
                'name': 1,
                'page_count': {'$size': '$pages'},
            },
        },
    ]

    try:
        manual_meta_data = await get_database().get_collection('unstructured_manuals').aggregate(mdb_query).next()
        manual_meta_data = UnstructuredManualMetaData.model_validate(manual_meta_data)
    except:
        return ServiceResponse(success=False, msg='Can not Get Manual Meta Data', status_code=404)

    return ServiceResponse(data={'manual_meta_data': manual_meta_data})


async def get_manuals_options() -> ServiceResponse:
    mdb_query = [
        {
            '$project': {
                'id': {'$toString': '$_id'},
                'name': 1,
                'page_count': {'$size': '$pages'},
            },
        },
    ]

    manuals_meta_data = await get_database().get_collection('unstructured_manuals').aggregate(mdb_query).to_list(length=None)
    manuals_meta_data = [UnstructuredManualMetaData.model_validate(x) for x in manuals_meta_data]
    return ServiceResponse(data={'manuals_options': manuals_meta_data})


async def create_unstructured_manual(unstructured_manual: UnstructuredManual):
    # check manual name duplicate
    manual = await get_database().get_collection('unstructured_manuals').find_one({'name': unstructured_manual.name})
    if manual:
        return ServiceResponse(success=False, msg='This Manual Already Exists', status_code=409)

    mdb_result = await get_database().get_collection('unstructured_manuals').insert_one(unstructured_manual.model_dump())
    manual_id = str(mdb_result.inserted_id)
    return ServiceResponse(data={'manual_id': manual_id})


async def delete_unstructured_manual(manual_id: str) -> ServiceResponse:
    bson_id = validate_bson_id(manual_id)
    if not bson_id:
        return ServiceResponse(success=False, msg='Bad Manual ID', status_code=400)

    result = await get_database().get_collection('unstructured_manuals').delete_one({'_id': bson_id})
    if not result.deleted_count:
        return ServiceResponse(success=False, status_code=404, msg='Manual not Found')
    return ServiceResponse(msg='OK')
