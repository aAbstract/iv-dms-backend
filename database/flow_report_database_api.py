from  bson import ObjectId
from models.runtime import ServiceResponse
from database.mongo_driver import get_database
from models.flow_report import (FlowReport, FlowReportChange, FlowReportStatus, FlowStage,
    FlowStageTemplate, FlowStageTemplateMap, ReportItem, ReportSubSectionWritten, UserChange,
    UserChangeType)
from database.mongo_driver import get_database, validate_bson_id
from models.regulations import IOSASection, RegulationType
from models.users import UserRole


async def get_flow_report_stage_template_options_db(template_name: str) -> ServiceResponse:

    # get templates
    if template_name:
        for member in FlowStageTemplateMap:
            if template_name == member.value['name']:
                return ServiceResponse(data={"templates": [FlowStageTemplate.model_validate(member.value)]})
        return ServiceResponse(
            success=False,
            status_code=422,
            msg="This Flow Stage Template Name is incorrect",
        )
    else:
        templates = []
        for member in FlowStageTemplateMap:
            templates.append(FlowStageTemplate.model_validate(member.value))

    return ServiceResponse(data={"templates": templates})

async def create_flow_report_db(regulation_id: str,
                            title: str,
                            checklist_template_code:str,
                            flow_stage_template: str,
                            start_date: str,
                            end_date : str,
                            organization: str,
                            username: str) -> ServiceResponse:
    bson_id = validate_bson_id(regulation_id)
    if not bson_id:
        return ServiceResponse(success=False, msg='Bad Regulation ID', status_code=400)
    # get type from regulation
    regulation = await get_database().get_collection('regulations').find_one({'_id': bson_id})
    if not regulation:
        return ServiceResponse(success=False, msg="This Regulation ID doesn't exist", status_code=404)

    if not (regulation['type'] in RegulationType.__members__.values()):
        return ServiceResponse(success=False, msg='Bad Regulation Type', status_code=400)
    
    # get IOSA section
    if ' ' not in checklist_template_code:
        return ServiceResponse(success=False, msg='Bad Checklist Template Code', status_code=400)

    section_code, _ = checklist_template_code.split(' ')
    iosa_section = await get_database().get_collection('regulations').find_one({'_id': bson_id, 'sections.code': section_code}, projection={"_id": 0, "sections.$": 1})
    if not iosa_section:
        return ServiceResponse(success=False, msg='Regulation Checklist Code not Found', status_code=404)

    if len(iosa_section['sections']) > 1:
        return ServiceResponse(success=False, msg='Multiple Regulation Checklist Codes were Found', status_code=400)

    iosa_section = IOSASection.model_validate(iosa_section['sections'][0])

    found = False
    for member in FlowStageTemplateMap:
        if flow_stage_template == member.value['name']:
            flow_stage_template = FlowStageTemplate.model_validate(member.value)
            found = True
            break
    if not found:
        return ServiceResponse(
            success=False,
            status_code=422,
            msg="This Flow Stage Template Name is incorrect",
        )
    # assign users based on role and organization
    updated_stages = []
    for stage in flow_stage_template.stages:
        if not (stage.assigned_role in UserRole.__members__.values()):
            return ServiceResponse(success=False, msg='Bad role stored in template', status_code=400)

        user = await get_database().get_collection("users").find_one({"organization":organization,"user_role":stage.assigned_role})
        if not user:
            return ServiceResponse(success=False,status_code=400,msg=f"No user with {stage.assigned_role} role in {organization}")
        stage.assigned_user = user['username']
        updated_stages.append(stage)

    # construct flow report
    flow_report = FlowReport(
        title=title,
        regulation_id=regulation_id,
        code=section_code,
        sub_sections=[],
        flow_stages=updated_stages,
        status=FlowReportStatus.INPROGRESS,
        current_stage_index=0,
        start_date=start_date,
        end_date=end_date,
        organization=organization,
        creator=username
    )

    sub_section_iosa_item_map = {}
    for item in iosa_section.items:
        if item.code.startswith(checklist_template_code):
            sub_section_title = item.iosa_map[1]

            if not sub_section_title in sub_section_iosa_item_map:
                sub_section_iosa_item_map[sub_section_title] = []
            sub_section_iosa_item_map[sub_section_title].append(ReportItem(code=item.code))

    flow_report.sub_sections = [ReportSubSectionWritten(
        title=sub_section_header,
        checklist_items=iosa_codes,
    ) for sub_section_header, iosa_codes in sub_section_iosa_item_map.items()]

    flow_report = FlowReport.model_validate(flow_report)
    flow_report_dict = flow_report.model_dump()

    mdb_result = await get_database().get_collection("flow_reports").insert_one(flow_report_dict)
    flow_report_dict['_id'] = str(mdb_result.inserted_id)

    # create flow report user change
    user_change = FlowReportChange(
        report_id= str(mdb_result.inserted_id),
        organization= organization,
        user_changes = [
            UserChange(
                user_name=username,
                user_comment="",
                change_type=UserChangeType.CREATE,
                report_after= flow_report
                )
            ]
        )
    
    mdb_result = await get_database().get_collection("flow_report_changes").insert_one(user_change.model_dump())

    return ServiceResponse(data={'flow_report': flow_report_dict})

