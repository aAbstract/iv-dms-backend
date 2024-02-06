from bson import ObjectId
import json
import requests
import _test_config
from models.flow_report import (FinalComment, FlowReportChange, FlowReportStatus,
    FlowStageTemplateMap, UserChangeType)
from datetime import datetime


def test_create_flow_report_lock():
    api_url = f"{_test_config.get_api_url()}/flow_report/list-flow-report"
    http_headers = {"X-Auth": "Bearer fake_token"}
    http_res = requests.post(api_url, headers=http_headers)
    assert http_res.status_code == 403
    json_res_body = json.loads(http_res.content.decode())
    assert (
        not json_res_body["success"]
        and json_res_body["msg"] == "Unauthorized API Access [Invalid Token]"
    )

    user_access_token = _test_config.login_user(
        "sam", "CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV"
    )
    http_headers = {"X-Auth": f"Bearer {user_access_token}"}
    http_res = requests.post(api_url, headers=http_headers)
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
        "flow_stage_template": FlowStageTemplateMap.STAGES_4["name"],
        "start_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
        "end_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
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
        "flow_stages",
        "status",
        "current_stage_index",
        "start_date",
        "end_date",
        "organization",
        "_id",
        "creator"
    }
    assert json_res_body["data"]["flow_report"]["title"] == "Test Title"

    # reset flow report
    flow_report_change = get_database["flow_report_changes"].find_one(
        {"report_id": str(json_res_body["data"]["flow_report"]["_id"])}
    )
    assert "user_changes" in flow_report_change
    assert 1 == len(flow_report_change["user_changes"])
    assert flow_report_change["user_changes"][0]["change_type"] == "CREATE"
    flow_report_change = get_database["flow_report_changes"].find_one_and_delete(
        {"report_id": str(json_res_body["data"]["flow_report"]["_id"])}
    )

    flow_report = get_database["flow_reports"].find_one_and_delete(
        {"_id": ObjectId(json_res_body["data"]["flow_report"]["_id"])}
    )
    assert flow_report["_id"]


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

    http_res = requests.post(api_url, headers=http_headers)

    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body["success"]
    assert "flow_report" in json_res_body["data"]
    assert isinstance(json_res_body["data"]["flow_report"], list)


def test_get_flow_report_history():
    admin_access_token = _test_config.login_user(
        "cwael", "CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV"
    )
    http_headers = {"X-Auth": f"Bearer {admin_access_token}"}

    # get flow report id
    get_database = _test_config.get_database()
    assert get_database != None

    flow_report = get_database["flow_reports"].find_one(
        {"title": FlowStageTemplateMap.STAGES_4["name"]}
    )
    assert flow_report["_id"]

    payload = {"flow_report_id": str(flow_report["_id"])}

    # test api
    api_url = f"{_test_config.get_api_url()}/flow_report/get-flow-report-history"

    http_res = requests.post(api_url, headers=http_headers, json=payload)

    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body["success"]
    assert "user_changes" in json_res_body["data"]
    assert isinstance(json_res_body["data"]["user_changes"], list)

    obj_keys = set(json_res_body["data"]["user_changes"][0])
    assert obj_keys == {
        "user_name",
        "user_comment",
        "change_type",
        "report_after",
        "date",
    }
    assert json_res_body["data"]["user_changes"][0]["change_type"] == "CREATE"


