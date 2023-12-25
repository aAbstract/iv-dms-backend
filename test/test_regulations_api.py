import json
import requests
import _test_config


def test_get_options_api_lock():
    api_url = f"{_test_config.get_api_url()}/regulations/get-options"
    http_headers = {'Authorization': 'Bearer fake_token'}
    http_res = requests.post(api_url, headers=http_headers)
    assert http_res.status_code == 403
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Unauthorized API Access [Invalid Token]')


def test_get_options_api_success():
    api_url = f"{_test_config.get_api_url()}/regulations/get-options"
    access_token = _test_config.login_user('cwael', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'Authorization': f"Bearer {access_token}"}
    http_res = requests.post(api_url, headers=http_headers)
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'regulations_options' in json_res_body['data']
    if len(json_res_body['data']['regulations_options']) > 0:
        regulations_option = json_res_body['data']['regulations_options'][0]
        assert ('id' in regulations_option and 'type' in regulations_option and 'name' in regulations_option)
