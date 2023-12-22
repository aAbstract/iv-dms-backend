import requests
import json
import _test_config


def test_server_online():
    api_url = f"{_test_config.get_api_url()}/test"
    http_res = requests.get(api_url)
    assert (http_res.status_code == 200)
    json_res_body = json.loads(http_res.content.decode())
    assert (json_res_body['success'] and json_res_body['msg'] == 'server online')