def test_get_flow_report():
    admin_access_token = _test_config.login_user(
        "cwael", "CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV"
    )
    http_headers = {"X-Auth": f"Bearer {admin_access_token}"}

    # get flow report id
    get_database = _test_config.get_database()
    assert get_database != None

    flow_report = get_database["flow_reports"].find_one(
        {"title": FlowStageTemplateMap.STAGES_4["name"]}
    )
    assert "_id" in flow_report

    # get activity change before
    flow_report_change = get_database["flow_report_changes"].find_one(
        {"report_id": str(flow_report["_id"])}
    )
    assert "user_changes" in flow_report_change
    change_size = len(flow_report_change["user_changes"])

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
        "flow_stages",
        "status",
        "current_stage_index",
        "start_date",
        "end_date",
        "organization",
        "applicability",
        "guidance",
        "_id",
        "creator"
    }

    # reset flow report
    flow_report_change = get_database["flow_report_changes"].find_one(
        {"report_id": str(flow_report["_id"])}
    )
    assert "user_changes" in flow_report_change
    assert change_size + 1 == len(flow_report_change["user_changes"])
    assert flow_report_change["user_changes"][-1]["change_type"] == "VIEW"
    _ = get_database["flow_report_changes"].update_one(
        {"report_id": str(flow_report["_id"])}, {"$pop": {"user_changes": 1}}
    )


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
        "flow_stage_template": FlowStageTemplateMap.STAGES_4["name"],
        "start_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
        "end_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
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
        "flow_stages",
        "status",
        "current_stage_index",
        "start_date",
        "end_date",
        "organization",
        "_id",
        "creator"
    }
    assert json_res_body["data"]["flow_report"]["title"] == "Test Title"

    # check activity flow report
    flow_report_change = get_database["flow_report_changes"].find_one(
        {"report_id": str(json_res_body["data"]["flow_report"]["_id"])}
    )
    assert "user_changes" in flow_report_change
    assert 1 == len(flow_report_change["user_changes"])
    assert flow_report_change["user_changes"][0]["change_type"] == "CREATE"

    # delete flow report
    # test api
    api_url = f"{_test_config.get_api_url()}/flow_report/delete-flow-report"

    report_id = json_res_body["data"]["flow_report"]["_id"]
    payload = {"flow_report_id": str(report_id), "comment": "Test Delete"}
    print(payload)
    http_res = requests.post(api_url, headers=http_headers, json=payload)

    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body["success"]

    flow_report = get_database["flow_reports"].find_one({"_id": report_id})
    assert flow_report == None

    # check activity flow report
    flow_report_change = get_database["flow_report_changes"].find_one(
        {"report_id": str(report_id)}
    )
    assert "user_changes" in flow_report_change
    assert 2 == len(flow_report_change["user_changes"])
    assert flow_report_change["user_changes"][1]["change_type"] == "DELETE"
    assert flow_report_change["user_changes"][1]["user_comment"] == "Test Delete"

    flow_report_change = get_database["flow_report_changes"].find_one_and_delete(
        {"report_id": str(report_id)}
    )


def test_forward_flow_report():
    admin_access_token = _test_config.login_user(
        "cwael", "CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV"
    )
    http_headers = {"X-Auth": f"Bearer {admin_access_token}"}

    # get flow report id
    get_database = _test_config.get_database()
    assert get_database != None

    flow_report = get_database["flow_reports"].find_one(
        {"title": FlowStageTemplateMap.STAGES_4["name"]}
    )
    assert "_id" in flow_report

    # get activity change before
    flow_report_change = get_database["flow_report_changes"].find_one(
        {"report_id": str(flow_report["_id"])}
    )
    assert "user_changes" in flow_report_change
    change_size = len(flow_report_change["user_changes"])

    payload = {
        "flow_report_id": str(flow_report["_id"]),
        "comment": "I will forward",
        "user_forward": "cwael",
    }

    # test api
    api_url = f"{_test_config.get_api_url()}/flow_report/forward-flow-report"

    http_res = requests.post(api_url, headers=http_headers, json=payload)

    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body["success"]

    # reset flow report
    flow_report_change = get_database["flow_report_changes"].find_one(
        {"report_id": str(flow_report["_id"])}
    )
    assert "user_changes" in flow_report_change
    assert change_size + 1 == len(flow_report_change["user_changes"])
    assert flow_report_change["user_changes"][-1]["change_type"] == "FORWARD"
    _ = get_database["flow_report_changes"].update_one(
        {"report_id": str(flow_report["_id"])}, {"$pop": {"user_changes": 1}}
    )


def test_get_flow_report_stage_template_options():
    admin_access_token = _test_config.login_user(
        "cwael", "CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV"
    )
    http_headers = {"X-Auth": f"Bearer {admin_access_token}"}

    payload = {"template_name": FlowStageTemplateMap.STAGES_4["name"]}

    # test api
    api_url = f"{_test_config.get_api_url()}/flow_report/get-flow-report-stage-template-options"

    http_res = requests.post(api_url, headers=http_headers, json=payload)

    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body["success"]
    assert "templates" in json_res_body["data"]
    obj_keys = set(json_res_body["data"]["templates"][0])
    assert obj_keys == {"stages", "name"}


