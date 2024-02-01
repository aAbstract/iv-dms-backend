import json
import requests
import _test_config
from models.users import User

LLM_SCORE_TH = 0.15


def test_llm_api_lock():
    api_url = f"{_test_config.get_api_url()}/llm/iosa-audit"
    http_headers = {'X-Auth': 'Bearer fake_token'}
    http_res = requests.post(api_url, headers=http_headers, json={
        'regulation_id': '000000000000000000000000',
        'checklist_code': 'XXX 0.0.0',
        'text': 'some text',
    })
    assert http_res.status_code == 403
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Unauthorized API Access [Invalid Token]')


def test_llm_api_success():
    access_token = _test_config.login_user('cwael', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'X-Auth': f"Bearer {access_token}"}

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
    assert obj_keys == {'score_tag', 'details', 'score_text', 'comments', 'suggestions', 'modified', 'score', 'pct_score'}
    
    # reset user    
    get_database = _test_config.get_database() 
    assert get_database != None

    user = get_database["users"].find_one({"username": 'cwael'})

    user = User.model_validate(user).model_dump()

    gemini_audits = user['activity']['gemini_audits']
    user['activity']['gemini_audits'] -= 1
    get_database["users"].update_one({"username": "cwael"},{"$set": user})

    user = get_database["users"].find_one({"username": "cwael"})

    user = User.model_validate(user).model_dump()

    assert user['activity']['gemini_audits'] == (gemini_audits - 1)


def test_llm_api_success_low_score():
    access_token = _test_config.login_user('cwael', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'X-Auth': f"Bearer {access_token}"}

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
        'text': _test_config.dummy_prompt,
    })
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert 'llm_resp' in json_res_body['data']
    obj_keys = set(json_res_body['data']['llm_resp'])
    assert obj_keys == {'score_tag', 'details', 'score_text', 'comments', 'suggestions', 'modified', 'score', 'pct_score'}
    assert json_res_body['data']['llm_resp']['pct_score'] < LLM_SCORE_TH


def test_llm_api_success_high_score():
    access_token = _test_config.login_user('cwael', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'X-Auth': f"Bearer {access_token}"}

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
        'checklist_code': 'FLT 3.1.1',
        'text': _test_config.valid_prompt,
    })
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert 'llm_resp' in json_res_body['data']
    obj_keys = set(json_res_body['data']['llm_resp'])
    assert obj_keys == {'score_tag', 'details', 'score_text', 'comments', 'suggestions', 'modified', 'score', 'pct_score'}
    assert json_res_body['data']['llm_resp']['pct_score'] > (1 - LLM_SCORE_TH)
