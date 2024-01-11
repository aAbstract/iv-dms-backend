from models.runtime import ServiceResponse
from database.mongo_driver import get_database, validate_bson_id
from models.regulations import RegulationsMetaData, IOSAItem, IOSASection


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


async def get_checklist_code_iosa_map(regulation_id: str, checklist_code: str) -> ServiceResponse:
    bson_id = validate_bson_id(regulation_id)
    if not bson_id:
        return ServiceResponse(success=False, msg='Bad Regulation ID', status_code=400)

    mdb_query = [
        {'$match': {'_id': bson_id}},
        {'$unwind': '$sections'},
        {'$unwind': '$sections.items'},
        {'$match': {'sections.items.code': checklist_code}},
        {'$project': {'_id': 0, 'iosa_map': '$sections.items.iosa_map'}},
    ]

    try:
        iosa_map = await get_database().get_collection('regulations').aggregate(mdb_query).next()
    except:
        return ServiceResponse(success=False, msg='Checklist Code not Found', status_code=404)

    return ServiceResponse(data=iosa_map)


async def get_iosa_checklist(regulation_id: str, checklist_code: str) -> ServiceResponse:
    bson_id = validate_bson_id(regulation_id)
    if not bson_id:
        return ServiceResponse(success=False, msg='Bad Regulation ID', status_code=400)

    mdb_query = [
        {'$match': {'_id': bson_id}},
        {'$unwind': '$sections'},
        {'$unwind': '$sections.items'},
        {'$match': {'sections.items.code': checklist_code}},
        {'$project': {
            '_id': 0,
            'iosa_checklist': '$sections.items',
        }},
    ]

    try:
        iosa_checklist = await get_database().get_collection('regulations').aggregate(mdb_query).next()
        iosa_checklist = IOSAItem.model_validate(iosa_checklist['iosa_checklist'])
    except:
        return ServiceResponse(success=False, msg='Checklist Code not Found', status_code=404)

    return ServiceResponse(data={'iosa_checklist': iosa_checklist})


async def get_checklist_template(regulation_id: str, checklist_template_code: str) -> ServiceResponse:
    bson_id = validate_bson_id(regulation_id)
    if not bson_id:
        return ServiceResponse(success=False, msg='Bad Regulation ID', status_code=400)

    if ' ' not in checklist_template_code:
        return ServiceResponse(success=False, msg='Bad Checklist Template Code', status_code=400)

    section_code = checklist_template_code.split(' ')[0]
    iosa_section = await get_database().get_collection('regulations').find_one({'_id': bson_id, 'sections.code': section_code}, projection={"_id": 0, "sections.$": 1})
    if not iosa_section:
        return ServiceResponse(success=False, msg='Regulation Checklist Code not Found', status_code=404)

    if len(iosa_section['sections']) > 1:
        return ServiceResponse(success=False, msg='Multiple Regulation Checklist Codes were Found', status_code=400)

    iosa_section = IOSASection.model_validate(iosa_section['sections'][0])
    return ServiceResponse(data={'checklist_template': iosa_section})
