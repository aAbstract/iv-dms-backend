from uuid import uuid4
import json
import os
import httpx
from typing import BinaryIO
from models.runtime import ServiceResponse
from models.regulations import IOSAItem
from models.fs_index import CHAT_DOC_STATUS_CODE_MAP, ChatDocStatus
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
            return ServiceResponse(success=False, status_code=http_res.status_code, msg=f"ChatDoc API Error: {http_res.content.decode()}")

        json_res = json.loads(http_res.content.decode())
        if json_res['status'] != 'ok':
            return ServiceResponse(success=False, status_code=503, msg=f"ChatDoc API Error: {http_res.content.decode()}")

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
                return ServiceResponse(msg='ChatDoc API Disabled', data={'chat_doc_status': ChatDocStatus.PARSED})

            return ServiceResponse(success=False, status_code=http_res.status_code, msg=f"ChatDoc API Error: {http_res.content.decode()}")

        json_res = json.loads(http_res.content.decode())
        if json_res['status'] != 'ok':
            return ServiceResponse(success=False, status_code=503, msg=f"ChatDoc API Error: {http_res.content.decode()}")

        return ServiceResponse(data={'chat_doc_status': CHAT_DOC_STATUS_CODE_MAP[json_res['data']['status']]})


async def scan_doc(doc_id: str, filename: str, iosa_item: IOSAItem) -> ServiceResponse:
    chat_doc_enable = int(os.environ['CHAT_DOC_ENABLE'])
    if not chat_doc_enable:
        return ServiceResponse(data={
            'is_found': True,
            'text': 'NONE',
            'doc_ref': {},
        })

    api_key = os.environ['CHAT_DOC_API_KEY']
    api_headers = {'Authorization': f"Bearer {api_key}"}
    api_url = 'https://api.chatdoc.com/api/v2/questions'
    prompt = f"""
    given this REGULATION
    "{iosa_item.paragraph}"

    extract from file "{filename}" the best section that documents this REGULATION.
    output format is json object with this shape {{is_found: boolean, text: string}}.
    if nothing documents the REGULATION then is_found=false and text=NONE.
    do not include in text citaion.
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
            return ServiceResponse(success=False, status_code=http_res.status_code, msg=f"ChatDoc API Error: {http_res.content.decode()}")

        json_res = json.loads(http_res.content.decode())
        if json_res['status'] != 'ok':
            return ServiceResponse(success=False, status_code=503, msg=f"ChatDoc API Error: {http_res.content.decode()}")

        try:
            model_res = json.loads(json_res['data']['answer'])
        except:
            await log_man.add_log('lib.chat_doc.scan_doc', 'ERROR', f"chat_doc api parse error: {json_res['data']['answer']}")
            return ServiceResponse(success=False, status_code=503, msg='ChatDoc API Parse Error')

        if model_res['is_found']:
            return ServiceResponse(data={
                'is_found': True,
                'text': model_res['text'],
                'doc_ref': json_res['data']['source_info'][0],
            })
        return ServiceResponse(data={'is_found': False})
