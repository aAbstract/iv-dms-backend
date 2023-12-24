import json
import requests
import _test_config


def test_parse_pdf_api_lock():
    api_url = f"{_test_config.get_api_url()}/manuals/parse-pdf"
    http_headers = {'Authorization': 'Bearer fake_token'}
    http_res = requests.post(api_url, headers=http_headers, files={'file': open('README.md', 'rb')})
    assert http_res.status_code == 403
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Unauthorized API Access [Invalid Token]')


def test_parse_pdf_api_success():
    admin_access_token = _test_config.login_user('cwael', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    api_url = f"{_test_config.get_api_url()}/manuals/parse-pdf"
    http_headers = {'Authorization': f"Bearer {admin_access_token}"}
    http_res = requests.post(api_url, headers=http_headers, files={'file': open('README.md', 'rb')})
    assert http_res.status_code == 200
    # TODO-GAMAL: write this unit test


def test_get_page_api_lock():
    api_url = f"{_test_config.get_api_url()}/manuals/get-page"
    http_headers = {'Authorization': 'Bearer fake_token'}
    http_res = requests.post(api_url, headers=http_headers, json={
        'manual_id': '65884d8ded1f27514efaa32e',
        'page_order': 0,
    })
    assert http_res.status_code == 403
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Unauthorized API Access [Invalid Token]')


def test_get_page_api_manual_not_found():
    api_url = f"{_test_config.get_api_url()}/manuals/get-page"
    admin_access_token = _test_config.login_user('cwael', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'Authorization': f"Bearer {admin_access_token}"}
    http_res = requests.post(api_url, headers=http_headers, json={
        'manual_id': '000000000000000000000000',
        'page_order': 0,
    })
    assert http_res.status_code == 404
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Manual not Found')

    http_res = requests.post(api_url, headers=http_headers, json={
        'manual_id': 'fake_id',
        'page_order': 0,
    })
    assert http_res.status_code == 400
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Bad Manual ID')


def test_get_page_api_success():
    api_url = f"{_test_config.get_api_url()}/manuals/get-page"
    admin_access_token = _test_config.login_user('cwael', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'Authorization': f"Bearer {admin_access_token}"}
    http_res = requests.post(api_url, headers=http_headers, json={
        'manual_id': '65884d8ded1f27514efaa32e',
        'page_order': 0,
    })
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'page' in json_res_body['data']


def test_get_meta_data_api_lock():
    api_url = f"{_test_config.get_api_url()}/manuals/get-meta-data"
    http_headers = {'Authorization': 'Bearer fake_token'}
    http_res = requests.post(api_url, headers=http_headers, json={'manual_id': '65884d8ded1f27514efaa32e'})
    assert http_res.status_code == 403
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Unauthorized API Access [Invalid Token]')


def test_get_meta_data_api_success():
    api_url = f"{_test_config.get_api_url()}/manuals/get-meta-data"
    admin_access_token = _test_config.login_user('cwael', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'Authorization': f"Bearer {admin_access_token}"}
    http_res = requests.post(api_url, headers=http_headers, json={'manual_id': '65884d8ded1f27514efaa32e'})
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'manual_meta_data' in json_res_body['data']
    manual_meta_data = json_res_body['data']['manual_meta_data']
    assert ('name' in manual_meta_data and 'page_count' in manual_meta_data)
