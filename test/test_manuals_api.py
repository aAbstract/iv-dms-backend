import time
import os
import json
import requests
from dotenv import load_dotenv
import _test_config


def test_parse_pdf_api_lock():
    api_url = f"{_test_config.get_api_url()}/manuals/parse-pdf"
    http_headers = {'X-Auth': 'Bearer fake_token'}
    http_res = requests.post(api_url, headers=http_headers, files={'file': open('data/sample_manual.pdf', 'rb')})
    assert http_res.status_code == 403
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Unauthorized API Access [Invalid Token]')


def test_get_page_api_lock():
    api_url = f"{_test_config.get_api_url()}/manuals/get-page"
    http_headers = {'X-Auth': 'Bearer fake_token'}
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
    http_headers = {'X-Auth': f"Bearer {access_token}"}
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
    http_headers = {'X-Auth': f"Bearer {access_token}"}

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
    http_headers = {'X-Auth': 'Bearer fake_token'}
    http_res = requests.post(api_url, headers=http_headers, json={'manual_id': '000000000000000000000000'})
    assert http_res.status_code == 403
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Unauthorized API Access [Invalid Token]')


def test_get_meta_data_api_success():
    access_token = _test_config.login_user('cwael', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'X-Auth': f"Bearer {access_token}"}

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


def test_chat_doc_parse_api():
    # test parse doc
    access_token = _test_config.login_user('cwael', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    api_url = f"{_test_config.get_api_url()}/manuals/parse-pdf"
    http_headers = {'X-Auth': f"Bearer {access_token}"}
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
    assert json_res_body['data']['chat_doc_status'] in ['PARSED', 'PARSING', 'PARSING_FAILD']


def test_chat_doc_scan_api():
    load_dotenv()
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

    # test pdf AI scanner
    api_url = f"{_test_config.get_api_url()}/manuals/scan-pdf"
    http_res = requests.post(api_url, headers=http_headers, json={
        'regulation_id': regulation_id,
        'checklist_code': 'FLT 3.1.1',
        'doc_uuid': os.environ['COMPLETE_CHAT_DOC_UUID'],
    })
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'ai_task_id' in json_res_body['data']
    ai_task_id = json_res_body['data']['ai_task_id']

    while True:
        api_url = f"{_test_config.get_api_url()}/ai-tasks/check-task"
        http_res = requests.post(api_url, headers=http_headers, json={'task_id': ai_task_id})
        assert http_res.status_code == 200
        json_res_body = json.loads(http_res.content.decode())
        assert 'ai_task_status' in json_res_body['data']
        assert 'json_resp' in json_res_body['data']
        task_status = json_res_body['data']['ai_task_status']
        task_resp = json_res_body['data']['json_resp']
        if task_status != 'IN_PROGRESS':
            break
        time.sleep(5)

    # check task_resp structure
    assert 'matches' in task_resp['data']
    if len(task_resp['data']['matches']) > 0:
        obj_keys = set(task_resp['data']['matches'][0])
        assert obj_keys == {'text', 'refs'}


def test_chat_doc_parse_api_bad_file_type():
    access_token = _test_config.login_user('cwael', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    api_url = f"{_test_config.get_api_url()}/manuals/parse-pdf"
    http_headers = {'X-Auth': f"Bearer {access_token}"}
    http_res = requests.post(api_url, headers=http_headers, files={'file': open('data/sample_manual.txt', 'rb')})
    assert http_res.status_code == 409
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Bad File Extention')


def test_get_user_manuals_api_lock():
    api_url = f"{_test_config.get_api_url()}/manuals/get-manuals"
    http_headers = {'X-Auth': 'Bearer fake_token'}
    http_res = requests.post(api_url, headers=http_headers)
    assert http_res.status_code == 403
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Unauthorized API Access [Invalid Token]')


def test_get_user_manuals_api_success():
    access_token = _test_config.login_user('cwael', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    api_url = f"{_test_config.get_api_url()}/manuals/get-manuals"
    http_headers = {'X-Auth': f"Bearer {access_token}"}
    http_res = requests.post(api_url, headers=http_headers)
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert 'files' in json_res_body['data']
    if len(json_res_body['data']['files']) > 0:
        example_file = json_res_body['data']['files'][0]
        obj_keys = set(example_file.keys())
        assert obj_keys == {'doc_status', 'filename', 'datetime', 'id', 'doc_uuid', 'username', 'file_type'}
