import requests
import json
import _test_config


def test_create_airline_user_lock():

    # Log in
    http_headers = {'X-Auth': 'Bearer fake_token'}

    # Get Database
    get_database = _test_config.get_database()
    assert get_database != None

    # Create airline
    airline = get_database.get_collection("airlines").insert_one(
        {"organization": "AeroSync", "name": "AeroSync Test"})

    # Call API
    api_url = f"{_test_config.get_api_url()}/users/create_airline_user"
    payload = {
        "phone_number": "+201234567890",
        "username": "airline_user_test",
        "disp_name": "airline_user_test",
        "email": "boombastic@hotmail.com",
        "password": "verysecurepassword",
        "airline_id": str(airline.inserted_id)
    }

    http_res = requests.post(api_url, json=payload)
    assert http_res.status_code == 401
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg']
            == 'Unauthorized API Access [Empty Authorization Header]')

    # Clean Up
    get_database.get_collection("airlines").delete_one(
        {"_id": airline.inserted_id})


def test_create_airline_user_lock_admin_role():

    # Log in
    access_token = _test_config.login_user(
        'cwael', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'X-Auth': f"Bearer {access_token}"}

    # Get Database
    get_database = _test_config.get_database()
    assert get_database != None

    # Create airline
    airline = get_database.get_collection("airlines").insert_one(
        {"organization": "AeroSync", "name": "AeroSync Test"})

    # Call API
    api_url = f"{_test_config.get_api_url()}/users/create_airline_user"
    payload = {
        "phone_number": "+201234567890",
        "username": "airline_user_test",
        "disp_name": "airline_user_test",
        "email": "boombastic@hotmail.com",
        "password": "verysecurepassword",
        "airline_id": str(airline.inserted_id)
    }

    http_res = requests.post(api_url, headers=http_headers, json=payload)
    assert http_res.status_code == 403
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg']
            == 'Unauthorized API Access [Restricted Access]')

    # Clean Up
    get_database.get_collection("airlines").delete_one(
        {"_id": airline.inserted_id})


def test_create_airline_user():

    # Log in
    access_token = _test_config.login_user(
        'eslam', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'X-Auth': f"Bearer {access_token}"}

    # Get Database
    get_database = _test_config.get_database()
    assert get_database != None

    # Create airline
    airline = get_database.get_collection("airlines").insert_one(
        {"organization": "AeroSync", "name": "AeroSync Test"})

    # Call API
    api_url = f"{_test_config.get_api_url()}/users/create_airline_user"
    payload = {
        "phone_number": "+201234567890",
        "username": "airline_user_test",
        "disp_name": "airline_user_test",
        "email": "boombastic@hotmail.com",
        "password": "verysecurepassword",
        "airline_id": str(airline.inserted_id)
    }
    http_res = requests.post(api_url, headers=http_headers, json=payload)

    # Validate
    assert http_res.status_code == 200
    new_user = get_database.get_collection(
        "users").find_one({"username": "airline_user_test"})
    assert new_user['phone_number'] == "+201234567890"
    assert new_user['email'] == "boombastic@hotmail.com"
    assert new_user['airline'] == str(airline.inserted_id)

    # Call API 2
    api_url = f"{_test_config.get_api_url()}/users/create_airline_user"
    payload = {
        "phone_number": "+201234567890",
        "username": "airline_user_test2",
        "disp_name": "airline_user_test2",
        "email": "boombastic2@hotmail.com",
        "password": "verysecurepassword",
        "airline_id": str(airline.inserted_id)
    }
    http_res = requests.post(api_url, headers=http_headers, json=payload)
    assert http_res.status_code == 400
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['msg'] == "An Airline User already exists for this Airline"

    # Clean Up
    get_database.get_collection("airlines").delete_one(
        {"_id": airline.inserted_id})
    get_database.get_collection("users").delete_one({"_id": new_user['_id']})


def test_reset_airline_user_password():

    # Log in
    access_token = _test_config.login_user(
        'eslam', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'X-Auth': f"Bearer {access_token}"}

    # Get Database
    get_database = _test_config.get_database()
    assert get_database != None

    # Create airline
    airline = get_database.get_collection("airlines").insert_one(
        {"organization": "AeroSync", "name": "AeroSync Test"})

    # Create Airline User
    api_url = f"{_test_config.get_api_url()}/users/create_airline_user"
    payload = {
        "phone_number": "+201234567890",
        "username": "airline_user_test",
        "disp_name": "airline_user_test",
        "email": "boombastic@hotmail.com",
        "password": "verysecurepassword",
        "airline_id": str(airline.inserted_id)
    }

    http_res = requests.post(api_url, headers=http_headers, json=payload)

    # Validate
    assert http_res.status_code == 200
    new_user = get_database.get_collection(
        "users").find_one({"username": "airline_user_test"})
    assert new_user['phone_number'] == "+201234567890"
    assert new_user['email'] == "boombastic@hotmail.com"
    assert new_user['airline'] == str(airline.inserted_id)
    assert _test_config.hash_password(
        "verysecurepassword") == new_user['pass_hash']

    # Call API
    api_url = f"{_test_config.get_api_url()}/users/reset_airline_user_password"
    payload = {
        "airline_username": "airline_user_test",
        "new_password": "notverysecurepassword"
    }
    http_res = requests.post(api_url, headers=http_headers, json=payload)

    # Validate
    assert http_res.status_code == 200
    new_user = get_database.get_collection(
        "users").find_one({"username": "airline_user_test"})
    assert new_user['phone_number'] == "+201234567890"
    assert new_user['email'] == "boombastic@hotmail.com"
    assert new_user['airline'] == str(airline.inserted_id)
    assert _test_config.hash_password(
        "notverysecurepassword") == new_user['pass_hash']

    # Clean Up
    get_database.get_collection("airlines").delete_one(
        {"_id": airline.inserted_id})
    get_database.get_collection("users").delete_one({"_id": new_user['_id']})


