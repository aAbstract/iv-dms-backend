import json
import requests
import _test_config


def test_parse_pdf_api_lock():
    api_url = f"{_test_config.get_api_url()}/manuals/parse-pdf"
    http_headers = {'Authorization': 'Bearer fake_token'}
    http_res = requests.post(api_url, headers=http_headers, files={'file': open('temp/sample_manual.pdf', 'rb')})
    assert http_res.status_code == 403
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Unauthorized API Access [Invalid Token]')


def test_parse_pdf_api_success():
    # add manual
    access_token = _test_config.login_user('cwael', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    api_url = f"{_test_config.get_api_url()}/manuals/parse-pdf"
    http_headers = {'Authorization': f"Bearer {access_token}"}
    http_res = requests.post(api_url, headers=http_headers, files={'file': open('temp/sample_manual.pdf', 'rb')})
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'manual_id' in json_res_body['data']
    manual_id = json_res_body['data']['manual_id']

    # check manual exists
    http_res = requests.post(api_url, headers=http_headers, files={'file': open('temp/sample_manual.pdf', 'rb')})
    assert http_res.status_code == 403
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'This Manual Already Exists')

    # delete manual
    access_token = _test_config.login_user('eslam', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'Authorization': f"Bearer {access_token}"}
    api_url = f"{_test_config.get_api_url()}/manuals/delete-manual"
    http_res = requests.post(api_url, headers=http_headers, json={'manual_id': manual_id})
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert (json_res_body['success'] and json_res_body['msg'] == 'OK')

    # check manual is deleted
    http_res = requests.post(api_url, headers=http_headers, json={'manual_id': manual_id})
    assert http_res.status_code == 404
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Manual not Found')


def test_get_page_api_lock():
    api_url = f"{_test_config.get_api_url()}/manuals/get-page"
    http_headers = {'Authorization': 'Bearer fake_token'}
    http_res = requests.post(api_url, headers=http_headers, json={
        'manual_id': '000000000000000000000000',
        'page_order': 0,
    })
    assert http_res.status_code == 403
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Unauthorized API Access [Invalid Token]')


def test_get_page_api_manual_not_found():
    api_url = f"{_test_config.get_api_url()}/manuals/get-page"
    access_token = _test_config.login_user('cwael', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'Authorization': f"Bearer {access_token}"}
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
    access_token = _test_config.login_user('cwael', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'Authorization': f"Bearer {access_token}"}

    # get manuals options
    api_url = f"{_test_config.get_api_url()}/manuals/get-options"
    http_res = requests.post(api_url, headers=http_headers)
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'manuals_options' in json_res_body['data']
    example_manual = [x for x in json_res_body['data']['manuals_options'] if x['name'] == 'Example Manual 2'][0]
    assert ('name' in example_manual and 'page_count' in example_manual)

    # get manual page
    api_url = f"{_test_config.get_api_url()}/manuals/get-page"
    http_res = requests.post(api_url, headers=http_headers, json={
        'manual_id': example_manual['id'],
        'page_order': 0,
    })
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'page' in json_res_body['data']


def test_get_meta_data_api_lock():
    api_url = f"{_test_config.get_api_url()}/manuals/get-meta-data"
    http_headers = {'Authorization': 'Bearer fake_token'}
    http_res = requests.post(api_url, headers=http_headers, json={'manual_id': '000000000000000000000000'})
    assert http_res.status_code == 403
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Unauthorized API Access [Invalid Token]')


def test_get_meta_data_api_success():
    access_token = _test_config.login_user('cwael', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'Authorization': f"Bearer {access_token}"}

    # get manuals options
    api_url = f"{_test_config.get_api_url()}/manuals/get-options"
    http_res = requests.post(api_url, headers=http_headers)
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'manuals_options' in json_res_body['data']
    example_manual = [x for x in json_res_body['data']['manuals_options'] if x['name'] == 'Example Manual 2'][0]
    assert ('name' in example_manual and 'page_count' in example_manual)

    # get manual meta data
    api_url = f"{_test_config.get_api_url()}/manuals/get-meta-data"
    http_res = requests.post(api_url, headers=http_headers, json={'manual_id': example_manual['id']})
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'manual_meta_data' in json_res_body['data']
    manual_meta_data = json_res_body['data']['manual_meta_data']
    assert ('id' in manual_meta_data and 'name' in manual_meta_data and 'page_count' in manual_meta_data)
