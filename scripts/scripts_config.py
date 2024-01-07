import requests
import json
import code
import readline
from rlcompleter import Completer


# SERVER_ADDR = '127.0.0.1'
SERVER_ADDR = 'iv-dms.duckdns.org'
SERVER_PORT = 8080
API_URL = f"https://{SERVER_ADDR}/api"
# API_URL = f"http://{SERVER_ADDR}:{SERVER_PORT}/api"


def login_user(username: str, password: str) -> str:
    api_url = f"{API_URL}/auth/login"
    json_req_body = {
        'username': username,
        'password': password,
    }
    http_res = requests.post(api_url, json=json_req_body)
    json_res_body = json.loads(http_res.content.decode())
    return json_res_body['data']['access_token']
