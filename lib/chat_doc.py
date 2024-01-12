import re
from uuid import uuid4
import json
import os
import httpx
from typing import BinaryIO
from models.runtime import ServiceResponse
from models.regulations import IOSAItem
from models.fs_index import ChatDOCStatus
import lib.log as log_man


async def parse_doc(filename: str, file_ptr: BinaryIO) -> ServiceResponse:
    chat_doc_enable = int(os.environ['CHAT_DOC_ENABLE'])
    if not chat_doc_enable:
        return ServiceResponse(data={'chat_doc_uuid': str(uuid4())})

    api_key = os.environ['CHAT_DOC_API_KEY']
    api_headers = {'Authorization': f"Bearer {api_key}"}
    api_url = 'https://api.chatdoc.com/api/v2/documents/upload'
    async with httpx.AsyncClient(timeout=60) as client:
        http_res = await client.post(api_url, headers=api_headers, files={'file': (filename, file_ptr)})

        if http_res.status_code != 200:
            return ServiceResponse(success=False, status_code=http_res.status_code, msg=f"ChatDOC API Error: {http_res.content.decode()}")

        json_res = json.loads(http_res.content.decode())
        if json_res['status'] != 'ok':
            return ServiceResponse(success=False, status_code=503, msg=f"ChatDOC API Error: {http_res.content.decode()}")

        return ServiceResponse(data={'chat_doc_uuid': json_res['data']['id']})


async def check_doc(chat_doc_uuid: str) -> ServiceResponse:
    chat_doc_enable = int(os.environ['CHAT_DOC_ENABLE'])
    api_key = os.environ['CHAT_DOC_API_KEY']
    api_headers = {'Authorization': f"Bearer {api_key}"}
    api_url = f"https://api.chatdoc.com/api/v2/documents/{chat_doc_uuid}"
    async with httpx.AsyncClient(timeout=60) as client:
        http_res = await client.get(api_url, headers=api_headers)

        if http_res.status_code != 200:
            if http_res.status_code == 404 and not chat_doc_enable:
                return ServiceResponse(data={
                    'chat_doc_status': ChatDOCStatus.map_status_code(300)
                })

            return ServiceResponse(success=False, status_code=http_res.status_code, msg=f"ChatDOC API Error: {http_res.content.decode()}")

        json_res = json.loads(http_res.content.decode())
        if json_res['status'] != 'ok':
            return ServiceResponse(success=False, status_code=503, msg=f"ChatDOC API Error: {http_res.content.decode()}")

        return ServiceResponse(data={
            'chat_doc_status': ChatDOCStatus.map_status_code(json_res['data']['status'])
        })


async def scan_doc(doc_id: str, filename: str, iosa_item: IOSAItem) -> ServiceResponse:
    chat_doc_enable = int(os.environ['CHAT_DOC_ENABLE'])
    if not chat_doc_enable:
        return ServiceResponse(data={
            'matches': [{'text': 'ChatDOC API Disabled', 'refs': [0]}],
            'doc_refs': [],
        })

    api_key = os.environ['CHAT_DOC_API_KEY']
    api_headers = {'Authorization': f"Bearer {api_key}"}
    api_url = 'https://api.chatdoc.com/api/v2/questions'
    prompt = f"""
    given this REGULATION
    "{iosa_item.paragraph}"

    extract from file "{filename}" best sections that documents this REGULATION.
    output format must only be a json list.
    each object in the list has these keys: text, refs.
    text: the text that documents this REGULATION.
    refs: a list of references where this text is located in file "{filename}".
    if nothing documents the REGULATION then just output NONE.
    """

    async with httpx.AsyncClient(timeout=60) as client:
        http_res = await client.post(api_url, headers=api_headers, json={
            "upload_id": doc_id,
            "question": prompt,
            "stream": False,
            "search_entire_doc": True,
            "detailed_citation": True,
            "language": "en",
            "model_type": "gpt-4"
        })

        if http_res.status_code != 200:
            return ServiceResponse(success=False, status_code=http_res.status_code, msg=f"ChatDOC API Error: {http_res.content.decode()}")

        json_res = json.loads(http_res.content.decode())
        if json_res['status'] != 'ok':
            return ServiceResponse(success=False, status_code=503, msg=f"ChatDOC API Error: {http_res.content.decode()}")

        # clean answer text
        model_answer = re.sub(r'\["[0-9]+"\]', '', json_res['data']['answer'])
        model_answer = re.sub(r'"\[<span data-index="([0-9]+)">[0-9]+</span>\]"', r'\1', model_answer)
        try:
            model_json_answer = json.loads(model_answer)
        except:
            await log_man.add_log('lib.chat_doc.scan_doc', 'ERROR', f"chat_doc api parse error: {json_res['data']['answer']}")
            return ServiceResponse(success=False, status_code=503, msg='ChatDOC API Parse Error')

        if len(model_json_answer) > 0:
            obj_keys = set(model_json_answer[0].keys())
            if obj_keys != {'text', 'refs'}:
                return ServiceResponse(success=False, status_code=503, msg='Invalid ChatDOC API Response')

        # clean refs
        for match in model_json_answer:
            match['refs'] = [x for x in match['refs'] if isinstance(x, int)]

        return ServiceResponse(data={
            'matches': model_json_answer,
            'doc_refs': json_res['data']['source_info'],
        })
