from bson import ObjectId
import json
import requests
import _test_config
import os

def test_get_logs_lock():
    api_url = f"{_test_config.get_api_url()}/activity/get-logs"
    http_headers = {'X-Auth': 'Bearer fake_token'}
    http_res = requests.post(api_url, headers=http_headers, json={'limit': 10})
    assert http_res.status_code == 403
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Unauthorized API Access [Invalid Token]')

    user_access_token = _test_config.login_user('cwael', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'X-Auth': f"Bearer {user_access_token}"}
    http_res = requests.post(api_url, headers=http_headers, json={'limit': 10})
    assert http_res.status_code == 403
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Unauthorized API Access [Restricted Access]')


def test_get_logs():
    api_url = f"{_test_config.get_api_url()}/activity/get-logs"
    admin_access_token = _test_config.login_user('eslam', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'X-Auth': f"Bearer {admin_access_token}"}
    http_res = requests.post(api_url, headers=http_headers, json={'limit': 10})
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'logs' in json_res_body['data']
    logs = json_res_body['data']['logs']
    if len(logs) > 0:
        obj_keys = set(logs[0].keys())
        assert obj_keys == {'level', 'id', 'description', 'datetime', 'source'}

def test_llm_usage_increment_airline_user():

    # Avoid Costs
    if int(os.environ["ANTHROPIC_ENABLE"]):
        return
    
    # Log in
    admin_access_token = _test_config.login_user(
        "eslam", "CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV"
    )
    http_headers = {"X-Auth": f"Bearer {admin_access_token}"}
    
    # Get database
    get_database = _test_config.get_database()
    assert get_database != None

    # Create airline
    airline = get_database.get_collection("airlines").insert_one({"organization":"AeroSync","name":"AeroSync Test"})

    # Create airline User
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

    # Log in as Airline User
    admin_access_token = _test_config.login_user(
        "airline_user_test", "verysecurepassword"
    )
    http_headers = {"X-Auth": f"Bearer {admin_access_token}"}

    # Get Regulation ID
    api_url = f"{_test_config.get_api_url()}/regulations/get-options"
    http_res = requests.post(api_url, headers=http_headers)
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body["success"]
    assert "regulations_options" in json_res_body["data"]
    regulation_id = [
        x
        for x in json_res_body["data"]["regulations_options"]
        if x["name"] == "IOSA Standards Manual (ISM) Ed 16-Revision2"
    ][0]["id"]

    # Get File
    file_1 = get_database["fs_index"].find_one({"filename": "CASS Manual_18 Dec 23.pdf"})

    # call llm api
    api_url = f"{_test_config.get_api_url()}/llm/iosa-audit-pages"
    http_res = requests.post(
        api_url,
        headers=http_headers,
        json={
            "regulation_id": regulation_id,
            "checklist_code": "FLT 3.1.1",
            "text":"",
            "pagesMapper": {file_1["doc_uuid"]: ["1.2.2"]},
        },
    )

    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert "llm_resp" in json_res_body["data"]
    assert "overall_compliance_score" in json_res_body["data"]
    assert "context_id" in json_res_body["data"]

    # call llm api again
    api_url = f"{_test_config.get_api_url()}/llm/iosa-audit-pages"
    http_res = requests.post(
        api_url,
        headers=http_headers,
        json={
            "regulation_id": regulation_id,
            "checklist_code": "FLT 3.1.1",
            "text":"",
            "pagesMapper": {file_1["doc_uuid"]: ["1.2.2"]},
        },
    )

    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert "llm_resp" in json_res_body["data"]
    assert "overall_compliance_score" in json_res_body["data"]
    assert "context_id" in json_res_body["data"]

    new_user = get_database.get_collection("users").find_one({"username":"airline_user_test"})
    assert new_user['input_token_count'] == 400
    assert new_user['output_token_count'] == 1000
    assert new_user['request_count'] == 2

    # Clean Up
    get_database.get_collection("users").delete_one({"_id": new_user['_id']})
    get_database.get_collection("airlines").delete_one({"_id": airline.inserted_id})
    get_database.get_collection("gpt35t_contexts").find_one_and_delete(
        {"_id": ObjectId(json_res_body["data"]["context_id"])}
    )
