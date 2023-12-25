from models.runtime import ServiceResponse
from database.mongo_driver import get_database
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
