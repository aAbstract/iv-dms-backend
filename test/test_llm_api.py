import json
import requests
import os
from bson import ObjectId
import _test_config
from dotenv import load_dotenv
from models.gpt_35t import GPT35TAuditTag
from time import sleep
import logging

load_dotenv()


LLM_SCORE_TH = 0.4


def test_llm_api_lock():
    api_url = f"{_test_config.get_api_url()}/llm/iosa-audit"
    http_headers = {"X-Auth": "Bearer fake_token"}
    http_res = requests.post(
        api_url,
        headers=http_headers,
        json={
            "regulation_id": "000000000000000000000000",
            "checklist_code": "XXX 0.0.0",
            "text": "some text",
        },
    )
    assert http_res.status_code == 403
    json_res_body = json.loads(http_res.content.decode())
    assert (
        not json_res_body["success"]
        and json_res_body["msg"] == "Unauthorized API Access [Invalid Token]"
    )


def test_llm_api_success():
    access_token = _test_config.login_user("cwael", "CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV")
    http_headers = {"X-Auth": f"Bearer {access_token}"}

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

    # call llm api
    api_url = f"{_test_config.get_api_url()}/llm/iosa-audit"
    http_res = requests.post(
        api_url,
        headers=http_headers,
        json={
            "regulation_id": regulation_id,
            "checklist_code": "FLT 2.1.35",
            "text": _test_config.example_prompt,
        },
    )
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert "llm_resp" in json_res_body["data"]
    obj_keys = set(json_res_body["data"]["llm_resp"])
    assert obj_keys == {
        "score_tag",
        "details",
        "score_text",
        "comments",
        "suggestions",
        "modified",
        "score",
        "pct_score",
    }


def test_llm_api_success_low_score():
    access_token = _test_config.login_user("cwael", "CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV")
    http_headers = {"X-Auth": f"Bearer {access_token}"}

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

    # call llm api
    api_url = f"{_test_config.get_api_url()}/llm/iosa-audit"
    http_res = requests.post(
        api_url,
        headers=http_headers,
        json={
            "regulation_id": regulation_id,
            "checklist_code": "FLT 2.1.35",
            "text": _test_config.dummy_prompt,
        },
    )
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert "llm_resp" in json_res_body["data"]
    obj_keys = set(json_res_body["data"]["llm_resp"])
    assert obj_keys == {
        "score_tag",
        "details",
        "score_text",
        "comments",
        "suggestions",
        "modified",
        "score",
        "pct_score",
    }
    assert json_res_body["data"]["llm_resp"]["pct_score"] < LLM_SCORE_TH


def test_llm_api_success_high_score():
    access_token = _test_config.login_user("cwael", "CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV")
    http_headers = {"X-Auth": f"Bearer {access_token}"}

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

    # call llm api
    api_url = f"{_test_config.get_api_url()}/llm/iosa-audit"
    http_res = requests.post(
        api_url,
        headers=http_headers,
        json={
            "regulation_id": regulation_id,
            "checklist_code": "FLT 3.1.1",
            "text": _test_config.valid_prompt,
        },
    )
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert "llm_resp" in json_res_body["data"]
    obj_keys = set(json_res_body["data"]["llm_resp"])
    assert obj_keys == {
        "score_tag",
        "details",
        "score_text",
        "comments",
        "suggestions",
        "modified",
        "score",
        "pct_score",
    }
    assert json_res_body["data"]["llm_resp"]["pct_score"] > (1 - LLM_SCORE_TH)


