from bson import ObjectId
from models.runtime import ServiceResponse
from database.mongo_driver import get_database
from models.flow_reports import (
    Airline,
    FlowReport,
    FlowReportStatus,
    ReportItem,
    ReportSubSectionWritten,
    UserChange,
    UserChangeType,
)
from database.mongo_driver import get_database, validate_bson_id
from models.regulations import IOSASection, RegulationType
from models.users import UserRole


async def create_flow_report_db(
    regulation_id: str,
    title: str,
    checklist_template_code: str,
    organization: str,
    username: str,
    airline_id: str
) -> ServiceResponse:

    bson_id = validate_bson_id(regulation_id)
    if not bson_id:
        return ServiceResponse(success=False, msg="Bad Regulation ID", status_code=400)

    # get type from regulation
    regulation = (
        await get_database().get_collection("regulations").find_one({"_id": bson_id})
    )
    if not regulation:
        return ServiceResponse(
            success=False, msg="This Regulation ID doesn't exist", status_code=404
        )

    if not (regulation["type"] in RegulationType.__members__.values()):
        return ServiceResponse(
            success=False, msg="Bad Regulation Type", status_code=400
        )
    # get IOSA section
    if " " not in checklist_template_code:
        return ServiceResponse(
            success=False, msg="Bad Checklist Template Code", status_code=400
        )

    section_code, _ = checklist_template_code.split(" ")

    iosa_section = (
        await get_database()
        .get_collection("regulations")
        .find_one(
            {"_id": bson_id, "sections.code": section_code},
            projection={"_id": 0, "sections.$": 1},
        )
    )

    if not iosa_section:
        return ServiceResponse(
            success=False, msg="Regulation Checklist Code not Found", status_code=404
        )

    if len(iosa_section["sections"]) > 1:
        return ServiceResponse(
            success=False,
            msg="Multiple Regulation Checklist Codes were Found",
            status_code=400,
        )

    iosa_section = IOSASection.model_validate(iosa_section["sections"][0])

    # validate airline
    if username:
        user = await get_database().get_collection("users").find_one({"username": username})

        if not user:
            return ServiceResponse(success=False, msg="This Username Doesn't exist", status_code=404)

        if user['user_role'] == UserRole.AIRLINES:
            airline_id = user['airline']

    airline_id = validate_bson_id(airline_id)
    if not airline_id:
        return ServiceResponse(success=False, msg="Bad Airline ID", status_code=400)

    # get airline
    airline = await get_database().get_collection("airlines").find_one({"_id": airline_id})

    if not airline:
        return ServiceResponse(
            success=False, msg="This airline ID doesn't exist", status_code=404
        )

    if airline['organization'] != organization:
        return ServiceResponse(
            success=False, msg="Your organization can't access this airline", status_code=403
        )

    # construct flow report
    flow_report = FlowReport(
        title=title,
        regulation_id=regulation_id,
        code=checklist_template_code,
        sub_sections=[],
        status=FlowReportStatus.INPROGRESS,
        organization=organization,
        airline=str(airline['_id']),
        creator=username,
        user_changes=[
            UserChange(
                user_name=username,
                user_comment="",
                change_type=UserChangeType.CREATE,
            )
        ],
    )

    sub_section_iosa_item_map = {}
    for item in iosa_section.items:
        # the dot here prevents the match between flt 1 and flt 11.1
        # where flt 11.1 doesn't start with  "flt 1."
        # bug flt 11.1 starts with  "flt 1" which is incorrect

        if item.code.startswith(checklist_template_code+".") or ("Table" in item.code):

            sub_section_title = item.iosa_map[-1]

            if not sub_section_title in sub_section_iosa_item_map:
                sub_section_iosa_item_map[sub_section_title] = []
            sub_section_iosa_item_map[sub_section_title].append(
                ReportItem(code=item.code, page=item.page)
            )

    flow_report.sub_sections = [
        ReportSubSectionWritten(
            title=sub_section_header,
            checklist_items=iosa_codes,
        )
        for sub_section_header, iosa_codes in sub_section_iosa_item_map.items()
    ]

    flow_report = FlowReport.model_validate(flow_report)
    flow_report_dict = flow_report.model_dump()

    mdb_result = (
        await get_database().get_collection("flow_reports").insert_one(flow_report_dict)
    )

    flow_report_dict["_id"] = str(mdb_result.inserted_id)
    airline["id"] = str(airline["_id"])
    del airline["_id"]
    flow_report_dict["airline"] = airline
    del flow_report_dict["sub_sections"]

    return ServiceResponse(data={"flow_report": flow_report_dict})


