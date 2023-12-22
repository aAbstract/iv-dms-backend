import lib.crypto as crypto_man
from models.httpio import LoginRequest
from models.httpio import ServiceResponse
from database.mongo_driver import get_database
from models.users import User


async def login_user(login_req: LoginRequest) -> ServiceResponse:
    # check user in database
    user = await get_database().get_collection('users').find_one({'username': login_req.username})
    if not user:
        return ServiceResponse(success=False, msg='Login Failed, Invalid User Credentials', status_code=401)

    # check password hash
    user = User.parse_obj(user)
    password_hash = crypto_man.hash_password(login_req.password)
    if password_hash != user.pass_hash:
        return ServiceResponse(success=False, msg='Login Failed, Invalid User Credentials', status_code=401)

    # create jwt token
    jwt_token = crypto_man.create_jwt_token({
        'username': user.username,
        'role': user.user_role,
    })
    return ServiceResponse(data={'access_token': jwt_token})
