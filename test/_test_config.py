import requests
import json


_SERVER_URL = '127.0.0.1'
_SERVER_PORT = 8080


def get_api_url():
    return f"http://{_SERVER_URL}:{_SERVER_PORT}/api"


def login_user(username: str, password: str) -> str:
    api_url = f"{get_api_url()}/auth/login"
    json_req_body = {
        'username': username,
        'password': password,
    }
    http_res = requests.post(api_url, json=json_req_body)
    json_res_body = json.loads(http_res.content.decode())
    return json_res_body['data']['access_token']
