# autopep8: off
import os
import sys
from bson import ObjectId
import json
import requests
import _test_config
from dotenv import load_dotenv


def load_root_path():
    file_dir = os.path.abspath(__file__)
    lv1_dir = os.path.dirname(file_dir)
    root_dir = os.path.dirname(lv1_dir)
    sys.path.append(root_dir)


load_root_path()
load_dotenv()
from models.flow_reports import (FinalComment, FlowReportStatus, UserChangeType)
# autopep8: on


def test_list_flow_report_lock():
    api_url = f"{_test_config.get_api_url()}/flow_report/list-flow-report"
    http_headers = {"X-Auth": "Bearer fake_token"}
    payload = {"creator": "cwael"}

    http_res = requests.post(api_url, headers=http_headers, json=payload)
    assert http_res.status_code == 403
    json_res_body = json.loads(http_res.content.decode())
    print(json_res_body)
    assert (
        not json_res_body["success"]
        and json_res_body["msg"] == "Unauthorized API Access [Invalid Token]"
    )

    user_access_token = _test_config.login_user(
        "sam", "CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV"
    )
    http_headers = {"X-Auth": f"Bearer {user_access_token}"}
    http_res = requests.post(api_url, headers=http_headers, json=payload)
    assert http_res.status_code == 403
    json_res_body = json.loads(http_res.content.decode())
    assert (
        not json_res_body["success"]
        and json_res_body["msg"] == "Unauthorized API Access [Restricted Access]"
    )


def test_create_flow_report():
    admin_access_token = _test_config.login_user(
        "cwael", "CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV"
    )
    http_headers = {"X-Auth": f"Bearer {admin_access_token}"}

    get_database = _test_config.get_database()
    assert get_database != None

    # get regulations options
    api_url = f"{_test_config.get_api_url()}/regulations/get-options"
    http_res = requests.post(api_url, headers=http_headers)
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body["success"]
    assert "regulations_options" in json_res_body["data"]
    regulation_id = [
        x
        for x in json_res_body["data"]["regulations_options"]
        if x["name"] == "IOSA Standards Manual (ISM) Ed 16-Revision2"
    ][0]["id"]

    # test api
    api_url = f"{_test_config.get_api_url()}/flow_report/create-flow-report"

    payload = {
        "regulation_id": regulation_id,
        "title": "Test Title",
        "checklist_template_code": "FLT 2",
    }
    print(payload)
    http_res = requests.post(api_url, headers=http_headers, json=payload)

    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body["success"]
    assert "flow_report" in json_res_body["data"]

    obj_keys = set(json_res_body["data"]["flow_report"])
    assert obj_keys == {
        "title",
        "regulation_id",
        "code",
        "status",
        "organization",
        "_id",
        "creator",
        "user_changes"
    }
    assert json_res_body["data"]["flow_report"]["title"] == "Test Title"

    flow_report = get_database["flow_reports"].find_one_and_delete(
        {"_id": ObjectId(json_res_body["data"]["flow_report"]["_id"])}
    )

    assert flow_report["_id"]
    assert flow_report["title"] == "Test Title"
    assert "user_changes" in flow_report
    assert (
        flow_report["user_changes"][0]["change_type"] == UserChangeType.CREATE
    )


def test_list_flow_report():
    admin_access_token = _test_config.login_user(
        "cwael", "CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV"
    )
    http_headers = {"X-Auth": f"Bearer {admin_access_token}"}
    get_database = _test_config.get_database()
    assert get_database != None

    # get regulations options
    api_url = f"{_test_config.get_api_url()}/regulations/get-options"
    http_res = requests.post(api_url, headers=http_headers)
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body["success"]
    assert "regulations_options" in json_res_body["data"]
    regulation_id = [
        x
        for x in json_res_body["data"]["regulations_options"]
        if x["name"] == "IOSA Standards Manual (ISM) Ed 16-Revision2"
    ][0]["id"]

    # create flow report
    api_url = f"{_test_config.get_api_url()}/flow_report/create-flow-report"

    payload = {
        "regulation_id": regulation_id,
        "title": "Test Title",
        "checklist_template_code": "FLT 2",
    }

    http_res = requests.post(api_url, headers=http_headers, json=payload)

    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body["success"]
    assert "flow_report" in json_res_body["data"]

    obj_keys = set(json_res_body["data"]["flow_report"])
    assert obj_keys == {
        "title",
        "regulation_id",
        "code",
        "status",
        "organization",
        "_id",
        "creator",
        "user_changes"
    }
    assert json_res_body["data"]["flow_report"]["title"] == "Test Title"
    assert json_res_body["data"]["flow_report"]["code"] == "FLT 2"

    flow_report_id = json_res_body["data"]['flow_report']["_id"]

    # test api
    api_url = f"{_test_config.get_api_url()}/flow_report/list-flow-report"

    payload = {"creator": "cwael"}
    print(http_headers)
    http_res = requests.post(api_url, headers=http_headers, json=payload)

    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body["success"]
    assert "flow_reports" in json_res_body["data"]
    assert isinstance(json_res_body["data"]["flow_reports"], list)
    obj_keys = set(json_res_body["data"]["flow_reports"][0])
    assert obj_keys == {
        "title",
        "regulation_id",
        "code",
        "status",
        "organization",
        "_id",
        "creator",
        "user_changes"
    }

    # reset db
    flow_report = get_database["flow_reports"].find_one_and_delete({"_id": ObjectId(flow_report_id)})
    assert flow_report["_id"]


