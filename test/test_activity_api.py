import json
import requests
import _test_config
from models.users import User

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

def test_get_user_activity():
    api_url = f"{_test_config.get_api_url()}/activity/get-user-activity"
    admin_access_token = _test_config.login_user('eslam', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'X-Auth': f"Bearer {admin_access_token}"}
    http_res = requests.post(api_url, headers=http_headers)
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'activity' in json_res_body['data']
    activity = json_res_body['data']['activity']
    obj_keys = set(activity.keys())
    assert obj_keys == {'gemini_audits', 'chatdoc_parse_docs', 'chatdoc_check_docs', 'chatdoc_scan_docs'}

def test_increment_gemini_user_activity():
    username = 'eslam'
    # login info
    admin_access_token = _test_config.login_user(username, 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'X-Auth': f"Bearer {admin_access_token}"}

    # get activity before increment
    api_url = f"{_test_config.get_api_url()}/activity/get-user-activity"
    http_res = requests.post(api_url, headers=http_headers)
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'activity' in json_res_body['data']
    activity = json_res_body['data']['activity']
    obj_keys = set(activity.keys())
    assert obj_keys == {'gemini_audits', 'chatdoc_parse_docs', 'chatdoc_check_docs', 'chatdoc_scan_docs'}
    before_gemini_audits = activity['gemini_audits']
    before_chatdoc_parse_docs = activity['chatdoc_parse_docs']
    before_chatdoc_check_docs = activity['chatdoc_check_docs']
    before_chatdoc_scan_docs = activity['chatdoc_scan_docs']
    
    # get regulations options
    api_url = f"{_test_config.get_api_url()}/regulations/get-options"
    http_res = requests.post(api_url, headers=http_headers)
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'regulations_options' in json_res_body['data']
    regulation_id = [x for x in json_res_body['data']['regulations_options'] if x['name'] == 'IOSA Standards Manual (ISM) Ed 16-Revision2'][0]['id']

    # call llm api
    api_url = f"{_test_config.get_api_url()}/llm/iosa-audit"
    http_res = requests.post(api_url, headers=http_headers, json={
        'regulation_id': regulation_id,
        'checklist_code': 'FLT 2.1.35',
        'text': _test_config.example_prompt,
    })
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert 'llm_resp' in json_res_body['data']
    obj_keys = set(json_res_body['data']['llm_resp'])

    assert obj_keys == {'details','modified','comments','suggestions','pct_score', 'score', 'score_tag', 'score_text'}

    # get activity after increment
    api_url = f"{_test_config.get_api_url()}/activity/get-user-activity"
    http_res = requests.post(api_url, headers=http_headers)
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'activity' in json_res_body['data']
    activity = json_res_body['data']['activity']
    obj_keys = set(activity.keys())
    assert obj_keys == {'gemini_audits', 'chatdoc_parse_docs', 'chatdoc_check_docs', 'chatdoc_scan_docs'}
    
    after_gemini_audits = activity['gemini_audits']
    after_chatdoc_parse_docs = activity['chatdoc_parse_docs']
    after_chatdoc_check_docs = activity['chatdoc_check_docs']
    after_chatdoc_scan_docs = activity['chatdoc_scan_docs']

    # check increment
    assert (before_gemini_audits + 1) == after_gemini_audits
    assert before_chatdoc_check_docs == after_chatdoc_check_docs
    assert before_chatdoc_parse_docs == after_chatdoc_parse_docs
    assert before_chatdoc_scan_docs == after_chatdoc_scan_docs    


    # reset user    
    get_database = _test_config.get_database() 
    assert get_database != None

    user = get_database["users"].find_one({"username": username})

    user = User.model_validate(user).model_dump()

    user['activity']['gemini_audits'] = before_gemini_audits
    get_database["users"].update_one({"username": username},{"$set": user})

    user = get_database["users"].find_one({"username": username})

    user = User.model_validate(user).model_dump()

    assert user['activity']['gemini_audits'] == before_gemini_audits

