import os
import json
import requests
import code
import readline
from rlcompleter import Completer
from dotenv import load_dotenv


load_dotenv()
API_HEADERS = {'Authorization': f"Bearer {os.environ['CHAT_DOC_API_KEY']}"}
UPLOAD_API = 'https://api.chatdoc.com/api/v2/documents/upload'
DOCS_API = 'https://api.chatdoc.com/api/v2/documents'
SUGGS_API = 'https://api.chatdoc.com/api/v2/questions/suggested'
ASK_API = 'https://api.chatdoc.com/api/v2/questions'
DOC_ID = os.environ['COMPLETE_CHAT_DOC_UUID']


def upload_doc(filename: str):
    http_res = requests.post(UPLOAD_API, headers=API_HEADERS, files={'file': open(filename, 'rb')})
    json_res = json.loads(http_res.content.decode())
    print(json.dumps(json_res, indent=2))


def check_doc(doc_id: str):
    api_url = f"{DOCS_API}/{doc_id}"
    http_res = requests.get(api_url, headers=API_HEADERS)
    json_res = json.loads(http_res.content.decode())
    print(json.dumps(json_res, indent=2))


def get_suggs(doc_id: str):
    api_url = f"{SUGGS_API}"
    http_res = requests.get(api_url, headers=API_HEADERS, params={'upload_id': doc_id})
    json_res = json.loads(http_res.content.decode())
    print(json.dumps(json_res, indent=2))


def del_doc(doc_id: str):
    api_url = f"{DOCS_API}/{doc_id}"
    http_res = requests.delete(api_url, headers=API_HEADERS, params={'upload_id': doc_id})
    json_res = json.loads(http_res.content.decode())
    print(json.dumps(json_res, indent=2))


def ask_doc(doc_id: str, question: str):
    json_req = {
        "upload_id": doc_id,
        "question": question,
        "stream": True,
        "search_entire_doc": True,
        "detailed_citation": True,
        "language": "en",
        "model_type": "gpt-4"
    }
    http_res = requests.post(ASK_API, headers=API_HEADERS, json=json_req, stream=True)
    json_res = json.loads(http_res.content.decode())
    print(json.dumps(json_res, indent=2))


readline.set_completer(Completer().complete)
readline.parse_and_bind("tab: complete")
code.interact(local=locals())
