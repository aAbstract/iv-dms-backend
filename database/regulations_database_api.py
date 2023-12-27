from models.runtime import ServiceResponse
from database.mongo_driver import get_database, validate_bson_id
from models.regulations import RegulationsMetaData


async def get_regulations_options() -> ServiceResponse:
    mdb_query = [
        {
            '$project': {
                'id': {'$toString': '$_id'},
                'type': 1,
                'name': 1,
            },
        },
    ]

    regulations_meta_data = await get_database().get_collection('regulations').aggregate(mdb_query).to_list(length=None)
    regulations_meta_data = [RegulationsMetaData.model_validate(x) for x in regulations_meta_data]
    return ServiceResponse(data={'regulations_options': regulations_meta_data})


async def get_regulation_codes(regulation_id: str) -> ServiceResponse:
    bson_id = validate_bson_id(regulation_id)
    if not bson_id:
        return ServiceResponse(success=False, msg='Bad Regulation ID', status_code=400)

    mdb_query = [
        {'$match': {'_id': bson_id}},
        {
            '$project': {
                'regulation_codes': {
                    '$map': {
                        'input': '$sections',
                        'as': 'section',
                        'in': {
                            'section_name': '$$section.name',
                            'section_code': '$$section.code',
                            'checklist_codes': {
                                '$map': {
                                    'input': '$$section.items',
                                    'as': 'item',
                                    'in': '$$item.code'
                                },
                            },
                        },
                    },
                },
            },
        },
        {
            '$project': {
                '_id': 0,
                'regulation_codes': 1,
            },
        },
    ]

    try:
        regulation_codes = await get_database().get_collection('regulations').aggregate(mdb_query).next()
    except:
        return ServiceResponse(success=False, msg='Regulation Codes not Found', status_code=404)

    return ServiceResponse(data=regulation_codes)