def test_get_flow_report():
    admin_access_token = _test_config.login_user(
        "cwael", "CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV"
    )
    http_headers = {"X-Auth": f"Bearer {admin_access_token}"}

    # create flow report
    # get regulations options
    api_url = f"{_test_config.get_api_url()}/regulations/get-options"
    http_res = requests.post(api_url, headers=http_headers)
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body["success"]
    assert "regulations_options" in json_res_body["data"]
    regulation_id = [
        x
        for x in json_res_body["data"]["regulations_options"]
        if x["name"] == "IOSA Standards Manual (ISM) Ed 16-Revision2"
    ][0]["id"]

    # test api
    api_url = f"{_test_config.get_api_url()}/flow_report/create-flow-report"

    payload = {
        "regulation_id": regulation_id,
        "title": "Test Title",
        "checklist_template_code": "FLT 2",
    }

    http_res = requests.post(api_url, headers=http_headers, json=payload)

    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body["success"]
    assert "flow_report" in json_res_body["data"]

    # get status before change
    assert "user_changes" in json_res_body["data"]['flow_report']
    change_size = len(json_res_body["data"]["flow_report"]["user_changes"])
    assert json_res_body["data"]["flow_report"]["user_changes"][0]['change_type'] == UserChangeType.CREATE
    obj_keys = set(json_res_body["data"]["flow_report"])

    assert obj_keys == {
        "title",
        "regulation_id",
        "code",
        "status",
        "organization",
        "_id",
        "creator",
        "user_changes"
    }
    assert json_res_body["data"]["flow_report"]["title"] == "Test Title"
    assert json_res_body["data"]["flow_report"]["code"] == "FLT 2"
    flow_report = json_res_body["data"]["flow_report"]
    assert flow_report["_id"]

    # get flow report id
    get_database = _test_config.get_database()
    assert get_database != None

    payload = {"flow_report_id": str(flow_report["_id"])}

    # test api
    api_url = f"{_test_config.get_api_url()}/flow_report/get-flow-report"

    http_res = requests.post(api_url, headers=http_headers, json=payload)

    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body["success"]

    obj_keys = set(json_res_body["data"])
    assert obj_keys == {
        "title",
        "regulation_id",
        "code",
        "sub_sections",
        "status",
        "organization",
        "applicability",
        "guidance",
        "_id",
        "creator",
        "user_changes"
    }

    # reset flow report
    flow_report = get_database["flow_reports"].find_one_and_delete(
        {"_id": ObjectId(json_res_body["data"]["_id"])}
    )
    assert "user_changes" in flow_report
    assert change_size + 1 == len(flow_report["user_changes"])
    assert (
        flow_report["user_changes"][1]["change_type"] == UserChangeType.VIEW
    )
    assert flow_report["_id"]
    assert flow_report["title"] == "Test Title"
    assert flow_report["code"] == "FLT 2"


def test_delete_flow_report():
    admin_access_token = _test_config.login_user(
        "cwael", "CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV"
    )
    http_headers = {"X-Auth": f"Bearer {admin_access_token}"}

    get_database = _test_config.get_database()
    assert get_database != None

    # get regulations options
    api_url = f"{_test_config.get_api_url()}/regulations/get-options"
    http_res = requests.post(api_url, headers=http_headers)
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body["success"]
    assert "regulations_options" in json_res_body["data"]
    regulation_id = [
        x
        for x in json_res_body["data"]["regulations_options"]
        if x["name"] == "IOSA Standards Manual (ISM) Ed 16-Revision2"
    ][0]["id"]

    # test api
    api_url = f"{_test_config.get_api_url()}/flow_report/create-flow-report"

    payload = {
        "regulation_id": regulation_id,
        "title": "Test Title",
        "checklist_template_code": "FLT 2",
    }

    http_res = requests.post(api_url, headers=http_headers, json=payload)

    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body["success"]
    assert "flow_report" in json_res_body["data"]

    # get status before change
    assert "user_changes" in json_res_body["data"]['flow_report']
    change_size = len(json_res_body["data"]["flow_report"]["user_changes"])
    assert json_res_body["data"]["flow_report"]["user_changes"][0]['change_type'] == UserChangeType.CREATE

    obj_keys = set(json_res_body["data"]["flow_report"])
    assert obj_keys == {
        "title",
        "regulation_id",
        "code",
        "status",
        "organization",
        "_id",
        "creator",
        "user_changes"
    }
    assert json_res_body["data"]["flow_report"]["title"] == "Test Title"
    assert json_res_body["data"]["flow_report"]["code"] == "FLT 2"

    # delete flow report
    # test api
    api_url = f"{_test_config.get_api_url()}/flow_report/delete-flow-report"

    report_id = json_res_body["data"]["flow_report"]["_id"]
    payload = {"flow_report_id": str(report_id), "comment": "Test Delete"}

    http_res = requests.post(api_url, headers=http_headers, json=payload)

    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body["success"]
    flow_report = get_database["flow_reports"].find_one({"_id": ObjectId(report_id)})
    assert flow_report['status'] == FlowReportStatus.DELETED
    assert "user_changes" in flow_report
    assert change_size + 1 == len(flow_report["user_changes"])
    assert (
        flow_report["user_changes"][1]["change_type"] == UserChangeType.DELETE
    )
    flow_report = get_database["flow_reports"].find_one_and_delete({"_id": ObjectId(report_id)})
    assert flow_report["_id"]


