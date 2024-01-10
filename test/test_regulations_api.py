import json
import requests
import _test_config


def test_get_options_api_lock():
    api_url = f"{_test_config.get_api_url()}/regulations/get-options"
    http_headers = {'X-Auth': 'Bearer fake_token'}
    http_res = requests.post(api_url, headers=http_headers)
    assert http_res.status_code == 403
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Unauthorized API Access [Invalid Token]')


def test_get_options_api_success():
    api_url = f"{_test_config.get_api_url()}/regulations/get-options"
    access_token = _test_config.login_user('cwael', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'X-Auth': f"Bearer {access_token}"}
    http_res = requests.post(api_url, headers=http_headers)
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'regulations_options' in json_res_body['data']
    if len(json_res_body['data']['regulations_options']) > 0:
        regulations_option = json_res_body['data']['regulations_options'][0]
        obj_keys = set(regulations_option.keys())
        assert obj_keys == {'id', 'type', 'name'}


def test_get_codes_api_lock():
    api_url = f"{_test_config.get_api_url()}/regulations/get-codes"
    http_headers = {'X-Auth': 'Bearer fake_token'}
    http_res = requests.post(api_url, headers=http_headers, json={'regulation_id': '000000000000000000000000'})
    assert http_res.status_code == 403
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Unauthorized API Access [Invalid Token]')


def test_get_codes_api_regulation_not_found():
    api_url = f"{_test_config.get_api_url()}/regulations/get-codes"
    access_token = _test_config.login_user('cwael', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'X-Auth': f"Bearer {access_token}"}
    http_res = requests.post(api_url, headers=http_headers, json={'regulation_id': '000000000000000000000000'})
    assert http_res.status_code == 404
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Regulation Codes not Found')


def test_get_codes_api_success():
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

    # get codes
    api_url = f"{_test_config.get_api_url()}/regulations/get-codes"
    http_res = requests.post(api_url, headers=http_headers, json={'regulation_id': regulation_id})
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert 'regulation_codes' in json_res_body['data']
    if len(json_res_body['data']['regulation_codes']) > 0:
        regulation_codes = json_res_body['data']['regulation_codes'][0]
        obj_keys = set(regulation_codes)
        assert obj_keys == {'section_name', 'section_code', 'checklist_codes'}


def test_get_checklist_code_iosa_map_api_lock():
    api_url = f"{_test_config.get_api_url()}/regulations/get-iosa-map"
    http_headers = {'X-Auth': 'Bearer fake_token'}
    http_res = requests.post(api_url, headers=http_headers, json={
        'regulation_id': '000000000000000000000000',
        'checklist_code': 'XXX 0.0.0',
    })
    assert http_res.status_code == 403
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Unauthorized API Access [Invalid Token]')


def test_get_checklist_code_iosa_map_api_success():
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

    # get iosa map
    api_url = f"{_test_config.get_api_url()}/regulations/get-iosa-map"
    http_res = requests.post(api_url, headers=http_headers, json={
        'regulation_id': regulation_id,
        'checklist_code': 'FLT 1.3.4',
    })
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert 'iosa_map' in json_res_body['data']


def test_get_iosa_checklist_api_lock():
    api_url = f"{_test_config.get_api_url()}/regulations/get-iosa-checklist"
    http_headers = {'X-Auth': 'Bearer fake_token'}
    http_res = requests.post(api_url, headers=http_headers, json={
        'regulation_id': '000000000000000000000000',
        'checklist_code': 'XXX 0.0.0',
    })
    assert http_res.status_code == 403
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Unauthorized API Access [Invalid Token]')


def test_get_iosa_checklist_api_sucess():
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

    # get iosa checklist not found
    api_url = f"{_test_config.get_api_url()}/regulations/get-iosa-checklist"
    http_res = requests.post(api_url, headers=http_headers, json={
        'regulation_id': regulation_id,
        'checklist_code': 'FLT 0.0.0',
    })
    assert http_res.status_code == 404
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Checklist Code not Found')

    # get iosa checklist
    http_res = requests.post(api_url, headers=http_headers, json={
        'regulation_id': regulation_id,
        'checklist_code': 'FLT 1.3.4',
    })
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert 'iosa_checklist' in json_res_body['data']
    obj_keys = set(json_res_body['data']['iosa_checklist'])
    assert obj_keys == {'constraints', 'iosa_map', 'guidance', 'code', 'paragraph'}