def test_update_flow_report_status():
    admin_access_token = _test_config.login_user(
        "cwael", "CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV"
    )
    http_headers = {"X-Auth": f"Bearer {admin_access_token}"}

    # get flow report id
    get_database = _test_config.get_database()
    assert get_database != None

    flow_report = get_database["flow_reports"].find_one(
        {"title": FlowStageTemplateMap.STAGES_4["name"]}
    )
    assert "_id" in flow_report

    # get activity change before
    flow_report_change = get_database["flow_report_changes"].find_one(
        {"report_id": str(flow_report["_id"])}
    )
    assert "user_changes" in flow_report_change
    change_size = len(flow_report_change["user_changes"])

    # get status before change
    assert "status" in flow_report
    before_status = flow_report["status"]
    assert before_status == FlowReportStatus.INPROGRESS

    payload = {
        "status": FlowReportStatus.CLOSED,
        "flow_report_id": str(flow_report["_id"]),
        "comment": "Test Comment",
    }

    # test api
    api_url = f"{_test_config.get_api_url()}/flow_report/update-flow-report-status"

    http_res = requests.post(api_url, headers=http_headers, json=payload)

    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert json_res_body["success"]

    # get status after change
    flow_report = get_database["flow_reports"].find_one(
        {"title": FlowStageTemplateMap.STAGES_4["name"]}
    )
    assert "_id" in flow_report
    assert "status" in flow_report
    after_status = flow_report["status"]
    assert after_status == FlowReportStatus.CLOSED

    # check user change object after
    flow_report_change = get_database["flow_report_changes"].find_one(
        {"report_id": str(flow_report["_id"])}
    )
    assert "user_changes" in flow_report_change
    assert change_size + 1 == len(flow_report_change["user_changes"])
    assert (
        flow_report_change["user_changes"][-1]["change_type"] == UserChangeType.UPDATE
    )
    assert flow_report_change["user_changes"][-1]["user_comment"] == "Test Comment"

    # reset
    _ = get_database["flow_report_changes"].update_one(
        {"report_id": str(flow_report["_id"])}, {"$pop": {"user_changes": 1}}
    )
    _ = get_database["flow_reports"].update_one(
        {"_id": flow_report["_id"]}, {"$set": {"status": FlowReportStatus.INPROGRESS}}
    )


def test_update_flow_report_sub_sections():
    admin_access_token = _test_config.login_user(
        "cwael", "CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV"
    )
    http_headers = {"X-Auth": f"Bearer {admin_access_token}"}

    # get flow report id
    get_database = _test_config.get_database()
    assert get_database != None

    flow_report = get_database["flow_reports"].find_one(
        {"title": FlowStageTemplateMap.STAGES_4["name"]}
    )
    assert "_id" in flow_report
    assert "sub_sections" in flow_report
    sub_sections_before = flow_report["sub_sections"]

    # get activity change before
    flow_report_change = get_database["flow_report_changes"].find_one(
        {"report_id": str(flow_report["_id"])}
    )

    assert "user_changes" in flow_report_change
    change_size = len(flow_report_change["user_changes"])

    # get status before change

    payload = {
        "sub_sections": [
            {
                "title": "Section 1",
                "checklist_items": [
                    {
                        "code": "FLT 1.2.1",
                        "manual_references": [
                            {"check_in_code": "OMA 2.1.2", "description": "NeW DESC"}
                        ],
                        "final_comment": FinalComment.DOCNOTIMP,
                        "comments": "Test Comment",
                        "actions": "Test actions",
                    }
                ],
            }
        ],
        "flow_report_id": str(flow_report["_id"]),
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
        {"title": FlowStageTemplateMap.STAGES_4["name"]}
    )
    assert "_id" in flow_report
    assert "sub_sections" in flow_report

    assert flow_report['sub_sections'][0]['checklist_items'][0]['manual_references'][0] == {"check_in_code": "OMA 2.1.2", "description": "NeW DESC"}
    assert flow_report['sub_sections'][0]['checklist_items'][0]['final_comment'] == FinalComment.DOCNOTIMP
    assert flow_report['sub_sections'][0]['checklist_items'][0]['comments'] == "Test Comment"
    assert flow_report['sub_sections'][0]['checklist_items'][0]['actions'] == "Test actions"

    # check user change object after
    flow_report_change = get_database["flow_report_changes"].find_one(
        {"report_id": str(flow_report["_id"])}
    )
    assert "user_changes" in flow_report_change
    assert change_size + 1 == len(flow_report_change["user_changes"])
    assert (
        flow_report_change["user_changes"][-1]["change_type"] == UserChangeType.UPDATE
    )
    assert flow_report_change["user_changes"][-1]["user_comment"] == "Test Comment"

    # reset
    _ = get_database["flow_report_changes"].update_one(
        {"report_id": str(flow_report["_id"])}, {"$pop": {"user_changes": 1}}
    )
    _ = get_database["flow_reports"].update_one(
        {"_id": flow_report["_id"]}, {"$set": {"sub_sections": sub_sections_before}}
    )
