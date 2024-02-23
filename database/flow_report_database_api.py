from bson import ObjectId
from models.runtime import ServiceResponse
from database.mongo_driver import get_database
from models.flow_reports import (
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

    # construct flow report
    flow_report = FlowReport(
        title=title,
        regulation_id=regulation_id,
        code=checklist_template_code,
        sub_sections=[],
        status=FlowReportStatus.INPROGRESS,
        organization=organization,
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
        if item.code.startswith(checklist_template_code):
            sub_section_title = item.iosa_map[1]

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
    del flow_report_dict["sub_sections"]

    return ServiceResponse(data={"flow_report": flow_report_dict})


async def list_flow_report_db(organization: str, creator: str) -> ServiceResponse:
    
    if creator:
        flow_reports = [
            report
            async for report in get_database()
            .get_collection("flow_reports")
            .find(
                {"organization": organization, "creator": creator}
            )
            if report.get("status") != FlowReportStatus.DELETED
        ]
    else:
        flow_reports = [
            report
            async for report in get_database()
            .get_collection("flow_reports")
            .find({"organization": organization})
            if report.get("status") != FlowReportStatus.DELETED
        ]

    for report in range(len(flow_reports)):
        # TODO-GALAL: fix this later
        flow_reports[report]["id"] = str(flow_reports[report]["_id"])
        del flow_reports[report]["_id"]
        
        flow_reports[report]["regulation_id"] = str(flow_reports[report]["regulation_id"])
        flow_reports[report]['type'] = 'IOSA'  # TODO-LATER: fix this
        FlowReport.model_validate(flow_reports[report])
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
        {"_id": bson_id}, {"$set": {"status": FlowReportStatus.DELETED}, "$push": {"user_changes": user_change.model_dump()}}
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

    flow_report["_id"] = str(flow_report["_id"])
    flow_report["regulation_id"] = str(flow_report["regulation_id"])

    flow_report = FlowReport.model_validate(flow_report).model_dump()

    if flow_report["organization"] != organization:
        return ServiceResponse(
            success=False,
            status_code=403,
            msg="Your organization can't access this flow report",
        )
    # get applicability and general guidence
    iosa_section = (
        await get_database()
        .get_collection("regulations")
        .find_one(
            {
                "_id": ObjectId(flow_report["regulation_id"]),
                "sections.code": flow_report["code"].split()[0],
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


async def change_flow_report_sub_sections_db(flow_report_id: str, organization: str, username: str, sub_sections: list, comment: str) -> ServiceResponse:

    bson_id = validate_bson_id(flow_report_id)
    if not bson_id:
        return ServiceResponse(success=False, msg='Bad flow report ID', status_code=400)

    flow_report = await get_database().get_collection("flow_reports").find_one({"_id": bson_id})

    if not flow_report:
        return ServiceResponse(success=False, msg="This flow report ID doesn't exist", status_code=404)

    flow_report = FlowReport.model_validate(flow_report).model_dump()

    if (flow_report['organization'] != organization):
        return ServiceResponse(success=False, status_code=403, msg="Your organization can't access this flow report")

    # this check if any mentioned section by the user exists
    # and every checklist the user wants to update exists and raises an error if it doesn't
    # ESLAM: I hope we do not have to debug this section in the future.
    for input_section in sub_sections:
        ReportSubSectionWritten.model_validate(input_section)

        try:
            ReportSubSectionWritten.model_validate(input_section)
        except:
            return ServiceResponse(success=False, status_code=400, msg=f"Bad Sub Section")
        found = False
        for i, array_section in enumerate(flow_report['sub_sections']):
            if input_section['title'] == array_section['title']:
                found = True
                for input_item in input_section['checklist_items']:
                    item_found = False
                    for j, array_item in enumerate(array_section['checklist_items']):
                        if input_item['code'] == array_item['code']:
                            if (input_item.get('fs_index') != None):
                                fs_index = await get_database().get_collection('fs_index').find_one({'_id': ObjectId(input_item['fs_index'])})

                                if not fs_index:
                                    return ServiceResponse(success=False, status_code=404, msg=f"{input_item['fs_index']} File Index not Found")

                                if fs_index['organization'] != organization:
                                    return ServiceResponse(success=False, status_code=403, msg=f"Your organization can't access this file {input_item['fs_index']}")
                            
                            # skip validation for references
                            # TODO-GALAL - fix it
                            # for reference in input_item['manual_references']:

                            #     if not validate_bson_id(reference['fs_index']):
                            #         return ServiceResponse(success=False, msg=f"Bad fs index bson ID {reference['fs_index']}", status_code=400)

                            #     fs_index = await get_database().get_collection('fs_index').find_one({'_id': ObjectId(reference['fs_index'])})

                            #     if not fs_index:
                            #         return ServiceResponse(success=False, status_code=404, msg=f"{input_item['fs_index']} File Index not Found")

                            #     if fs_index['organization'] != organization:
                            #         return ServiceResponse(success=False, status_code=403, msg=f"Your organization can't access this file {input_item['fs_index']}")

                            item_found = True
                            flow_report['sub_sections'][i]['checklist_items'][j] = input_item
                            break
                    if not item_found:
                        return ServiceResponse(success=False, status_code=404, msg=f"Item with code '{input_item['code']}' not found in '{array_section['title']}' section.")
                break
        if not found:
            return ServiceResponse(success=False, status_code=404, msg=f"Section {input_section['title']} doesn't exit")

    flow_report = FlowReport.model_validate(flow_report).model_dump()

    user_change = UserChange(
        user_name=username,
        user_comment=comment,
        change_type=UserChangeType.UPDATE,
    ).model_dump()

    flow_report = await get_database().get_collection("flow_reports").find_one_and_update({"_id": bson_id}, {"$set": {"sub_sections": flow_report['sub_sections']},
                                                                                                             "$push": {"user_changes": user_change}})

    FlowReport.model_validate(flow_report)

    flow_report["_id"] = str(flow_report['_id'])
    del flow_report["sub_sections"]

    return ServiceResponse(data=flow_report)
