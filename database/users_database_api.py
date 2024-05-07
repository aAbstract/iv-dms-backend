import lib.crypto as crypto_man
from models.runtime import ServiceResponse
from database.mongo_driver import get_database, validate_bson_id
from models.users import User, UserRole
import re
from models.gpt_35t import LLMCostRate
from bson import ObjectId

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

    # check airline user enabled
    if user.user_role == UserRole.AIRLINES:
        if user.is_disabled:
            return ServiceResponse(success=False, msg='Login Failed, Airline User Is Disabled', status_code=403)
         
        # create jwt token
        jwt_token = crypto_man.create_jwt_token({
            'username': user.username,
            'display_name': user.disp_name,
            'role': user.user_role,
            'organization': user.organization,
            'airline': user.airline
        })
    else:   
        # create jwt token
        jwt_token = crypto_man.create_jwt_token({
            'username': user.username,
            'display_name': user.disp_name,
            'role': user.user_role,
            'organization': user.organization,
        })
    return ServiceResponse(data={'access_token': jwt_token})


async def create_airline_user_db(username: str, disp_name: str, email: str, phone_number: str, password: str, airline_id: str, organization: str) -> ServiceResponse:
    
    # Validate Airline
    airline_id = validate_bson_id(airline_id)
    if not airline_id:
        return ServiceResponse(success=False, msg="Bad Airline ID", status_code=400)

    airline = await get_database().get_collection("airlines").find_one({"_id": airline_id})

    if not airline:
        return ServiceResponse(
            success=False, msg="This airline ID doesn't exist", status_code=404
        )

    if airline['organization'] != organization:
        return ServiceResponse(
            success=False, msg="Your organization can't access this airline", status_code=403
        )

    # Checks if a user already exists for this airline
    airline_user = await get_database().get_collection("users").find_one({"organization": organization, "airline": str(airline['_id']), 'deleted':False})

    if airline_user:
        return ServiceResponse(
            success=False, msg="An Airline User already exists for this Airline", status_code=400
        )

    # Validate User Credentials
    user = await get_database().get_collection("users").find_one({"username": username})

    if user:
        return ServiceResponse(
            success=False, msg="This Username Already Exists", status_code=400
        )

    if not disp_name:
        return ServiceResponse(
            success=False, msg="Can't have an empty Display Name", status_code=400
        )

    if not re.match(r"\+?[1-9][0-9]{7,14}", phone_number):
        return ServiceResponse(
            success=False, msg="Invalid Phone Number", status_code=400
        )

    if not password:
        return ServiceResponse(
            success=False, msg="Can't have an empty password", status_code=400
        )

    # Create User
    password_hash = crypto_man.hash_password(password)

    user = User(
        username=username,
        disp_name=disp_name,
        pass_hash=password_hash,
        user_role=UserRole.AIRLINES,
        phone_number=phone_number,
        email=email,
        organization=organization,
        airline=str(airline_id),
        is_disabled=False,
        input_token_count=0,
        output_token_count=0,
        request_count=0,
    )

    user = user.model_dump()

    user = await get_database().get_collection("users").insert_one(user)

    if not user:
        return ServiceResponse(
            success=False, msg="Failed to Create User", status_code=500
        )
    
    user_id = str(user.inserted_id)
  
    return ServiceResponse(data = {"_id":user_id})


async def reset_airline_user_password_db(user_id: str, new_password: str, organization: str) -> ServiceResponse:

    # Validate User
    user_id = validate_bson_id(user_id)
    if not user_id:
        return ServiceResponse(success=False, msg="Bad Airline ID", status_code=400)
    
    user = await get_database().get_collection("users").find_one({"_id": user_id})

    if not user:
        return ServiceResponse(
            success=False, msg="This Username Doesn't Exist", status_code=404
        )

    if user['organization'] != organization:
        return ServiceResponse(
            success=False, msg="Your organization can't access this airline user", status_code=403
        )

    if user['user_role'] != UserRole.AIRLINES:
        return ServiceResponse(
            success=False, msg="Can't Rest a non-airline user's Password", status_code=400
        )

    if not new_password:
        return ServiceResponse(
            success=False, msg="Can't have an empty password", status_code=400
        )

    new_password = crypto_man.hash_password(new_password)

    user = await get_database().get_collection("users").update_one({"_id": user['_id']}, {'$set': {"pass_hash": new_password}})

    if not user.acknowledged:
        return ServiceResponse(
            success=False, msg="Failed to Change Password", status_code=500
        )

    return ServiceResponse()