async def list_flow_report_db(organization:str) -> ServiceResponse:

    flow_reports = [report async for report in get_database().get_collection("flow_reports").find({"organization":organization},projection={"sub_sections": 0})]
    for report in flow_reports:
        report['_id'] = str(report['_id']) 
    return ServiceResponse(data={'flow_report': flow_reports})

async def delete_flow_report_db(username:str,user_comment:str,flow_report_id:str,organization:str) -> ServiceResponse:

    bson_id = validate_bson_id(flow_report_id)
    if not bson_id:
        return ServiceResponse(success=False, msg='Bad flow report ID', status_code=400)

    flow_report = await get_database().get_collection("flow_reports").find_one({"_id":bson_id})

    if not flow_report:
        return ServiceResponse(success=False, msg="This flow report ID doesn't exist", status_code=404)

    if(flow_report['organization'] != organization):
        return ServiceResponse(success=False,status_code=403,msg="Your organization can't delete this flow report")

    # create flow report user change
    user_change = UserChange(
        user_name=username,
        user_comment=user_comment,
        change_type=UserChangeType.DELETE,
    )
    
    flow_report_change = await get_database().get_collection("flow_report_changes").find_one({"report_id": flow_report_id})
    flow_report_change = FlowReportChange.model_validate(flow_report_change).model_dump()
    flow_report_change['user_changes'].append(user_change.model_dump())
    flow_report_change = await get_database().get_collection("flow_report_changes").update_one({"report_id": flow_report_id},{"$set": flow_report_change})

    await get_database().get_collection("flow_reports").delete_one({"_id":bson_id})

    return ServiceResponse()

async def get_flow_report_history_db(flow_report_id:str,organization:str) -> ServiceResponse:

    bson_id = validate_bson_id(flow_report_id)
    if not bson_id:
        return ServiceResponse(success=False, msg='Bad flow report ID', status_code=400)

    flow_report_change = [report async for report in get_database().get_collection("flow_report_changes").find({"report_id":flow_report_id})]

    if not flow_report_change:
        return ServiceResponse(success=False, msg="This flow report change ID doesn't exist", status_code=404)

    if len(flow_report_change) > 1:
        return ServiceResponse(success=False, msg='Multiple flow report Changes were Found', status_code=400)
   
    flow_report_change = flow_report_change[0]

    if(flow_report_change['organization'] != organization):
        return ServiceResponse(success=False,status_code=403,msg="Your organization can't access this flow report")

    return ServiceResponse(data={"user_changes":flow_report_change['user_changes']})

async def get_flow_report_db(flow_report_id:str,organization:str,username:str) -> ServiceResponse:

    bson_id = validate_bson_id(flow_report_id)
    if not bson_id:
        return ServiceResponse(success=False, msg='Bad flow report ID', status_code=400)

    flow_report = await get_database().get_collection("flow_reports").find_one({"_id":bson_id})
    
    if not flow_report:
        return ServiceResponse(success=False, msg="This flow report ID doesn't exist", status_code=404)
    
    flow_report = FlowReport.model_validate(flow_report).model_dump()

    if(flow_report['organization'] != organization):
        return ServiceResponse(success=False,status_code=403,msg="Your organization can't access this flow report")
    # get applicability and general guidence
    iosa_section = await get_database().get_collection('regulations').find_one({'_id': ObjectId(flow_report['regulation_id']), 'sections.code': flow_report['code']}, projection={"_id": 0, "sections.$": 1})
    if not iosa_section:
        return ServiceResponse(success=False, msg='Regulation Checklist Code not Found', status_code=404)

    if len(iosa_section['sections']) > 1:
        return ServiceResponse(success=False, msg='Multiple Regulation Checklist Codes were Found', status_code=400)

    iosa_section = IOSASection.model_validate(iosa_section['sections'][0])

    flow_report['applicability'] = iosa_section.applicability
    flow_report['guidance'] = iosa_section.guidance
    flow_report['_id'] = flow_report_id
    # create flow report user change
    user_change = UserChange(
        user_name=username,
        user_comment="",
        change_type=UserChangeType.VIEW,
    )
    
    flow_report_change = await get_database().get_collection("flow_report_changes").find_one({"report_id": flow_report_id})
    flow_report_change = FlowReportChange.model_validate(flow_report_change).model_dump()
    flow_report_change['user_changes'].append(user_change.model_dump())
    flow_report_change = await get_database().get_collection("flow_report_changes").update_one({"report_id": flow_report_id},{"$set": flow_report_change})

    return ServiceResponse(data=flow_report)

