import json
import requests
import _test_config


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
    assert obj_keys == {'score_tag', 'details', 'score_text', 'comments', 'score', 'pct_score'}