async def toggle_airline_user_db(user_id: str, organization: str) -> ServiceResponse:

    # Validate User
    user_id = validate_bson_id(user_id)
    if not user_id:
        return ServiceResponse(success=False, msg="Bad Airline ID", status_code=400)
    
    user = await get_database().get_collection("users").find_one({"_id": user_id})

    if not user:
        return ServiceResponse(
            success=False, msg="This Username Doesn't Exist", status_code=404
        )

    if user['organization'] != organization:
        return ServiceResponse(
            success=False, msg="Your organization can't access this airline user", status_code=403
        )

    if user['user_role'] != UserRole.AIRLINES:
        return ServiceResponse(
            success=False, msg="Can't Disable a non-airline user", status_code=400
        )

    db_response = await get_database().get_collection("users").update_one({"_id": user['_id']}, {"$set": {"is_disabled": not user['is_disabled']}})

    if not db_response.acknowledged:
        return ServiceResponse(
            success=False, msg="Failed to Toggle Airline User's Disability", status_code=500
        )

    return ServiceResponse(data={"is_disabled": (not user['is_disabled'])})


async def delete_airline_user_db(user_id: str, organization: str) -> ServiceResponse:
    
    # Validate User
    user_id = validate_bson_id(user_id)
    if not user_id:
        return ServiceResponse(success=False, msg="Bad Airline ID", status_code=400)
    
    user = await get_database().get_collection("users").find_one({"_id": user_id})

    if not user:
        return ServiceResponse(
            success=False, msg="This Username Doesn't Exist", status_code=404
        )

    if user['organization'] != organization:
        return ServiceResponse(
            success=False, msg="Your organization can't access this airline user", status_code=403
        )

    if user['user_role'] != UserRole.AIRLINES:
        return ServiceResponse(
            success=False, msg="Can't Delete a non-airline user", status_code=400
        )

    user_ack = await get_database().get_collection("users").delete_one({"_id": user['_id']})
    airline_ack = await get_database().get_collection("airlines").update_one({"_id": ObjectId(user['airline'])},{"$set":{"deleted":True}})

    if not (user_ack.acknowledged and airline_ack.acknowledged):
        return ServiceResponse(
            success=False, msg="Failed to Delete Airline User", status_code=500
        )

    return ServiceResponse()


async def get_airline_users_table(organization: str) -> ServiceResponse:

    # Get All Airline Users
    airline_users = [
        user
        async for user in get_database()
        .get_collection("users")
        .find( {"organization": organization,'user_role':UserRole.AIRLINES},{"_id":1,"username":1,"airline": 1,"input_token_count":1,"output_token_count":1,"request_count":1,"is_disabled":1})
    ]
    
    for airline_user in airline_users:    
        airline_user["_id"] = str(airline_user["_id"])
        airline_user['manual_count'] = await get_database().get_collection("fs_index").count_documents({"airline": str(airline_user['airline'])})
        airline_user['cost'] = (airline_user['input_token_count'] * LLMCostRate.ANTHROPIC_INPUT.value) +  (airline_user['output_token_count'] * LLMCostRate.ANTHROPIC_OUTPUT.value) 
        airline_user['tokens'] = airline_user['input_token_count'] + airline_user['output_token_count']
        airline = await get_database().get_collection("airlines").find_one({"_id": ObjectId(airline_user['airline'])})
        airline_user['username'] = airline['name']
        
        del airline_user['input_token_count']
        del airline_user['output_token_count']
        del airline_user['airline']

    return ServiceResponse(data = {"airlines":airline_users})
