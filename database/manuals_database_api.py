from models.runtime import ServiceResponse
from database.mongo_driver import get_database
from bson import ObjectId
from models.manuals import UnstructuredManual


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
