from models.runtime import ServiceResponse
from database.mongo_driver import get_database
from bson import ObjectId
from models.manuals import UnstructuredManual
from models.httpio import UnstructuredManualMetaData


def _validate_bson_id(manual_id) -> ObjectId | None:
    try:
        return ObjectId(manual_id)
    except:
        return None


async def get_manual_page(manual_id: str, page_order: int) -> ServiceResponse:
    bson_id = _validate_bson_id(manual_id)
    if not bson_id:
        return ServiceResponse(success=False, msg='Bad Manual ID', status_code=400)

    manual = await get_database().get_collection('unstructured_manuals').find_one({'_id': ObjectId(manual_id)})
    if not manual:
        return ServiceResponse(success=False, msg='Manual not Found', status_code=404)

    manual = UnstructuredManual.model_validate(manual)
    return ServiceResponse(data={'page': manual.pages[page_order]})


async def get_manual_meta_data(manual_id: str) -> ServiceResponse:
    bson_id = _validate_bson_id(manual_id)
    if not bson_id:
        return ServiceResponse(success=False, msg='Bad Manual ID', status_code=400)

    mdb_query = [
        {'$match': {'_id': bson_id}},
        {
            '$project': {
                '_id': 1,
                'name': 1,
                'page_count': {'$size': '$pages'},
            },
        },
    ]

    manual_meta_data = await get_database().get_collection('unstructured_manuals').aggregate(mdb_query).next()
    if not manual_meta_data:
        return ServiceResponse(success=False, msg='Can not Get Manual Meta Data', status_code=404)

    manual_meta_data = UnstructuredManualMetaData.model_validate(manual_meta_data)
    return ServiceResponse(data={'manual_meta_data': manual_meta_data})
