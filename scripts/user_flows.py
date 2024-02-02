# autopep8: off
import json
import os
import sys
import time
from dotenv import load_dotenv
def load_root_path():
    file_dir = os.path.abspath(__file__)
    lv1_dir = os.path.dirname(file_dir)
    root_dir = os.path.dirname(lv1_dir)
    sys.path.append(root_dir)


load_root_path()
load_dotenv()
from scripts.scripts_config import *
# autopep8: on


# change this
TEXT_TO_AUDIT = """
No person may serve as a crewmember knowing that he has a physical deficiency or mental
condition that would render him unable to meet the requirements of his current medical
certificate, to discharge his responsibilities to a safe standard or could endanger the safety of
the aircraft or its occupants.
Crewmembers should not undertake flying duties whilst under the influence of alcohol,
narcotics, drugs or any medicine that was not approved by the medical department for use for
crewmembers like sleeping tablet.
The following factors shall be considered while undertaking flying duties by crewmembers:
- alcohol and psychoactive substance use;
- pregnancy;
- illness or use of medication(s);
- blood donations;
- surgery;
- deep under water diving;
- Fatigue occurrence on one flight or accumulated over period of time.
- Each crewmember is responsible to notify crew scheduling office and/or Operations
Control Center about his/her state of unfitness for undertaking flying duties due to any
of the above factors. The notification shall take place using Nesma Airlines’
communications tools. Crew scheduling office shall release the reporting crewmember
from assigned duty. Released crewmember shall not be reassigned for flying duties
unless he is fit for duty
"""

# TEXT_TO_AUDIT = """
# English and Arabic are the designated common language used by all Nesma Airlines flight
# crewmembers for communication.
# Personnel who demonstrate proficiency below expert level (ICAO Level 6) should be formally
# evaluated at intervals in accordance with ECAR 63.9 and ICAO Annex 1 item 1.2.9.6 as
# follows:
# ▪ Those demonstrated language proficiency at the operational level (Level 4) should be
# evaluated at least once every three years
# ▪ Those demonstrated language proficiency at the operational level (Level 5) should be
# evaluated at least once every six years
# ECAA requires level four of English language as a minimum level. All operational
# communications shall be established and maintained in English:
# 1. On the flight deck during line operation.
# 2. Between flight crew and cabin crew during line operation.
# 3. During flight crew training and evaluation activities.
# 4. In normal operations, abnormal and emergency situations
# 5. In the event of incapacitation of any crewmember
# """


def scan_doc_user_flow():
    access_token = login_user('cwael', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'X-Auth': f"Bearer {access_token}"}

    # get regulations options
    api_url = f"{API_URL}/regulations/get-options"
    http_res = requests.post(api_url, headers=http_headers)
    json_res_body = json.loads(http_res.content.decode())
    regulation_id = [x for x in json_res_body['data']['regulations_options'] if x['name'] == 'IOSA Standards Manual (ISM) Ed 16-Revision2'][0]['id']

    # test pdf AI scanner
    print('scanning PDF...')
    api_url = f"{API_URL}/manuals/scan-pdf"
    http_res = requests.post(api_url, headers=http_headers, json={
        'regulation_id': regulation_id,
        'checklist_code': 'FLT 3.7.1',
        'doc_uuid': os.environ['COMPLETE_CHAT_DOC_UUID'],
    })
    json_res_body = json.loads(http_res.content.decode())
    ai_task_id = json_res_body['data']['ai_task_id']

    while True:
        api_url = f"{API_URL}/ai-tasks/check-task"
        http_res = requests.post(api_url, headers=http_headers, json={'task_id': ai_task_id})
        json_res_body = json.loads(http_res.content.decode())
        task_status = json_res_body['data']['ai_task_status']
        print(f"AI Task {ai_task_id} Status: {task_status}")
        task_resp = json_res_body['data']['json_res']
        if task_status != 'IN_PROGRESS':
            break
        time.sleep(5)

    print('=' * 100)
    print(json.dumps(task_resp, indent=2))
    print('=' * 100)


def comply_enhance_user_flow():
    access_token = login_user('cwael', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
    http_headers = {'X-Auth': f"Bearer {access_token}"}
    verbose = True

    # get regulations options
    api_url = f"{API_URL}/regulations/get-options"
    http_res = requests.post(api_url, headers=http_headers)
    json_res_body = json.loads(http_res.content.decode())
    regulation_id = [x for x in json_res_body['data']['regulations_options'] if x['name'] == 'IOSA Standards Manual (ISM) Ed 16-Revision2'][0]['id']

    # call audit llm api
    print('calling IOSA audit API...')
    api_url = f"{API_URL}/llm/iosa-audit-unstruct"
    http_res = requests.post(api_url, headers=http_headers, json={
        'regulation_id': regulation_id,
        'checklist_code': 'FLT 3.4.2',  # change this
        'text': TEXT_TO_AUDIT,
    })
    json_res_body = json.loads(http_res.content.decode())
    old_ocs = json_res_body['data']['overall_compliance_score']
    print(f"OVERALL_COMPLIANCE_SCORE: {old_ocs}")
    if verbose:
        print('=' * 100)
        print(json_res_body['data']['llm_resp'])
        print('=' * 100)

    # call enhance llm api
    print('calling IOSA enhance API...')
    api_url = f"{API_URL}/llm/iosa-enhance-unstruct"
    context_id = json_res_body['data']['context_id']
    http_res = requests.post(api_url, headers=http_headers, json={'context_id': context_id})
    json_res_body = json.loads(http_res.content.decode())
    new_ocs = json_res_body['data']['new_compliance_score']
    print(f"NEW_COMPLIANCE_SCORE: {new_ocs}")
    if verbose:
        print('=' * 100)
        print(json_res_body['data']['llm_resp'])
        print('=' * 100)


if __name__ == '__main__':
    # scan_doc_user_flow()
    comply_enhance_user_flow()
