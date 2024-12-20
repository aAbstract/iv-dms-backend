import json
import requests
import _test_config


def test_create_attachment_api_lock():
    api_url = f"{_test_config.get_api_url()}/attachments/create-attachment"
    http_headers = {'X-Auth': 'Bearer fake_token'}
    http_res = requests.post(api_url, headers=http_headers, files={'file': open('data/sample_attachment.png', 'rb')})
    assert http_res.status_code == 403
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Unauthorized API Access [Invalid Token]')


def test_create_attachment_png_file_api_success():
    # test create attachment
    access_token = _test_config.login_user('cwael', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    api_url = f"{_test_config.get_api_url()}/attachments/create-attachment"
    http_headers = {'X-Auth': f"Bearer {access_token}"}
    http_res = requests.post(api_url, headers=http_headers, files={'file': open('data/sample_attachment.png', 'rb')})
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'file_id' in json_res_body['data']
    assert 'url_path' in json_res_body['data']

    # validate create attachment
    file_url = f"{_test_config.get_file_server_url()}{json_res_body['data']['url_path']}"
    http_res = requests.get(file_url)
    assert http_res.status_code == 200


def test_create_attachment_zip_file_api_success():
    # test create attachment
    access_token = _test_config.login_user('cwael', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    api_url = f"{_test_config.get_api_url()}/attachments/create-attachment"
    http_headers = {'X-Auth': f"Bearer {access_token}"}
    http_res = requests.post(api_url, headers=http_headers, files={'file': open('data/sample_attachment.zip', 'rb')})
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'file_id' in json_res_body['data']
    assert 'url_path' in json_res_body['data']

    # validate create attachment
    file_url = f"{_test_config.get_file_server_url()}{json_res_body['data']['url_path']}"
    http_res = requests.get(file_url)
    assert http_res.status_code == 200