def test_update_flow_report_sub_sections():
    admin_access_token = _test_config.login_user(
        "cwael", "CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV"
    )
    http_headers = {"X-Auth": f"Bearer {admin_access_token}"}

    get_database = _test_config.get_database()
    assert get_database != None

    # get regulations options
    api_url = f"{_test_config.get_api_url()}/regulations/get-options"
    http_res = requests.post(api_url, headers=http_headers)
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body["success"]
    assert "regulations_options" in json_res_body["data"]
    regulation_id = [
        x
        for x in json_res_body["data"]["regulations_options"]
        if x["name"] == "IOSA Standards Manual (ISM) Ed 16-Revision2"
    ][0]["id"]

    # create flow report
    api_url = f"{_test_config.get_api_url()}/flow_report/create-flow-report"

    payload = {
        "regulation_id": regulation_id,
        "title": "Test Title",
        "checklist_template_code": "FLT 1",
    }

    http_res = requests.post(api_url, headers=http_headers, json=payload)

    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body["success"]
    assert "flow_report" in json_res_body["data"]

    obj_keys = set(json_res_body["data"]["flow_report"])
    assert obj_keys == {
        "title",
        "regulation_id",
        "code",
        "status",
        "organization",
        "_id",
        "creator",
        "user_changes"
    }
    assert json_res_body["data"]["flow_report"]["title"] == "Test Title"
    assert json_res_body["data"]["flow_report"]["code"] == "FLT 1"
    flow_report_id = json_res_body["data"]["flow_report"]['_id']

    # get status before change
    assert "user_changes" in json_res_body["data"]['flow_report']
    change_size = len(json_res_body["data"]["flow_report"]["user_changes"])
    assert json_res_body["data"]["flow_report"]["user_changes"][0]['change_type'] == UserChangeType.CREATE

    # create fs index
    api_url = f"{_test_config.get_api_url()}/attachments/create-attachment"
    http_res = requests.post(api_url, headers=http_headers, files={'file': open('data/sample_attachment.png', 'rb')})
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body['success']
    assert 'file_id' in json_res_body['data']
    assert 'url_path' in json_res_body['data']
    file_id = str(json_res_body['data']['file_id'])
    # validate create attachment
    file_url = f"{_test_config.get_file_server_url()}{json_res_body['data']['url_path']}"
    http_res = requests.get(file_url)
    assert http_res.status_code == 200

    payload = {
        "sub_sections": [
            {
                "title": "1.1 Management System Overview",
                "checklist_items": [
                    {
                        "code": "FLT 1.1.1",
                        "manual_references": [
                            {"fs_index": file_id, "pages": [1, 2, 3]}
                        ],
                        "final_comment": FinalComment.DOCNOTIMP,
                        "comments": "Test Comment",
                        "actions": "Test actions",
                        "fs_index": file_id
                    }
                ],
            }
        ],
        "flow_report_id": flow_report_id,
        "comment": "Test Comment",
    }

    # test api
    api_url = f"{_test_config.get_api_url()}/flow_report/update-flow-report-sub-sections"

    http_res = requests.post(api_url, headers=http_headers, json=payload)

    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body["success"]

    # get status after change
    flow_report = get_database["flow_reports"].find_one(
        {"_id": ObjectId(flow_report_id)})

    assert "_id" in flow_report
    assert "sub_sections" in flow_report

    assert flow_report['sub_sections'][0]['checklist_items'][0]['manual_references'][0] == {"fs_index": file_id, "pages": [1, 2, 3]}
    assert flow_report['sub_sections'][0]['checklist_items'][0]['final_comment'] == FinalComment.DOCNOTIMP
    assert flow_report['sub_sections'][0]['checklist_items'][0]['comments'] == "Test Comment"
    assert flow_report['sub_sections'][0]['checklist_items'][0]['actions'] == "Test actions"
    assert flow_report['sub_sections'][0]['checklist_items'][0]['actions'] == "Test actions"
    assert flow_report['sub_sections'][0]['checklist_items'][0]['fs_index'] == file_id

    # check user change object after
    assert "user_changes" in flow_report
    assert change_size + 1 == len(flow_report["user_changes"])
    assert (
        flow_report["user_changes"][1]["change_type"] == UserChangeType.UPDATE
    )
    assert flow_report["user_changes"][1]["user_comment"] == "Test Comment"

    # reset
    flow_report = get_database["flow_reports"].find_one_and_delete({"_id": ObjectId(flow_report["_id"])})
    assert flow_report["_id"]
