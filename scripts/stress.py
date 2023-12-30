import os
import glob
import sys
import requests
import json
import threading
import colorama
import socket


TEST_COUNT = 10
THREAD_COUNT = 10
SERVER_PORT = 8080
SERVER_IP = '127.0.0.1'
SERVER_URL = f"http://{SERVER_IP}:{SERVER_PORT}"
API_URL = f"{SERVER_URL}/api"


def print_err_log(msg: str):
    err_tag = f"{colorama.Fore.RED}[ERROR]{colorama.Style.RESET_ALL}"
    print(f"{err_tag}: {msg}")


def is_port_open(host: str, port: int) -> bool:
    try:
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _socket.settimeout(2)
        _socket.connect((host, port))
        return True
    except:
        return False
    finally:
        _socket.close()


def run_test(iter_count: int, thread_id: int = 0) -> int:
    for i in range(iter_count):
        print(f"[THREAD-{thread_id}] Starting iteration {i}")
        test_exit_code = os.system('pytest')
        if test_exit_code != 0:
            print_err_log(f"[THREAD-{thread_id}] Test iteration {i} faild")
            return 1
    return 0


# check current directory
dir_content = glob.glob('*')
if 'test' not in dir_content:
    print_err_log('No tests found in this directory')
    sys.exit(1)

# check if server port is open
if not is_port_open(SERVER_IP, SERVER_PORT):
    print_err_log(f"Server {SERVER_URL} is offline")
    sys.exit(1)

# check http server
api_url = f"{API_URL}/test"
http_res = requests.get(api_url)
if http_res.status_code != 200:
    print_err_log(f"Local server error [status_code = {http_res.status_code}]")
    sys.exit(1)

json_res_body = json.loads(http_res.content.decode())

if not (json_res_body['success'] and json_res_body['msg'] == 'server online'):
    print_err_log(f"Local server error [json_res_body = {json_res_body}]")
    sys.exit(1)

test_mode = sys.argv[1]
if test_mode == '-p':
    # run parallel stress test
    test_per_thread = TEST_COUNT // THREAD_COUNT
    thread_list: list[threading.Thread] = [threading.Thread(target=run_test, args=(test_per_thread, i)) for i in range(THREAD_COUNT)]
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()

elif test_mode == '-s':
    # run sequential stress test
    rc = run_test(TEST_COUNT)
    if rc != 0:
        sys.exit(rc)

else:
    print_err_log(f"Unrecognized test mode {test_mode}\nUsage -p: parallel stress test, -s sequential stress test")

print('Integration stress test finished successfully')
