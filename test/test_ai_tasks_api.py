import _test_config
import requests
import json


def test_check_ai_task_status_api_lock():
    api_url = f"{_test_config.get_api_url()}/ai-tasks/check-task"
    http_headers = {'X-Auth': 'Bearer fake_token'}
    http_res = requests.post(api_url, headers=http_headers, json={'task_id': '000000000000000000000000'})
    assert http_res.status_code == 403
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Unauthorized API Access [Invalid Token]')


def test_check_ai_task_status_api_invalid_task_info():
    access_token = _test_config.login_user('cwael', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'X-Auth': f"Bearer {access_token}"}
    api_url = f"{_test_config.get_api_url()}/ai-tasks/check-task"
    http_res = requests.post(api_url, headers=http_headers, json={'task_id': '000000000000000000000000'})
    assert http_res.status_code == 404
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'AI Task not Found')


def test_get_all_ai_tasks_api_lock():
    api_url = f"{_test_config.get_api_url()}/ai-tasks/get-all-tasks"
    http_headers = {'X-Auth': 'Bearer fake_token'}
    http_res = requests.post(api_url, headers=http_headers)
    assert http_res.status_code == 403
    json_res_body = json.loads(http_res.content.decode())
    assert (not json_res_body['success'] and json_res_body['msg'] == 'Unauthorized API Access [Invalid Token]')


def test_get_all_ai_tasks_api_success():
    username = 'cwael'
    access_token = _test_config.login_user(username, 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'X-Auth': f"Bearer {access_token}"}
    api_url = f"{_test_config.get_api_url()}/ai-tasks/get-all-tasks"
    http_res = requests.post(api_url, headers=http_headers)
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert 'ai_tasks' in json_res_body['data']
    if len(json_res_body['data']['ai_tasks']) > 0:
        example_ai_task = json_res_body['data']['ai_tasks'][0]
        obj_keys = set(example_ai_task.keys())
        assert obj_keys == {'task_status', 'end_datetime', 'start_datetime', 'task_type', 'id'}


def test_get_ai_task_status_api_success():
    access_token = _test_config.login_user('cwael', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'X-Auth': f"Bearer {access_token}"}

    # get ai tasks options
    api_url = f"{_test_config.get_api_url()}/ai-tasks/get-all-tasks"
    http_res = requests.post(api_url, headers=http_headers)
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert 'ai_tasks' in json_res_body['data']
    assert len(json_res_body['data']['ai_tasks']) > 0
    target_ai_task = json_res_body['data']['ai_tasks'][0]

    # get target ai task status
    api_url = f"{_test_config.get_api_url()}/ai-tasks/check-task"
    http_res = requests.post(api_url, headers=http_headers, json={'task_id': target_ai_task['id']})
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert 'ai_task_status' in json_res_body['data']
    assert json_res_body['data']['ai_task_status'] == target_ai_task['task_status']
