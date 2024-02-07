from bson import ObjectId
import json
import requests
import _test_config
from models.flow_reports import (FinalComment, FlowReportChange, FlowReportStatus, UserChangeType)
from datetime import datetime

def test_list_flow_report_lock():
    api_url = f"{_test_config.get_api_url()}/flow_report/list-flow-report"
    http_headers = {"X-Auth": "Bearer fake_token"}
    payload = {"creator":"cwael"}

    http_res = requests.post(api_url, headers=http_headers,json=payload)
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
    http_res = requests.post(api_url, headers=http_headers,json=payload)
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
        "sub_sections",
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

def test_list_flow_report():
    admin_access_token = _test_config.login_user(
        "cwael", "CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV"
    )
    http_headers = {"X-Auth": f"Bearer {admin_access_token}"}

    # reset flow report
    get_database = _test_config.get_database()
    assert get_database != None

    # test api
    api_url = f"{_test_config.get_api_url()}/flow_report/list-flow-report"

    payload = {"creator":"cwael"}
    print(http_headers)
    http_res = requests.post(api_url, headers=http_headers,json=payload)

    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body["success"]
    assert "flow_reports" in json_res_body["data"]
    assert isinstance(json_res_body["data"]["flow_reports"], list)

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

    obj_keys = set(json_res_body["data"]["flow_report"])
    assert obj_keys == {
        "title",
        "regulation_id",
        "code",
        "sub_sections",
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

    obj_keys = set(json_res_body["data"]["flow_report"])
    assert obj_keys == {
        "title",
        "regulation_id",
        "code",
        "sub_sections",
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
    flow_report = get_database["flow_reports"].find_one_and_delete({"_id": ObjectId(report_id)})
    assert flow_report["_id"]