def test_increment_chatdoc_parse_user_activity():
    
    username = 'eslam'
    # login info
    admin_access_token = _test_config.login_user(username, 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'X-Auth': f"Bearer {admin_access_token}"}

    # get activity before increment
    api_url = f"{_test_config.get_api_url()}/activity/get-user-activity"
    http_res = requests.post(api_url, headers=http_headers)
    print(http_res.text)
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'activity' in json_res_body['data']
    activity = json_res_body['data']['activity']
    obj_keys = set(activity.keys())
    assert obj_keys == {'gemini_audits', 'chatdoc_parse_docs', 'chatdoc_check_docs', 'chatdoc_scan_docs'}
    before_gemini_audits = activity['gemini_audits']
    before_chatdoc_parse_docs = activity['chatdoc_parse_docs']
    before_chatdoc_check_docs = activity['chatdoc_check_docs']
    before_chatdoc_scan_docs = activity['chatdoc_scan_docs']



    # test parse doc
    api_url = f"{_test_config.get_api_url()}/manuals/parse-pdf"
    http_res = requests.post(api_url, headers=http_headers, files={'file': open('data/nesma_org_cos_rad.pdf', 'rb')})
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'doc_uuid' in json_res_body['data']

    # get activity after increment
    api_url = f"{_test_config.get_api_url()}/activity/get-user-activity"
    http_res = requests.post(api_url, headers=http_headers)
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'activity' in json_res_body['data']
    activity = json_res_body['data']['activity']
    obj_keys = set(activity.keys())
    assert obj_keys == {'gemini_audits', 'chatdoc_parse_docs', 'chatdoc_check_docs', 'chatdoc_scan_docs'}
    
    after_gemini_audits = activity['gemini_audits']
    after_chatdoc_parse_docs = activity['chatdoc_parse_docs']
    after_chatdoc_check_docs = activity['chatdoc_check_docs']
    after_chatdoc_scan_docs = activity['chatdoc_scan_docs']

    # check increment
    assert before_gemini_audits == after_gemini_audits
    assert before_chatdoc_check_docs == after_chatdoc_check_docs
    assert (before_chatdoc_parse_docs + 1) == after_chatdoc_parse_docs
    assert before_chatdoc_scan_docs == after_chatdoc_scan_docs    

    # reset user    
    get_database = _test_config.get_database() 
    assert get_database != None

    user = get_database["users"].find_one({"username": username})

    user = User.model_validate(user).model_dump()

    user['activity']['chatdoc_parse_docs'] = before_chatdoc_parse_docs
    get_database["users"].update_one({"username": username},{"$set": user})

    user = get_database["users"].find_one({"username": username})

    user = User.model_validate(user).model_dump()

    assert user['activity']['chatdoc_parse_docs'] == before_chatdoc_parse_docs

def test_increment_chatdoc_check_user_activity():
    
    username = 'eslam'
    # login info
    admin_access_token = _test_config.login_user(username, 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'X-Auth': f"Bearer {admin_access_token}"}

    # get activity before increment
    api_url = f"{_test_config.get_api_url()}/activity/get-user-activity"
    http_res = requests.post(api_url, headers=http_headers)
    print(http_res.text)
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'activity' in json_res_body['data']
    activity = json_res_body['data']['activity']
    obj_keys = set(activity.keys())
    assert obj_keys == {'gemini_audits', 'chatdoc_parse_docs', 'chatdoc_check_docs', 'chatdoc_scan_docs'}
    before_gemini_audits = activity['gemini_audits']
    before_chatdoc_parse_docs = activity['chatdoc_parse_docs']
    before_chatdoc_check_docs = activity['chatdoc_check_docs']
    before_chatdoc_scan_docs = activity['chatdoc_scan_docs']


    # test parse doc
    api_url = f"{_test_config.get_api_url()}/manuals/parse-pdf"
    http_res = requests.post(api_url, headers=http_headers, files={'file': open('data/nesma_org_cos_rad.pdf', 'rb')})
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'doc_uuid' in json_res_body['data']

    # test check doc
    api_url = f"{_test_config.get_api_url()}/manuals/check-pdf"
    http_res = requests.post(api_url, headers=http_headers, json={'doc_uuid': json_res_body['data']['doc_uuid']})
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'chat_doc_status' in json_res_body['data']

    # get activity after increment
    api_url = f"{_test_config.get_api_url()}/activity/get-user-activity"
    http_res = requests.post(api_url, headers=http_headers)
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'activity' in json_res_body['data']
    activity = json_res_body['data']['activity']
    obj_keys = set(activity.keys())
    assert obj_keys == {'gemini_audits', 'chatdoc_parse_docs', 'chatdoc_check_docs', 'chatdoc_scan_docs'}
    
    after_gemini_audits = activity['gemini_audits']
    after_chatdoc_parse_docs = activity['chatdoc_parse_docs']
    after_chatdoc_check_docs = activity['chatdoc_check_docs']
    after_chatdoc_scan_docs = activity['chatdoc_scan_docs']

    # check increment
    assert before_gemini_audits == after_gemini_audits
    assert (before_chatdoc_check_docs + 1) == after_chatdoc_check_docs
    assert (before_chatdoc_parse_docs + 1) == after_chatdoc_parse_docs
    assert before_chatdoc_scan_docs == after_chatdoc_scan_docs    

    # reset user    
    get_database = _test_config.get_database() 
    assert get_database != None

    user = get_database["users"].find_one({"username": username})

    user = User.model_validate(user).model_dump()

    user['activity']['chatdoc_parse_docs'] = before_chatdoc_parse_docs
    user['activity']['chatdoc_check_docs'] = before_chatdoc_check_docs

    get_database["users"].update_one({"username": username},{"$set": user})

    user = get_database["users"].find_one({"username": username})

    user = User.model_validate(user).model_dump()

    assert user['activity']['chatdoc_parse_docs'] == before_chatdoc_parse_docs
    assert user['activity']['chatdoc_check_docs'] == before_chatdoc_check_docs

