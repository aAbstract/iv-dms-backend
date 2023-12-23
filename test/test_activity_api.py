import json
import requests
import _test_config


def test_get_logs_lock():
    api_url = f"{_test_config.get_api_url()}/activity/get-logs"
    http_headers = {'Authorization': 'Bearer fake_token'}
    http_res = requests.post(api_url, headers=http_headers, json={'limit': 10})
    assert http_res.status_code == 403
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Unauthorized API Access [Invalid Token]')

    user_access_token = _test_config.login_user('cwael', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'Authorization': f"Bearer {user_access_token}"}
    http_res = requests.post(api_url, headers=http_headers, json={'limit': 10})
    assert http_res.status_code == 403
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Unauthorized API Access [Restricted Access]')


def test_get_logs():
    api_url = f"{_test_config.get_api_url()}/activity/get-logs"
    admin_access_token = _test_config.login_user('eslam', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'Authorization': f"Bearer {admin_access_token}"}
    http_res = requests.post(api_url, headers=http_headers, json={'limit': 10})
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'logs' in json_res_body['data']
