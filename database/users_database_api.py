import lib.crypto as crypto_man
from models.runtime import ServiceResponse
from database.mongo_driver import get_database
from models.users import User


async def login_user(username: str, password: str) -> ServiceResponse:
    # check user in database
    user = await get_database().get_collection('users').find_one({'username': username})
    if not user:
        return ServiceResponse(success=False, msg='Login Failed, Invalid User Credentials', status_code=401)

    # check password hash
    user = User.model_validate(user)
    password_hash = crypto_man.hash_password(password)
    if password_hash != user.pass_hash:
        return ServiceResponse(success=False, msg='Login Failed, Invalid User Credentials', status_code=401)

    # create jwt token
    jwt_token = crypto_man.create_jwt_token({
        'username': user.username,
        'role': user.user_role,
    })
    return ServiceResponse(data={'access_token': jwt_token})