async def list_flow_report_db(organization: str, username: str = "") -> ServiceResponse:

    query = {"organization": organization}

    if username:
        user = await get_database().get_collection("users").find_one({"username": username})

        if not user:
            return ServiceResponse(success=False, msg="This Username Doesn't exist", status_code=404)

        if user['user_role'] == UserRole.AIRLINES:
            query['airline'] = user['airline']

    flow_reports = [
        report
        async for report in get_database()
        .get_collection("flow_reports")
        .find(query)
        if report.get("status") != FlowReportStatus.DELETED
    ]

    for report in range(len(flow_reports)):

        flow_reports[report]["id"] = str(flow_reports[report]["_id"])
        del flow_reports[report]["_id"]

        regulation = await get_database().get_collection('regulations').find_one({'_id': ObjectId(flow_reports[report]["regulation_id"])})

        flow_reports[report]["regulation_id"] = str(
            flow_reports[report]["regulation_id"])

        flow_reports[report]["type"] = regulation['type']

        airline = await get_database().get_collection("airlines").find_one({"_id": ObjectId(flow_reports[report]["airline"])})
        if not airline:
            return ServiceResponse(
                success=False,
                msg="Airline id couln't be found",
                status_code=400,
            )

        airline["id"] = str(airline["_id"])
        del airline["_id"]
        FlowReport.model_validate(flow_reports[report])

        flow_reports[report]["airline"] = airline
        del flow_reports[report]["sub_sections"]

    return ServiceResponse(data={"flow_reports": flow_reports})


async def delete_flow_report_db(
    username: str, user_comment: str, flow_report_id: str, organization: str
) -> ServiceResponse:

    bson_id = validate_bson_id(flow_report_id)
    if not bson_id:
        return ServiceResponse(success=False, msg="Bad flow report ID", status_code=400)

    flow_report = (
        await get_database().get_collection("flow_reports").find_one({"_id": bson_id})
    )

    if not flow_report:
        return ServiceResponse(
            success=False, msg="This flow report ID doesn't exist", status_code=404
        )

    if flow_report["organization"] != organization:
        return ServiceResponse(
            success=False,
            status_code=403,
            msg="Your organization can't delete this flow report",
        )

    # create flow report user change
    user_change = UserChange(
        user_name=username,
        user_comment=user_comment,
        change_type=UserChangeType.DELETE,
    )

    await get_database().get_collection("flow_reports").update_one(
        {"_id": bson_id},
        {
            "$set": {"status": FlowReportStatus.DELETED},
            "$push": {"user_changes": user_change.model_dump()},
        },
    )

    return ServiceResponse()


