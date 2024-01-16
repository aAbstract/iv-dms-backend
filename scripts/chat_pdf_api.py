import time
import os
import json
import requests
import code
import readline
from rlcompleter import Completer
from dotenv import load_dotenv


load_dotenv()
API_HEADERS = {'x-api-key': os.environ['CHAT_PDF_API_KEY']}
UPLOAD_API = 'https://api.chatpdf.com/v1/sources/add-file'
ASK_API = 'https://api.chatpdf.com/v1/chats/message'
DOC_ID = os.environ['COMPLETE_CHAT_PDF_UUID']


def upload_doc(filename: str):
    http_res = requests.post(UPLOAD_API, headers=API_HEADERS, files={'file': open(filename, 'rb')})
    json_res = json.loads(http_res.content.decode())
    print(json.dumps(json_res, indent=2))


def ask_doc(doc_id: str, question: str):
    json_req = {
        'sourceId': doc_id,
        'messages': [
            {
                'role': 'user',
                'content': question,
            }
        ]
    }
    llm_start = time.time()
    http_res = requests.post(ASK_API, headers=API_HEADERS, json=json_req)
    print('=' * 100)
    print(f"response time: {time.time() - llm_start}s")
    print('=' * 100)
    json_res = json.loads(http_res.content.decode())
    print(json.dumps(json_res, indent=2))


readline.set_completer(Completer().complete)
readline.parse_and_bind('tab: complete')
code.interact(local=locals())
