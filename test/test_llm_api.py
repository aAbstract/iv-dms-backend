import json
import requests
import os
from bson import ObjectId
import _test_config


LLM_SCORE_TH = 0.4


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


def test_llm_unstruct_api_success_high_score():
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

    # call audit llm api
    api_url = f"{_test_config.get_api_url()}/llm/iosa-audit-unstruct"
    http_res = requests.post(api_url, headers=http_headers, json={
        'regulation_id': regulation_id,
        'checklist_code': 'FLT 3.1.1',
        'text': _test_config.valid_prompt,
    })
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert 'llm_resp' in json_res_body['data']
    assert 'overall_compliance_score' in json_res_body['data']
    assert 'context_id' in json_res_body['data']
    assert json_res_body['data']['overall_compliance_score'] > ((1 - LLM_SCORE_TH) * 100)
    old_ocs = json_res_body['data']['overall_compliance_score']

    # call enhance llm api
    api_url = f"{_test_config.get_api_url()}/llm/iosa-enhance-unstruct"
    context_id = json_res_body['data']['context_id']
    http_res = requests.post(api_url, headers=http_headers, json={'context_id': context_id})
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert 'llm_resp' in json_res_body['data']
    assert 'new_compliance_score' in json_res_body['data']
    assert 'context_id' in json_res_body['data']
    new_ocs = json_res_body['data']['new_compliance_score']
    assert new_ocs > old_ocs

    # TODO-LATER: delete gpt35t context
    # TODO-LATER: validate gpt35t context structure

def test_llm_pages_api_success():
    admin_access_token = _test_config.login_user('eslam', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'X-Auth': f"Bearer {admin_access_token}"}
    get_database = _test_config.get_database()
    assert get_database != None

    # get regulations options
    api_url = f"{_test_config.get_api_url()}/regulations/get-options"
    http_res = requests.post(api_url, headers=http_headers)
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'regulations_options' in json_res_body['data']
    regulation_id = [x for x in json_res_body['data']['regulations_options'] if x['name'] == 'IOSA Standards Manual (ISM) Ed 16-Revision2'][0]['id']

    # get file
    file = get_database['fs_index'].find_one({"filename":"nesma_OMA.pdf"})
    assert file['doc_uuid']

    # call llm api
    api_url = f"{_test_config.get_api_url()}/llm/iosa-audit-pages"
    http_res = requests.post(api_url, headers=http_headers, json={
        'regulation_id': regulation_id,
        'checklist_code': 'FLT 2.1.35',
        'pages': [1,2],
        'doc_uuid':file['doc_uuid']
    })

    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert 'llm_resp' in json_res_body['data']
    obj_keys = set(json_res_body['data']['llm_resp'])
    assert obj_keys == {'score_tag', 'details', 'score_text', 'comments', 'suggestions', 'modified', 'score', 'pct_score'}