async def forward_flow_report_db(flow_report_id:str,organization:str,username:str,user_comment:str,user_forward:str) -> ServiceResponse:

    bson_id = validate_bson_id(flow_report_id)
    if not bson_id:
        return ServiceResponse(success=False, msg='Bad flow report ID', status_code=400)

    flow_report = await get_database().get_collection("flow_reports").find_one({"_id":bson_id})
    
    if not flow_report:
        return ServiceResponse(success=False, msg="This flow report ID doesn't exist", status_code=404)
    
    flow_report = FlowReport.model_validate(flow_report).model_dump()

    if(flow_report['organization'] != organization):
        return ServiceResponse(success=False,status_code=403,msg="Your organization can't access this flow report")
    
    user_object = await get_database().get_collection("users").find_one({"username":user_forward})

    if not user_object:
        return ServiceResponse(success=False,status_code=404,msg="The receiver user doesn't exist")

    ###
    ###
    # todo
    # notification system function call to forward
    ###
    ###

    # create flow report user change
    user_change = UserChange(
        user_name=username,
        user_comment=user_comment,
        change_type=UserChangeType.FORWARD,
    ).model_dump()

    user_change['forward_user'] = user_forward

    flow_report_change = await get_database().get_collection("flow_report_changes").find_one({"report_id": flow_report_id})
    flow_report_change = FlowReportChange.model_validate(flow_report_change).model_dump()
    flow_report_change['user_changes'].append(user_change)
    flow_report_change = await get_database().get_collection("flow_report_changes").update_one({"report_id": flow_report_id},{"$set": flow_report_change})

    return ServiceResponse()

async def change_flow_report_status(flow_report_id:str,organization:str,username:str,status:str,comment:str) -> ServiceResponse:

    bson_id = validate_bson_id(flow_report_id)
    if not bson_id:
        return ServiceResponse(success=False, msg='Bad flow report ID', status_code=400)

    flow_report = await get_database().get_collection("flow_reports").find_one({"_id":bson_id})
    
    if not flow_report:
        return ServiceResponse(success=False, msg="This flow report ID doesn't exist", status_code=404)
    
    flow_report = FlowReport.model_validate(flow_report).model_dump()

    if(flow_report['organization'] != organization):
        return ServiceResponse(success=False,status_code=403,msg="Your organization can't access this flow report")
    
    if not (status in FlowReportStatus.__members__.values()):
        return ServiceResponse(success=False, msg='Bad Flow Report Status Type', status_code=400)

    mdb_result = await get_database().get_collection("flow_reports").update_one({"_id":bson_id},{"$set":{"status":status}})

    if not comment:
        comment = f"{username} set status to {status}"

    user_change = UserChange(
        user_name=username,
        user_comment=comment,
        change_type=UserChangeType.UPDATE,
    ).model_dump()

    await get_database().get_collection("flow_report_changes").update_one({"report_id": flow_report_id},{"$push": {"user_changes":user_change}})

    return ServiceResponse()

async def change_flow_report_sub_sections(flow_report_id:str,organization:str,username:str,sub_sections:list,comment:str) -> ServiceResponse:

    bson_id = validate_bson_id(flow_report_id)
    if not bson_id:
        return ServiceResponse(success=False, msg='Bad flow report ID', status_code=400)

    flow_report = await get_database().get_collection("flow_reports").find_one({"_id":bson_id})
    
    if not flow_report:
        return ServiceResponse(success=False, msg="This flow report ID doesn't exist", status_code=404)
    
    flow_report = FlowReport.model_validate(flow_report).model_dump()

    if(flow_report['organization'] != organization):
        return ServiceResponse(success=False,status_code=403,msg="Your organization can't access this flow report")
    
    found = False


    for input_section in sub_sections:
        try:
            ReportSubSectionWritten.model_validate(input_section)
        except:
            return ServiceResponse(success=False,status_code=400,msg=f"Bad Sub Section")
        found = False
        for i, array_section in enumerate(flow_report['sub_sections']):
            if input_section['title'] == array_section['title']:
                found = True
                for input_item in input_section['checklist_items']:
                    item_found = False
                    for j, array_item in enumerate(array_section['checklist_items']):
                        if input_item['code'] == array_item['code']:
                            item_found = True
                            # Replace the matching item in the array
                            flow_report['sub_sections'][i]['checklist_items'][j] = input_item
                            break
                    if not item_found:
                        return ServiceResponse(success=False,status_code=404,msg=f"Item with code '{input_item['code']}' not found in '{array_section['title']}' section.")
                break
        if not found:
            return ServiceResponse(success=False,status_code=404,msg=f"Section {input_section['title']} doesn't exit")

    flow_report = FlowReport.model_validate(flow_report).model_dump()
     
    await get_database().get_collection("flow_reports").update_one({"_id":bson_id},{"$set":{"sub_sections":flow_report['sub_sections']}})

    flow_report = await get_database().get_collection("flow_reports").find_one({"_id":bson_id})

    user_change = UserChange(
        user_name=username,
        user_comment=comment,
        change_type=UserChangeType.UPDATE,
        report_after=flow_report
    ).model_dump()

    await get_database().get_collection("flow_report_changes").update_one({"report_id": flow_report_id},{"$push": {"user_changes":user_change}})

    return ServiceResponse()