def test_llm_unstruct_api_success_high_score():
    access_token = _test_config.login_user("cwael", "CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV")
    http_headers = {"X-Auth": f"Bearer {access_token}"}
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

    # call audit llm api
    api_url = f"{_test_config.get_api_url()}/llm/iosa-audit-unstruct"
    http_res = requests.post(
        api_url,
        headers=http_headers,
        json={
            "regulation_id": regulation_id,
            "checklist_code": "FLT 3.1.1",
            "text": _test_config.valid_prompt,
        },
    )
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert "llm_resp" in json_res_body["data"]
    assert "overall_compliance_score" in json_res_body["data"]
    assert "context_id" in json_res_body["data"]
    assert json_res_body["data"]["overall_compliance_score"] > (
        (1 - LLM_SCORE_TH) * 100
    )
    old_ocs = json_res_body["data"]["overall_compliance_score"]
    assert json_res_body["data"]["overall_compliance_tag"]

    # call enhance llm api
    api_url = f"{_test_config.get_api_url()}/llm/iosa-enhance-unstruct"
    context_id = json_res_body["data"]["context_id"]

    payload = {
        "context_id": context_id,
        "overall_compliance_tag": GPT35TAuditTag.PARTIALLY_COMPLIANT,
        "regulation_id": regulation_id,
        "checklist_code": "FLT 3.1.1",
    }

    http_res = requests.post(api_url, headers=http_headers, json=payload)
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert "llm_resp" in json_res_body["data"]
    assert "overall_compliance_score" in json_res_body["data"]
    assert "overall_compliance_tag" in json_res_body["data"]
    assert json_res_body["data"]["overall_compliance_tag"] in (
        "Fully Compliant",
        "Partially Compliant",
        "Non Compliant",
    )

    assert "context_id" in json_res_body["data"]
    new_ocs = json_res_body["data"]["overall_compliance_score"]
    assert new_ocs > old_ocs

    get_database.get_collection("gpt35t_contexts").find_one_and_delete(
        {"_id": ObjectId(json_res_body["data"]["context_id"])}
    )
    # TODO-LATER: validate gpt35t context structure


