import requests
import json
import _test_config


def test_auth_api_login_failed_invalid_account():
    api_url = f"{_test_config.get_api_url()}/auth/login"
    http_res = requests.post(api_url, json={
        'username': 'fake_user',
        'password': 'fake_password',
    })
    assert http_res.status_code == 401
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Login Failed, Invalid User Credentials')


def test_auth_api_login_failed_invalid_password():
    api_url = f"{_test_config.get_api_url()}/auth/login"
    http_res = requests.post(api_url, json={
        'username': 'air_cairo',
        'password': 'fake_password',
    })
    assert http_res.status_code == 401
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Login Failed, Invalid User Credentials')


def test_auth_api_login_success():
    api_url = f"{_test_config.get_api_url()}/auth/login"
    http_res = requests.post(api_url, json={
        'username': 'cwael',
        'password': 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV',
    })
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'access_token' in json_res_body['data']