def test_delete_airline_user():

    # Log in
    access_token = _test_config.login_user(
        'eslam', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'X-Auth': f"Bearer {access_token}"}

    # Get Database
    get_database = _test_config.get_database()
    assert get_database != None

    # Create airline
    airline = get_database.get_collection("airlines").insert_one(
        {"organization": "AeroSync", "name": "AeroSync Test"})

    # Create Airline User
    api_url = f"{_test_config.get_api_url()}/users/create_airline_user"
    payload = {
        "phone_number": "+201234567890",
        "username": "airline_user_test",
        "disp_name": "airline_user_test",
        "email": "boombastic@hotmail.com",
        "password": "verysecurepassword",
        "airline_id": str(airline.inserted_id)
    }
    http_res = requests.post(api_url, headers=http_headers, json=payload)

    # Validate
    assert http_res.status_code == 200
    new_user = get_database.get_collection(
        "users").find_one({"username": "airline_user_test"})
    assert new_user['phone_number'] == "+201234567890"
    assert new_user['email'] == "boombastic@hotmail.com"
    assert new_user['airline'] == str(airline.inserted_id)

    # Call API
    api_url = f"{_test_config.get_api_url()}/users/delete_airline_user"
    payload = {
        "airline_username": "airline_user_test"
    }
    http_res = requests.post(api_url, headers=http_headers, json=payload)

    # Validate
    assert http_res.status_code == 200
    new_user = get_database.get_collection(
        "users").find_one({"username": "airline_user_test"})
    assert new_user == None

    # Clean Up
    get_database.get_collection("airlines").delete_one(
        {"_id": airline.inserted_id})


def test_toggle_airline_user_disability():

    # Log in
    access_token = _test_config.login_user(
        'eslam', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'X-Auth': f"Bearer {access_token}"}

    # Get Database
    get_database = _test_config.get_database()
    assert get_database != None

    # Create airline
    airline = get_database.get_collection("airlines").insert_one(
        {"organization": "AeroSync", "name": "AeroSync Test"})

    # Create Airline User
    api_url = f"{_test_config.get_api_url()}/users/create_airline_user"
    payload = {
        "phone_number": "+201234567890",
        "username": "airline_user_test",
        "disp_name": "airline_user_test",
        "email": "boombastic@hotmail.com",
        "password": "verysecurepassword",
        "airline_id": str(airline.inserted_id)
    }
    http_res = requests.post(api_url, headers=http_headers, json=payload)

    # Validate
    assert http_res.status_code == 200
    new_user = get_database.get_collection(
        "users").find_one({"username": "airline_user_test"})
    assert new_user['phone_number'] == "+201234567890"
    assert new_user['email'] == "boombastic@hotmail.com"
    assert new_user['airline'] == str(airline.inserted_id)
    old_disabled = new_user['is_disabled']

    # Call API
    api_url = f"{_test_config.get_api_url()}/users/toggle_airline_user"
    payload = {
        "airline_username": "airline_user_test"
    }
    http_res = requests.post(api_url, headers=http_headers, json=payload)

    # Validate
    assert http_res.status_code == 200
    new_user = get_database.get_collection(
        "users").find_one({"username": "airline_user_test"})
    assert new_user['is_disabled'] == (not old_disabled)

    # Clean Up
    get_database.get_collection("airlines").delete_one(
        {"_id": airline.inserted_id})
    get_database.get_collection("users").delete_one({"_id": new_user['_id']})


def test_get_airline_user_usage_table():

    # Log in
    access_token = _test_config.login_user(
        'eslam', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'X-Auth': f"Bearer {access_token}"}

    # Get Database
    get_database = _test_config.get_database()
    assert get_database != None

    # Create airline
    airline = get_database.get_collection("airlines").insert_one(
        {"organization": "AeroSync", "name": "AeroSync Test"})

    # Create Airline User
    api_url = f"{_test_config.get_api_url()}/users/create_airline_user"
    payload = {
        "phone_number": "+201234567890",
        "username": "airline_user_test",
        "disp_name": "airline_user_test",
        "email": "boombastic@hotmail.com",
        "password": "verysecurepassword",
        "airline_id": str(airline.inserted_id)
    }
    http_res = requests.post(api_url, headers=http_headers, json=payload)

    # Validate
    assert http_res.status_code == 200
    new_user = get_database.get_collection(
        "users").find_one({"username": "airline_user_test"})
    assert new_user['phone_number'] == "+201234567890"
    assert new_user['email'] == "boombastic@hotmail.com"
    assert new_user['airline'] == str(airline.inserted_id)

    # Call API
    api_url = f"{_test_config.get_api_url()}/users/get_airline_users_table"
    payload = {
    }
    http_res = requests.post(api_url, headers=http_headers, json=payload)

    # Validate
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['data']['airlines']
    assert set(json_res_body['data']['airlines'][0]) == {"username",
                                                         "is_disabled",
                                                         "request_count",
                                                         "manual_count",
                                                         "cost",
                                                         "tokens",
                                                         "_id"}

    # Clean Up
    get_database.get_collection("airlines").delete_one(
        {"_id": airline.inserted_id})
    get_database.get_collection("users").delete_one({"_id": new_user['_id']})
