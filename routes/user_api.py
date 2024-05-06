import os
from fastapi import APIRouter, Response, Body, Header, Query
import lib.log as log_man
import database.users_database_api as users_database_api
from database.flow_report_database_api import create_airlines_db
from models.httpio import JsonResponse
from models.users import UserRole
import lib.security as security_man
from pydantic import EmailStr
from typing import Annotated


_ROOT_ROUTE = f"{os.getenv('API_ROOT')}/users"
_MODULE_ID = 'routes.user_api'
_ALLOWED_USERS = [UserRole.ADMIN]
router = APIRouter()


@router.post(f"{_ROOT_ROUTE}/create_airline_user")
async def create_airline_user(res: Response, phone_number: str =  Body(embed=True), username: str = Body(embed=True), disp_name: str = Body(embed=True), email: EmailStr = Body(embed=True), password: str = Body(embed=True), airline_name: str = Body(embed=True), x_auth=Header(alias="X-Auth", default=None)) -> JsonResponse:
    """
    Creates a new user with type airline
    """
    func_id = f"{_MODULE_ID}.create_airline_user"

    # authorize user
    auth_service_response = await security_man.authorize_api(
        x_auth, _ALLOWED_USERS, func_id
    )

    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    await log_man.add_log(
        func_id,
        "DEBUG",
        f"received create airline user request: username={auth_service_response.data['token_claims']['username']} organization={auth_service_response.data['token_claims']['organization']} airline_name = {airline_name}",
    )
    organization = auth_service_response.data["token_claims"]["organization"]


    db_service_response = await create_airlines_db(
        name = airline_name,
        organization=organization,
    )

    if not db_service_response.success:
        res.status_code = db_service_response.status_code
        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )

    db_service_response = await users_database_api.create_airline_user_db(username=username, disp_name=disp_name,email=email,phone_number=phone_number,password=password,airline_id=db_service_response.data['airline_id'],organization=organization)
    res.status_code = db_service_response.status_code

    if not db_service_response.success:

        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )

    return JsonResponse(data=db_service_response.data)

@router.post(f"{_ROOT_ROUTE}/reset_airline_user_password")
async def reset_airline_user_password(res: Response, id:str = Body(embed=True),new_password: str =Body(embed=True) , x_auth=Header(alias="X-Auth", default=None)) -> JsonResponse:
    """
    Resets the Password of an airline user, done by an admin user
    """
    func_id = f"{_MODULE_ID}.reset_airline_user_password"

    # authorize user
    auth_service_response = await security_man.authorize_api(
        x_auth, _ALLOWED_USERS, func_id
    )

    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    await log_man.add_log(
        func_id,
        "DEBUG",
        f"received reset airline user password request: username={auth_service_response.data['token_claims']['username']} organization={auth_service_response.data['token_claims']['organization']} airline user id= {id}",
    )

    organization = auth_service_response.data["token_claims"]["organization"]

    db_service_response = await users_database_api.reset_airline_user_password_db(user_id=id, new_password=new_password,organization=organization)
    res.status_code = db_service_response.status_code

    if not db_service_response.success:

        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )

    return JsonResponse(data=db_service_response.data)

@router.post(f"{_ROOT_ROUTE}/toggle_airline_user")
async def toggle_airline_user(res: Response, id:str = Body(embed=True), x_auth=Header(alias="X-Auth", default=None)) -> JsonResponse:
    """
    toggle the disablity of an airline user, done by an admin user
    """
    func_id = f"{_MODULE_ID}.toggle_airline_user"

    # authorize user
    auth_service_response = await security_man.authorize_api(
        x_auth, _ALLOWED_USERS, func_id
    )

    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    await log_man.add_log(
        func_id,
        "DEBUG",
        f"received toggle airline user request: username={auth_service_response.data['token_claims']['username']} organization={auth_service_response.data['token_claims']['organization']} airline user id= {id}",
    )

    organization = auth_service_response.data["token_claims"]["organization"]

    db_service_response = await users_database_api.toggle_airline_user_db(user_id=id,organization=organization)
    res.status_code = db_service_response.status_code

    if not db_service_response.success:

        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )

    return JsonResponse(data=db_service_response.data)

@router.post(f"{_ROOT_ROUTE}/delete_airline_user")
async def delete_airline_user(res: Response, id:str = Body(embed=True), x_auth=Header(alias="X-Auth", default=None)) -> JsonResponse:
    """
    Deletsan airline user, done by an admin user
    """
    func_id = f"{_MODULE_ID}.delete_airline_user"

    # authorize user
    auth_service_response = await security_man.authorize_api(
        x_auth, _ALLOWED_USERS, func_id
    )

    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    await log_man.add_log(
        func_id,
        "DEBUG",
        f"received delete airline user  request: username={auth_service_response.data['token_claims']['username']} organization={auth_service_response.data['token_claims']['organization']} airline user id= {id}",
    )

    organization = auth_service_response.data["token_claims"]["organization"]

    db_service_response = await users_database_api.delete_airline_user_db(user_id=id,organization=organization)
    res.status_code = db_service_response.status_code

    if not db_service_response.success:

        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )

    return JsonResponse(data=db_service_response.data)

@router.post(f"{_ROOT_ROUTE}/get_airline_users_table")
async def get_airline_users_table(res: Response, x_auth=Header(alias="X-Auth", default=None)) -> JsonResponse:
    """
    Get the usage table of all airline users in an organization, done by an admin
    """
    func_id = f"{_MODULE_ID}.get_airline_users_table"

    # authorize user
    auth_service_response = await security_man.authorize_api(
        x_auth, _ALLOWED_USERS, func_id
    )

    if not auth_service_response.success:
        res.status_code = auth_service_response.status_code
        return JsonResponse(
            success=auth_service_response.success,
            msg=auth_service_response.msg,
        )

    await log_man.add_log(
        func_id,
        "DEBUG",
        f"received get airline users table  request: username={auth_service_response.data['token_claims']['username']} organization={auth_service_response.data['token_claims']['organization']}",
    )

    organization = auth_service_response.data["token_claims"]["organization"]

    db_service_response = await users_database_api.get_airline_users_table(organization=organization)
    res.status_code = db_service_response.status_code

    if not db_service_response.success:

        return JsonResponse(
            success=db_service_response.success,
            msg=db_service_response.msg,
        )

    return JsonResponse(data=db_service_response.data)