import json
import requests


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


print(f"API_URL={API_URL}")
print('checking server status...')
status_msg = json.loads(requests.get(f"{API_URL}/test").content.decode())
print(status_msg)

if status_msg['success']:
    print('fetching system logs...')
    api_url = f"{API_URL}/activity/get-logs"
    admin_access_token = login_user('eslam', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'X-Auth': f"Bearer {admin_access_token}"}
    http_res = requests.post(api_url, headers=http_headers, json={'limit': 10})
    json_obj = json.loads(http_res.content.decode())
    json_str = json.dumps(json_obj['data']['logs'], indent=2)
    print(json_str)
    print(f"count: {len(json_obj['data']['logs'])}")

else:
    print('ERROR: server offline')