async def get_flow_report_db(
    flow_report_id: str, organization: str, username: str
) -> ServiceResponse:

    bson_id = validate_bson_id(flow_report_id)
    if not bson_id:
        return ServiceResponse(success=False, msg="Bad flow report ID", status_code=400)

    flow_report = (
        await get_database().get_collection("flow_reports").find_one({"_id": bson_id})
    )

    if not flow_report:
        return ServiceResponse(
            success=False, msg="This flow report ID doesn't exist", status_code=404
        )

    # get type from regulation
    regulation = (
        await get_database().get_collection("regulations").find_one({"_id": ObjectId(flow_report["regulation_id"])})
    )
    if not regulation:
        return ServiceResponse(
            success=False, msg="This Regulation ID doesn't exist", status_code=404
        )

    flow_report["_id"] = str(flow_report["_id"])
    flow_report["regulation_id"] = str(flow_report["regulation_id"])

    flow_report = FlowReport.model_validate(flow_report).model_dump()

    if flow_report["organization"] != organization:
        return ServiceResponse(
            success=False,
            status_code=403,
            msg="Your organization can't access this flow report",
        )

    user = await get_database().get_collection("users").find_one({"username": username})

    if user['user_role'] == UserRole.AIRLINES:
        if user['airline'] != flow_report['airline']:
            return ServiceResponse(
                success=False,
                status_code=403,
                msg="Your User Airline Account Can't Access this Report",
            )

    section_code = flow_report["code"].split()[0]

    # get applicability and general guidence
    iosa_section = (
        await get_database()
        .get_collection("regulations")
        .find_one(
            {
                "_id": ObjectId(flow_report["regulation_id"]),
                "sections.code": section_code,
            },
            projection={"_id": 0, "sections.$": 1},
        )
    )

    if not iosa_section:
        return ServiceResponse(
            success=False, msg="Regulation Checklist Code not Found", status_code=404
        )

    if len(iosa_section["sections"]) > 1:
        return ServiceResponse(
            success=False,
            msg="Multiple Regulation Checklist Codes were Found",
            status_code=400,
        )

    iosa_section = IOSASection.model_validate(iosa_section["sections"][0])

    flow_report["applicability"] = iosa_section.applicability
    flow_report["guidance"] = iosa_section.guidance
    flow_report["_id"] = flow_report_id
    airline = await get_database().get_collection("airlines").find_one({"_id": ObjectId(flow_report["airline"])})
    if not airline:
        return ServiceResponse(
            success=False,
            msg="Airline id couldn't be found",
            status_code=400,
        )
    airline["id"] = str(airline["_id"])
    del airline["_id"]
    flow_report["airline"] = airline

    # create flow report user change
    user_change = UserChange(
        user_name=username,
        user_comment="",
        change_type=UserChangeType.VIEW,
    )

    await get_database().get_collection("flow_reports").update_one(
        {"_id": bson_id}, {"$push": {"user_changes": user_change.model_dump()}}
    )

    return ServiceResponse(data=flow_report)


