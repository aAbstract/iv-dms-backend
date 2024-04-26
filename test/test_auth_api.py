import requests
import json
import _test_config


def test_auth_api_login_failed_invalid_account():
    api_url = f"{_test_config.get_api_url()}/auth/login"
    http_res = requests.post(api_url, json={
        'username': 'fake_user',
        'password': 'fake_password',
    })
    assert http_res.status_code == 401
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Login Failed, Invalid User Credentials')


def test_auth_api_login_failed_invalid_password():
    api_url = f"{_test_config.get_api_url()}/auth/login"
    http_res = requests.post(api_url, json={
        'username': 'air_cairo',
        'password': 'fake_password',
    })
    assert http_res.status_code == 401
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Login Failed, Invalid User Credentials')


def test_auth_api_login_success():
    api_url = f"{_test_config.get_api_url()}/auth/login"
    http_res = requests.post(api_url, json={
        'username': 'cwael',
        'password': 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV',
    })
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'access_token' in json_res_body['data']

def test_auth_api_login_fail_airline_user():
    
    # Log in
    access_token = _test_config.login_user('eslam', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'X-Auth': f"Bearer {access_token}"}

    # Get Database
    get_database = _test_config.get_database()
    assert get_database != None

    # Create airline
    airline = get_database.get_collection("airlines").insert_one({"organization":"AeroSync","name":"AeroSync Test"})

    # Create Airline User
    api_url = f"{_test_config.get_api_url()}/users/create_airline_user"
    payload = {
        "phone_number":"+201234567890",
        "username":"airline_user_test",
        "disp_name":"airline_user_test",
        "email":"boombastic@hotmail.com",
        "password": "verysecurepassword",
        "airline_id":str(airline.inserted_id)
    }
    http_res = requests.post(api_url,headers=http_headers, json=payload)

    # Validate
    assert http_res.status_code == 200
    new_user = get_database.get_collection("users").find_one({"username":"airline_user_test"})
    assert new_user['phone_number'] == "+201234567890"
    assert new_user['email'] == "boombastic@hotmail.com"
    assert new_user['airline'] == str(airline.inserted_id)
    old_disabled = new_user['is_disabled']

    # Disable Airline User
    api_url = f"{_test_config.get_api_url()}/users/toggle_airline_user"
    payload = {
        "airline_username":"airline_user_test"
    }
    http_res = requests.post(api_url,headers=http_headers, json=payload)

    # Validate
    assert http_res.status_code == 200
    new_user = get_database.get_collection("users").find_one({"username":"airline_user_test"})
    assert new_user['is_disabled'] == (not old_disabled)
    
    # Call API
    api_url = f"{_test_config.get_api_url()}/auth/login"
    http_res = requests.post(api_url, json={
        'username': 'airline_user_test',
        'password': 'verysecurepassword',
    })
    assert http_res.status_code == 403
    json_res_body = json.loads(http_res.content.decode())
    assert not json_res_body['success']
    assert json_res_body['msg'] == 'Login Failed, Airline User Is Disabled'

    # Clean Up
    get_database.get_collection("airlines").delete_one({"_id": airline.inserted_id})
    get_database.get_collection("users").delete_one({"_id": new_user['_id']})