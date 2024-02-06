import lib.crypto as crypto_man
import lib.log as log_man
from models.runtime import ServiceResponse
from models.users import UserRole


def _parse_auth_token(auth: str) -> str:
    if 'Bearer' in auth:
        return auth.split(' ')[1]
    else:
        return auth


async def authorize_api(auth: str, allowed_roles: list[UserRole], func_id: str) -> ServiceResponse:
    if auth == None:
        err_msg = 'Unauthorized API Access [Empty Authorization Header]'
        await log_man.add_log(func_id, 'ERROR', err_msg)
        return ServiceResponse(success=False, msg=err_msg, status_code=401)

    # validate authorization header
    try:
        access_token = _parse_auth_token(auth)
        token_claims = crypto_man.decode_jwt_token(access_token)

    except:
        err_msg = 'Unauthorized API Access [Invalid Token]'
        await log_man.add_log(func_id, 'ERROR', err_msg)
        return ServiceResponse(success=False, msg=err_msg, status_code=403)

    # check logged in user
    if token_claims['role'] not in allowed_roles:
        err_msg = 'Unauthorized API Access [Restricted Access]'
        await log_man.add_log(func_id, 'ERROR', err_msg)
        return ServiceResponse(success=False, msg=err_msg, status_code=403)
    return ServiceResponse(data={'token_claims': token_claims})