def test_increment_chatdoc_scan_user_activity():
    
    # login info
    username = 'eslam'
    admin_access_token = _test_config.login_user(username, 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'X-Auth': f"Bearer {admin_access_token}"}

    # get activity before increment
    api_url = f"{_test_config.get_api_url()}/activity/get-user-activity"
    http_res = requests.post(api_url, headers=http_headers)
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'activity' in json_res_body['data']
    activity = json_res_body['data']['activity']
    obj_keys = set(activity.keys())
    assert obj_keys == {'gemini_audits', 'chatdoc_parse_docs', 'chatdoc_check_docs', 'chatdoc_scan_docs'}
    before_gemini_audits = activity['gemini_audits']
    before_chatdoc_parse_docs = activity['chatdoc_parse_docs']
    before_chatdoc_check_docs = activity['chatdoc_check_docs']
    before_chatdoc_scan_docs = activity['chatdoc_scan_docs']


    # get regulations options
    api_url = f"{_test_config.get_api_url()}/regulations/get-options"
    http_res = requests.post(api_url, headers=http_headers)
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'regulations_options' in json_res_body['data']
    regulation_id = [x for x in json_res_body['data']['regulations_options'] if x['name'] == 'IOSA Standards Manual (ISM) Ed 16-Revision2'][0]['id']


    # test pdf AI scanner
    api_url = f"{_test_config.get_api_url()}/manuals/scan-pdf"
    http_res = requests.post(api_url, headers=http_headers, json={
        'regulation_id': regulation_id,
        'checklist_code': 'FLT 3.1.1',
        'doc_uuid': '4aa2d2c4-0355-413e-8a1b-a7f87cb85098',
    })
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    print(json_res_body['data'])
    # check this later eslam
    # todo
    # assert 'is_found' in json_res_body['data']

    # if json_res_body['data']['is_found']:
    #     assert 'text' in json_res_body['data']
    #     assert 'doc_ref' in json_res_body['data']


    # get activity after increment
    api_url = f"{_test_config.get_api_url()}/activity/get-user-activity"
    http_res = requests.post(api_url, headers=http_headers)
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'activity' in json_res_body['data']
    activity = json_res_body['data']['activity']
    obj_keys = set(activity.keys())
    assert obj_keys == {'gemini_audits', 'chatdoc_parse_docs', 'chatdoc_check_docs', 'chatdoc_scan_docs'}
    
    after_gemini_audits = activity['gemini_audits']
    after_chatdoc_parse_docs = activity['chatdoc_parse_docs']
    after_chatdoc_check_docs = activity['chatdoc_check_docs']
    after_chatdoc_scan_docs = activity['chatdoc_scan_docs']

    # check increment
    assert before_gemini_audits == after_gemini_audits
    assert before_chatdoc_check_docs == after_chatdoc_check_docs
    assert before_chatdoc_parse_docs == after_chatdoc_parse_docs
    assert (before_chatdoc_scan_docs + 1) == after_chatdoc_scan_docs    

    # reset user    
    get_database = _test_config.get_database() 
    assert get_database != None

    user = get_database["users"].find_one({"username": username})

    user = User.model_validate(user).model_dump()

    user['activity']['chatdoc_scan_docs'] = before_chatdoc_scan_docs
    get_database["users"].update_one({"username": username},{"$set": user})

    user = get_database["users"].find_one({"username": username})

    user = User.model_validate(user).model_dump()

    assert user['activity']['chatdoc_scan_docs'] == before_chatdoc_scan_docs