async def change_flow_report_sub_sections_db(
    flow_report_id: str,
    organization: str,
    username: str,
    sub_sections: list,
    comment: str,
) -> ServiceResponse:

    bson_id = validate_bson_id(flow_report_id)
    if not bson_id:
        return ServiceResponse(success=False, msg="Bad flow report ID", status_code=400)

    flow_report = (
        await get_database().get_collection("flow_reports").find_one({"_id": bson_id})
    )

    if not flow_report:
        return ServiceResponse(
            success=False, msg="This flow report ID doesn't exist", status_code=404
        )

    flow_report = FlowReport.model_validate(flow_report).model_dump()

    if flow_report["organization"] != organization:
        return ServiceResponse(
            success=False,
            status_code=403,
            msg="Your organization can't access this flow report",
        )

    # this check if any mentioned section by the user exists
    # and every checklist the user wants to update exists and raises an error if it doesn't
    # ESLAM: I hope we do not have to debug this section in the future.
    for input_section in sub_sections:
        ReportSubSectionWritten.model_validate(input_section)

        try:
            ReportSubSectionWritten.model_validate(input_section)
        except:
            return ServiceResponse(
                success=False, status_code=400, msg=f"Bad Sub Section"
            )
        found = False
        for i, array_section in enumerate(flow_report["sub_sections"]):
            if input_section["title"] == array_section["title"]:
                found = True
                for input_item in input_section["checklist_items"]:
                    item_found = False
                    for j, array_item in enumerate(array_section["checklist_items"]):
                        if input_item["code"] == array_item["code"]:

                            # check ownership of single attachment
                            if input_item.get("fs_index") != None:
                                fs_index = (
                                    await get_database()
                                    .get_collection("fs_index")
                                    .find_one({"_id": ObjectId(input_item["fs_index"])})
                                )

                                if not fs_index:
                                    return ServiceResponse(
                                        success=False,
                                        status_code=404,
                                        msg=f"{input_item['fs_index']} File Index not Found",
                                    )

                                if fs_index["organization"] != organization:
                                    return ServiceResponse(
                                        success=False,
                                        status_code=403,
                                        msg=f"Your organization can't access this file {input_item['fs_index']}",
                                    )

                            # check ownership of manual refrences
                            for checkin in input_item["checkins"]:

                                # ownership of contexts user based or organization based?
                                # TODO-GALAL
                                context = (
                                    await get_database()
                                    .get_collection("gpt35t_contexts")
                                    .find_one({"_id": ObjectId(checkin["context_id"])})
                                )

                                if not context:
                                    return ServiceResponse(
                                        success=False,
                                        status_code=404,
                                        msg=f"GPT context {checkin['doc_uuid']} not Found",
                                    )

                                if context["organization"] != organization:
                                    return ServiceResponse(
                                        success=False,
                                        status_code=403,
                                        msg=f"You organization can't access this GPT context {checkin['context_id']}",
                                    )

                                for refrence in checkin["manual_references"].values():

                                    fs_index = (
                                        await get_database()
                                        .get_collection("fs_index")
                                        .find_one({"doc_uuid": refrence["doc_uuid"]})
                                    )

                                    if not fs_index:
                                        return ServiceResponse(
                                            success=False,
                                            status_code=404,
                                            msg=f"Doc UUID {refrence['doc_uuid']} not Found",
                                        )

                                    if fs_index["organization"] != organization:
                                        return ServiceResponse(
                                            success=False,
                                            status_code=403,
                                            msg=f"Your organization can't access this file {refrence['doc_uuid']}",
                                        )

                            item_found = True
                            flow_report["sub_sections"][i]["checklist_items"][
                                j
                            ] = input_item
                            break
                    if not item_found:
                        return ServiceResponse(
                            success=False,
                            status_code=404,
                            msg=f"Item with code '{input_item['code']}' not found in '{array_section['title']}' section.",
                        )
                break
        if not found:
            return ServiceResponse(
                success=False,
                status_code=404,
                msg=f"Section {input_section['title']} doesn't exit",
            )

    flow_report = FlowReport.model_validate(flow_report).model_dump()

    user_change = UserChange(
        user_name=username,
        user_comment=comment,
        change_type=UserChangeType.UPDATE,
    ).model_dump()

    flow_report = (
        await get_database()
        .get_collection("flow_reports")
        .find_one_and_update(
            {"_id": bson_id},
            {
                "$set": {"sub_sections": flow_report["sub_sections"]},
                "$push": {"user_changes": user_change},
            },
        )
    )
    FlowReport.model_validate(flow_report)

    airline = await get_database().get_collection("airlines").find_one({"_id": ObjectId(flow_report['airline'])})

    flow_report["_id"] = str(flow_report["_id"])
    del flow_report["sub_sections"]

    airline["id"] = str(airline["_id"])
    del airline["_id"]
    flow_report["airline"] = airline

    return ServiceResponse(data=flow_report)


async def list_airlines_db(organization: str) -> ServiceResponse:

    airlines = [airline async for airline in get_database().get_collection("airlines").find({"organization": organization, "deleted": False}) if Airline.model_validate(airline)]
    for airline in airlines:
        airline["id"] = str(airline["_id"])
        del airline["_id"]
    return ServiceResponse(data={"airlines": airlines})


async def create_airlines_db(organization: str, name: str) -> ServiceResponse:

    if not name:
        return ServiceResponse(
            success=False, status_code=400, msg=f"Can't create empty airline name"
        )
    name = name.strip()

    airline_obj = await get_database().get_collection("airlines").find_one({"organization": organization, "name": name, "deleted": False})

    if airline_obj != None:
        return ServiceResponse(
            success=False, status_code=400, msg=f"Airline Name already Exists"
        )

    airline_obj = await get_database().get_collection("airlines").insert_one(
        Airline(organization=organization, name=name).model_dump()
    )

    return ServiceResponse(data={"airline_id": str(airline_obj.inserted_id)})


async def delete_airlines_db(organization: str, id: str) -> ServiceResponse:

    bson_id = validate_bson_id(id)
    if not bson_id:
        return ServiceResponse(success=False, msg="Bad Airline ID", status_code=400)

    airline_obj = await get_database().get_collection("airlines").find_one({"_id": bson_id})

    if airline_obj == None:
        return ServiceResponse(
            success=False,
            status_code=403,
            msg=f"No airline with this ID",
        )

    await get_database().get_collection("airlines").delete_one({"_id": bson_id})

    return ServiceResponse()