def test_llm_pages_api_success_high_score():
    if not int(os.environ["GPT_35T_ENABLE"]):
        return

    admin_access_token = _test_config.login_user(
        "eslam", "CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV"
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

    # get file
    file_1 = get_database["fs_index"].find_one({"filename": "nesma_oma_ch1.pdf"})

    # call llm api
    api_url = f"{_test_config.get_api_url()}/llm/iosa-audit-pages"
    http_res = requests.post(
        api_url,
        headers=http_headers,
        json={
            "regulation_id": regulation_id,
            "checklist_code": "FLT 3.1.1",
            "pagesMapper": {file_1["doc_uuid"]: [45]},
        },
    )

    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert "llm_resp" in json_res_body["data"]
    assert "overall_compliance_score" in json_res_body["data"]
    assert "context_id" in json_res_body["data"]
    assert json_res_body["data"]["overall_compliance_score"] > (
        (1 - LLM_SCORE_TH) * 100
    )
    assert json_res_body["data"]["overall_compliance_tag"]
    get_database.get_collection("gpt35t_contexts").find_one_and_delete(
        {"_id": ObjectId(json_res_body["data"]["context_id"])}
    )


def test_llm_pages_api_combined_low_score():
    if not int(os.environ["GPT_35T_ENABLE"]):
        return

    admin_access_token = _test_config.login_user(
        "eslam", "CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV"
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

    # get file
    file_1 = get_database["fs_index"].find_one({"filename": "nesma_oma_ch2.pdf"})
    file_2 = get_database["fs_index"].find_one({"filename": "nesma_oma_ch3.pdf"})

    # call llm api
    api_url = f"{_test_config.get_api_url()}/llm/iosa-audit-pages"
    http_res = requests.post(
        api_url,
        headers=http_headers,
        json={
            "regulation_id": regulation_id,
            "checklist_code": "FLT 2.1.35",
            "pagesMapper": {
                file_1["doc_uuid"]: [10],
                file_2["doc_uuid"]: [10],
            },
        },
    )

    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert "llm_resp" in json_res_body["data"]
    assert "overall_compliance_score" in json_res_body["data"]
    assert "context_id" in json_res_body["data"]
    assert json_res_body["data"]["overall_compliance_score"] <= (LLM_SCORE_TH * 100)
    assert json_res_body["data"]["overall_compliance_tag"]
    get_database.get_collection("gpt35t_contexts").find_one_and_delete(
        {"_id": ObjectId(json_res_body["data"]["context_id"])}
    )


def test_llm_unstruct_generate():
    access_token = _test_config.login_user("cwael", "CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV")
    http_headers = {"X-Auth": f"Bearer {access_token}"}
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

    # call audit llm api
    api_url = f"{_test_config.get_api_url()}/llm/iosa-audit-unstruct"
    http_res = requests.post(
        api_url,
        headers=http_headers,
        json={
            "regulation_id": regulation_id,
            "checklist_code": "FLT 3.1.1",
            "text": _test_config.valid_prompt,
        },
    )
    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert "llm_resp" in json_res_body["data"]
    assert "overall_compliance_score" in json_res_body["data"]
    assert json_res_body["data"]["overall_compliance_tag"]
    assert "context_id" in json_res_body["data"]

    assert json_res_body["data"]["overall_compliance_score"] > (
        (1 - LLM_SCORE_TH) * 100
    )
    old_ocs = json_res_body["data"]["overall_compliance_score"]
    assert json_res_body["data"]["overall_compliance_score"]
    assert json_res_body["data"]["overall_compliance_tag"] in (
        "Fully Compliant",
        "Partially Compliant",
        "Non Compliant",
    )

    other_context = json_res_body["data"]["context_id"]

    # call generate llm api
    api_url = f"{_test_config.get_api_url()}/llm/iosa-enhance-unstruct"

    payload = {
        "context_id": other_context,
        "overall_compliance_tag": GPT35TAuditTag.NON_COMPLIANT,
        "regulation_id": regulation_id,
        "checklist_code": "FLT 3.1.1",
    }

    http_res = requests.post(api_url, headers=http_headers, json=payload)

    assert http_res.status_code == 200
    json_res_body = json.loads(http_res.content.decode())
    assert "llm_resp" in json_res_body["data"]
    assert "overall_compliance_score" in json_res_body["data"]
    assert "overall_compliance_tag" in json_res_body["data"]
    assert "context_id" in json_res_body["data"]

    assert json_res_body["data"]["overall_compliance_tag"] in (
        "Fully Compliant",
        "Partially Compliant",
        "Non Compliant",
    )

    new_ocs = json_res_body["data"]["overall_compliance_score"]
    assert new_ocs >= old_ocs

    get_database.get_collection("gpt35t_contexts").find_one_and_delete(
        {"_id": ObjectId(json_res_body["data"]["context_id"])}
    )
    get_database.get_collection("gpt35t_contexts").find_one_and_delete(
        {"_id": ObjectId(other_context)}
    )

    # TODO-LATER: validate gpt35t context structure

def _test_llm_stress_fully_compliant():
    
    access_token = _test_config.login_user("cwael", "CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV")
    http_headers = {"X-Auth": f"Bearer {access_token}"}
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

    correct = []
    average = []
    for text in _test_config.full_compliant_text:
        # call audit llm api
        api_url = f"{_test_config.get_api_url()}/llm/iosa-audit-unstruct"
        http_res = requests.post(
            api_url,
            headers=http_headers,
            json={
                "regulation_id": regulation_id,
                "checklist_code": "FLT 3.1.1",
                "text": text,
            },
        )
        if(http_res.status_code == 200):
            json_res_body = json.loads(http_res.content.decode())
            
            assert "overall_compliance_score" in json_res_body["data"]
            assert "context_id" in json_res_body["data"]
            if(json_res_body["data"]["overall_compliance_tag"] in ["Non Compliant", "Partially Compliant","Fully Compliant"]):
                correct.append(json_res_body["data"]["overall_compliance_tag"])
                average.append(json_res_body["data"]["overall_compliance_score"])
            else:    
                correct.append("Failed")
                average.append(sum(average) // len(average))
        else:
            correct.append("Failed")
            average.append(sum(average) // len(average))


    benchmark = {
        "percentage":correct.count("Fully Compliant") / len(correct),
        "threshold":sum(average) // len(average),
        "count":len(correct),
        "correct":correct.count("Fully Compliant") ,
        "incorrect": len(correct) - correct.count("Fully Compliant"),
        "Failed":correct.count("Failed"),
        "Fully Compliant":correct.count("Fully Compliant"),
        "Partially Compliant":correct.count("Partially Compliant"),
        "Non Compliant":correct.count("Non Compliant"),
    }

    file_path = r"data/llm_benchmarks/FLT 3.1.1/improved/fully_compliant.json"

    # Writing dictionary object to JSON file
    with open(file_path, "w") as json_file:
        json.dump(benchmark, json_file)

def _test_llm_stress_partially_compliant():

    access_token = _test_config.login_user("cwael", "CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV")
    http_headers = {"X-Auth": f"Bearer {access_token}"}
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

    correct = []
    average = []

    for text in _test_config.partial_compliant_text:
        # call audit llm api
        api_url = f"{_test_config.get_api_url()}/llm/iosa-audit-unstruct"
        http_res = requests.post(
            api_url,
            headers=http_headers,
            json={
                "regulation_id": regulation_id,
                "checklist_code": "FLT 3.1.1",
                "text": text,
            },
        )
        if(http_res.status_code == 200):
            json_res_body = json.loads(http_res.content.decode())
            
            assert "overall_compliance_score" in json_res_body["data"]
            assert "context_id" in json_res_body["data"]
            if(json_res_body["data"]["overall_compliance_tag"] in["Non Compliant", "Partially Compliant","Fully Compliant"]):
                correct.append(json_res_body["data"]["overall_compliance_tag"] )
                average.append(json_res_body["data"]["overall_compliance_score"])

            else:    
                average.append(sum(average) // len(average))
                correct.append("Failed")
        else:
            correct.append("Failed")
            average.append(sum(average) // len(average))


    benchmark = {
        "percentage":correct.count("Partially Compliant") / len(correct),
        "threshold":sum(average) // len(average),
        "count":len(correct),
        "correct":correct.count("Partially Compliant") ,
        "incorrect": len(correct) - correct.count("Partially Compliant"),
        "Failed":correct.count("Failed"),
        "Fully Compliant":correct.count("Fully Compliant"),
        "Partially Compliant":correct.count("Partially Compliant"),
        "Non Compliant":correct.count("Non Compliant"),
    }

    file_path = r"data/llm_benchmarks/FLT 3.1.1/improved/partially_compliant.json"

    # Writing dictionary object to JSON file
    with open(file_path, "w") as json_file:
        json.dump(benchmark, json_file)

def _test_llm_stress_non_compliant():
    access_token = _test_config.login_user("cwael", "CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV")
    http_headers = {"X-Auth": f"Bearer {access_token}"}
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
    average = []
    correct = []
    for text in _test_config.non_compliant_text:
        # call audit llm api
        api_url = f"{_test_config.get_api_url()}/llm/iosa-audit-unstruct"
        http_res = requests.post(
            api_url,
            headers=http_headers,
            json={
                "regulation_id": regulation_id,
                "checklist_code": "FLT 3.1.1",
                "text": text,
            },
        )
        if(http_res.status_code == 200):
            json_res_body = json.loads(http_res.content.decode())
            
            assert "overall_compliance_score" in json_res_body["data"]
            assert "context_id" in json_res_body["data"]
            if(json_res_body["data"]["overall_compliance_tag"] in["Non Compliant", "Partially Compliant","Fully Compliant"]):
                correct.append(json_res_body["data"]["overall_compliance_tag"] )
                average.append(json_res_body["data"]["overall_compliance_score"])

            else:    
                average.append(sum(average) // len(average))
                correct.append("Failed")
        else:
            average.append(sum(average) // len(average))
            correct.append("Failed")

    benchmark = {
        "percentage":correct.count("Non Compliant") / len(correct),
        "threshold":sum(average) // len(average),
        "count":len(correct),
        "correct":correct.count("Non Compliant") ,
        "incorrect": len(correct) - correct.count("Non Compliant"),
        "Failed":correct.count("Failed"),
        "Fully Compliant":correct.count("Fully Compliant"),
        "Partially Compliant":correct.count("Partially Compliant"),
        "Non Compliant":correct.count("Non Compliant"),
    }

    file_path = r"data/llm_benchmarks/FLT 3.1.1/improved/non_compliant.json"

    # Writing dictionary object to JSON file
    with open(file_path, "w") as json_file:
        json.dump(benchmark, json_file)
