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
