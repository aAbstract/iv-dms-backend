import re
import time
import os
from openai import AsyncOpenAI
from models.runtime import ServiceResponse
from models.regulations import IOSAItem
from models.gpt_35t import *


openai_client = AsyncOpenAI(api_key=os.environ['GPT_35T_API_KEY'])


async def gpt35t_generate(iosa_checklist: str, input_text: str) -> ServiceResponse:
    system_prompt = """
    We are two aviation professionals. A pilot and a flight operations engineer. And you are our AI assistant.
    We are going to audit our organization to match internationally recognized standards. Currently, we will be auditing against the IATA IOSA Checklist. the IOSA checklist is one of the most difficult standards in aviation. IATA defines the IOSA audit as "The IATA Operational Safety Audit (IOSA) Program is an internationally recognized and accepted evaluation system designed to assess the operational management and control systems of an airline."
    The IOSA Standards Manual (ISM) is published in order to provide the IOSA standards, recommended practices (ISARPs), associated guidance material and other supporting information necessary for an operator to successfully prepare for an audit.
    The ISM is the sole source of assessment criteria to be used by auditors when conducting an audit against the ISARPs.
    The ISM may also be used as a guide for any operator desiring to structure its operational management and control systems in conformity with the latest industry operational practices.
    During an audit, an operator is assessed against the ISARPs contained in this manual. To determine conformity with any standard or recommended practice, an auditor will gather evidence to assess the degree to which specifications are documented and implemented by the operator. In making such an assessment, the following information is applicable.
    """

    user_prompt = f"""    
    OBJECTIVES:
        1- We will present the "ISARP", then the current proposed answer "INPUT_TEXT" from the airlines company manuals. Assess the documentation and whether it sufficiently addresses the requirements of the ISARP, then give a rating to the documentation from 0 to 100 such that 0 is the answer doesn't address any part of the ISARP and 100 means it fully answers all the requirements of the ISARP. Then present your recommendations to change then a model answer that I can copy and paste in the manual to fully address the ISARP.
        2- Score the documentation on how sufficiently it addresses the requirements of the ISARP, with one of the below scoring tags.
        3- In the preparation for the audit, we will be focusing on the documentation, however we may ask you about implementation guidance (i.e. will ask you to provide us with procedures to comprehensively implement a specific standard).
        4- For each item and sub item in the ISARPs, estimate compliance score and provide explanation for the estimated score.
        5- Suggest any modifications to improve overall compliance scores.
    
    Scoring:
    Fully Compliant (3): All aspects are clearly and accurately addressed.
    Partially Compliant (2): Some aspects are addressed, but improvements or clarifications are needed.
    Non Compliant (1): Significant deviations from IOSA standards; a thorough revision is required.
    
    ISARPs: {iosa_checklist}
    INPUT_TEXT: {input_text}

    Your output must be in this format and contain these items:
    ASSESSMENT: This section provides a detailed evaluation of the documentation presented in the "INPUT_TEXT" against the corresponding ISARP. It involves a systematic analysis of how well the airline's manuals address the specified standards and recommended practices. The assessment should be in technical, professional language, employing aviation terms as appropriate.
    RECOMMENDATIONS: In this part, recommendations are made based on the assessment. These suggestions aim to improve the documentation's alignment with the "ISARPs". Recommendations should be specific, actionable, and directed towards enhancing compliance. The language used here should remain formal and professional, reflecting the technical nature of aviation.
    OVERALL_COMPLIANCE_SCORE: This is just a number that reflects the overall evaluation of the documentation's compliance with the ISARP with no explanation. The scale ranges from 0 to 100, with 0 indicating no adherence to the ISARP requirements and 100 indicating full compliance. The score is a quantitative representation of how well the airline's manuals meet the specified standards.
    OVERALL_COMPLIANCE_TAG: This is one of the scoring tags that reflect the overall evaluation of the documentation's compliance with the ISARP with no explanation. The value can only be Fully Compliant,  Partially Compliant, Non Compliant.
    """

    llm_debug = int(os.environ['LLM_DEBUG'])
    if llm_debug:
        print('=' * 100)
        print(f"system\n{system_prompt}")
        print(f"user\n{user_prompt}")
        print('=' * 100)

    llm_start = time.time()
    try:
        chat_context = [
            {
                'role': 'system',
                'content': system_prompt,
            },
            {
                'role': 'user',
                'content': user_prompt,
            },
        ]

        gpt_res = await openai_client.chat.completions.create(
            model='gpt-3.5-turbo-1106',
            n=1,
            temperature=0.3,
            frequency_penalty=0.2,
            presence_penalty=0.3,
            timeout=int(os.environ['API_TIMEOUT']),
            messages=chat_context,
        )

        if llm_debug:
            print(f"GPT_35T_1106 reponse time: {time.time() - llm_start}s")
            print('-' * 100)

        if len(gpt_res.choices) > 0:
            gpt_res_msg = gpt_res.choices[0].message
            chat_context.append({
                'role': gpt_res_msg.role,
                'content': gpt_res_msg.content,
            })
            return ServiceResponse(data={
                'gpt35t_resp': gpt_res_msg.content,
                'conversation': [GPT35TMessage.model_validate(x) for x in chat_context],
            })
        else:
            return ServiceResponse(success=False, status_code=503, msg='LLM 35T-1106 Empty Response')

    except Exception as e:
        return ServiceResponse(success=False, status_code=503, msg=f"LLM 35T-1106 Error: {e}")

async def gpt35t_generate_iosa(iosa_checklist: str) -> ServiceResponse:
    system_prompt = """
    We are two aviation professionals. A pilot and a flight operations engineer. And you are our assistant.
    You're an aviation professional with a robust 20-year background in both the business and commercial sectors of the industry. Your expertise extends to a deep-rooted understanding of aviation regulations the world over, a strong grasp of safety protocols, and a keen perception of the regulatory differences that come into play internationally.
    Your experience is underpinned by a solid educational foundation and specialized professional training. This has equipped you with a thorough and detailed insight into the technical and regulatory dimensions of aviation. Your assessments are carried out with attention to detail and a disciplined use of language that reflects a conscientious approach to legal responsibilities.
    In your role, you generate text that align with regulatory mandates, industry benchmarks, and established best practices. You approach this task with a critical eye, paying close attention to the language used and its implications. It's your job to make sure that terminology is employed accurately in compliance with legal stipulations.
    We are going to generate text to match internationally recognized standards. Currently, we will be generate text for the IATA IOSA Checklist. the IOSA checklist is one of the most difficult standards in aviation. IATA defines the IOSA audit as "The IATA Operational Safety Audit (IOSA) Program is an internationally recognized and accepted evaluation system designed to assess the operational management and control systems of an airline."
    The IOSA Standards Manual (ISM) is published in order to provide the IOSA standards, recommended practices (ISARPs), associated guidance material and other supporting information necessary for an operator to successfully prepare for an audit.
    The ISM is the sole source of assessment criteria to be used to generate text that align with the ISARPs.
    The ISM may also be used as a guide for any operator desiring to structure its operational management and control systems in conformity with the latest industry operational practices.
    """

    user_prompt = f"""
    ### OBJECTIVES ###
        1- We will present the "ISARP" from the airlines company manuals. Generate text that sufficiently addresses the requirements of the ISARP, then give a rating to the documentation from 0 to 100 such that 0 is the answer doesn't address any part of the ISARP and 100 means it fully answers all the requirements of the ISARP.
        2- Score your text on how sufficiently it addresses the requirements of the ISARP, with one of the below scoring tags.

    ### Scoring Tags ###
        Fully Compliant (3): All aspects are clearly and accurately addressed.
        Partially Compliant (2): Some aspects are addressed, but improvements or clarifications are needed.
        Non Compliant (1): Significant deviations from IOSA standards; a thorough revision is required.

    ### ISARP ### 	
    {iosa_checklist}

    Your output must be in this format and contain these items:
    NEW_TEXT: This is your generated text which will be in a single paragraph and will be a complete implementation of the ISARP.
    OVERALL_COMPLIANCE_SCORE: This is just a number that reflects the overall evaluation of your text's compliance with the ISARP with no explanation. The scale ranges from 0 to 100, with 0 indicating no adherence to the ISARP requirements and 100 indicating full compliance. The score is a quantitative representation of how well your text meet the specified standards.
    OVERALL_COMPLIANCE_TAG: This is one of the scoring tags that reflect the overall evaluation of the documentation's compliance with the ISARP with no explanation. The value can only be Fully Compliant,  Partially Compliant, Non Compliant.
    """

    llm_debug = int(os.environ['LLM_DEBUG'])
    if llm_debug:
        print('=' * 100)
        print(f"system\n{system_prompt}")
        print(f"user\n{user_prompt}")
        print('=' * 100)

    llm_start = time.time()
    try:
        chat_context = [
            {
                'role': 'system',
                'content': system_prompt,
            },
            {
                'role': 'user',
                'content': user_prompt,
            },
        ]

        gpt_res = await openai_client.chat.completions.create(
            model='gpt-3.5-turbo-1106',
            n=1,
            temperature=0.2,
            frequency_penalty=0.2,
            presence_penalty=0.3,
            timeout=int(os.environ['API_TIMEOUT']),
            messages=chat_context,
        )

        if llm_debug:
            print(f"GPT_35T_1106 reponse time: {time.time() - llm_start}s")
            print('-' * 100)

        if len(gpt_res.choices) > 0:
            gpt_res_msg = gpt_res.choices[0].message
            chat_context.append({
                'role': gpt_res_msg.role,
                'content': gpt_res_msg.content,
            })
            return ServiceResponse(data={
                'gpt35t_resp': gpt_res_msg.content,
                'conversation': [GPT35TMessage.model_validate(x) for x in chat_context],
            })
        else:
            return ServiceResponse(success=False, status_code=503, msg='LLM 35T-1106 Empty Response')

    except Exception as e:
        return ServiceResponse(success=False, status_code=503, msg=f"LLM 35T-1106 Error: {e}")

async def iosa_audit_text(iosa_item: IOSAItem, input_text: str) -> ServiceResponse:
    gpt35t_enable = int(os.environ['GPT_35T_ENABLE'])
    if not gpt35t_enable:
        dummy_scores_map = {
            'FLT 3.1.1': 90,
            'FLT 2.1.35': 20,
        }
        return ServiceResponse(data={
            'llm_resp': 'LLM 35T-1106 Disabled',
            'overall_compliance_score': dummy_scores_map.get(iosa_item.code, 0),
            'conversation': [],
        })

    res = await gpt35t_generate(iosa_item.paragraph, input_text)
    if not res.success:
        return res

    # post processing
    # replace unwanted keywords
    gpt35t_resp: str = res.data['gpt35t_resp']
    gpt35t_resp = gpt35t_resp.replace('INPUT_TEXT', 'Manual Answer')

    # extract OVERALL_COMPLIANCE_SCORE value
    if 'OVERALL_COMPLIANCE_SCORE' not in gpt35t_resp:
        return ServiceResponse(success=False, status_code=503, msg='Missing OVERALL_COMPLIANCE_SCORE Key')
    # extract OVERALL_COMPLIANCE_TAG value
    if 'OVERALL_COMPLIANCE_TAG' not in gpt35t_resp:
        return ServiceResponse(success=False, status_code=503, msg='Missing OVERALL_COMPLIANCE_TAG Key')

    re_matches_score = re.search(r'OVERALL_COMPLIANCE_SCORE:\s+(\d{1,3})|\*\*OVERALL_COMPLIANCE_SCORE:\*\*\s+(\d{1,3})', gpt35t_resp)
    re_matches_tag = re.search(r'OVERALL_COMPLIANCE_TAG:(\**)\s+Non Compliant|OVERALL_COMPLIANCE_TAG:(\**)\s+Partially Compliant|OVERALL_COMPLIANCE_TAG:(\**)\s+Fully Compliant', gpt35t_resp)

    if not re_matches_score:
        if int(os.environ['LLM_DEBUG']):
            print('=' * 100)
            print(gpt35t_resp)
            print('=' * 100)
        return ServiceResponse(success=False, status_code=503, msg='Failed to Compute Compliance Score')
    
    if not re_matches_tag:
        if int(os.environ['LLM_DEBUG']):
            print('=' * 100)
            print(gpt35t_resp)
            print('=' * 100)
        return ServiceResponse(success=False, status_code=503, msg='Failed to Compute Compliance Tag')


    re_matches_tag = " ".join(re_matches_tag.group().split()[-2:]).strip()

    if re_matches_tag not in ("Fully Compliant","Partially Compliant","Non Compliant"):
        return ServiceResponse(success=False, status_code=503, msg='Failed to Compute Compliance Tag')
    ovcomp_tag = str(re_matches_tag)

    re_groups_score = re_matches_score.groups()
    first_match = next((x for x in re_groups_score if x is not None), None)
    if not first_match:
        return ServiceResponse(success=False, status_code=503, msg='Failed to Compute Compliance Score')
    ovcomp_score = int(first_match)

    # remove the scores and tags from the response text
    text = gpt35t_resp[:re_matches_score.span()[0]]

    return ServiceResponse(data={
        'llm_resp': text,
        'overall_compliance_score': ovcomp_score,
        'overall_compliance_tag':ovcomp_tag,
        'conversation': res.data['conversation'],
    })


async def iosa_enhance_text(gpt35t_context: GPT35TContext) -> ServiceResponse:
    gpt35t_enable = int(os.environ['GPT_35T_ENABLE'])
    if not gpt35t_enable:
        return ServiceResponse(data={
            'llm_resp': 'LLM 35T-1106 Disabled',
            'overall_compliance_score': 100,
            'overall_compliance_tag':GPT35TAuditTag.FULLY_COMPLIANT,
            'conversation': [],
        })

    llm_debug = int(os.environ['LLM_DEBUG'])
    llm_start = time.time()
    try:
        gpt35t_context.conversation.append(GPT35TMessage(
            role=GPT35ContextRole.USER,
            content="""
            Apply these recommendations on "INPUT_TEXT" to enhance OVERALL_COMPLIANCE_SCORE.
            Your output must be in this format and contain these items:
            MODIFIED_TEXT: "INPUT_TEXT" after applying recommendations.
            NEW_COMPLIANCE_SCORE: The enhanced OVERALL_COMPLIANCE_SCORE value after applying the recommendations.
            NEW_COMPLIANCE_TAG: The enhanced OVERALL_COMPLIANCE_TAG value after applying the recommendations. The value can only be Fully Compliant,  Partially Compliant, Non Compliant.
            """,
        ))
        gpt_res = await openai_client.chat.completions.create(
            model='gpt-3.5-turbo-1106',
            n=1,
            temperature=0.3,
            frequency_penalty=0.2,
            presence_penalty=0.3,
            timeout=int(os.environ['API_TIMEOUT']),
            messages=[x.model_dump() for x in gpt35t_context.conversation],
        )
        if llm_debug:
            print(f"GPT_35T_1106 reponse time: {time.time() - llm_start}s")
            print('-' * 100)
        if len(gpt_res.choices) > 0:
            gpt_res_msg = gpt_res.choices[0].message
            gpt35t_context.conversation.append(GPT35TMessage(
                role=gpt_res_msg.role,
                content=gpt_res_msg.content,
            ))
        else:
            return ServiceResponse(success=False, status_code=503, msg='LLM 35T-1106 Empty Response')
    except Exception as e:
        return ServiceResponse(success=False, status_code=503, msg=f"LLM 35T-1106 Error: {e}")

    # post processing
    # replace unwanted keywords
    gpt35t_resp = gpt_res_msg.content
    gpt35t_resp = gpt35t_resp.replace('INPUT_TEXT', 'Manual Answer')

    # extract MODIFIED_TEXT value
    if 'MODIFIED_TEXT' not in gpt35t_resp:
        return ServiceResponse(success=False, status_code=503, msg='Missing MODIFIED_TEXT Key')
    # extract NEW_COMPLIANCE_SCORE value
    if 'NEW_COMPLIANCE_SCORE' not in gpt35t_resp:
        return ServiceResponse(success=False, status_code=503, msg='Missing NEW_COMPLIANCE_SCORE Key')
    # extract NEW_COMPLIANCE_TAG value
    if 'NEW_COMPLIANCE_TAG' not in gpt35t_resp:
        return ServiceResponse(success=False, status_code=503, msg='Missing NEW_COMPLIANCE_TAG Key')
    
    re_matches_text = re.search(r"MODIFIED_TEXT:(.*)?", gpt35t_resp)
    if not re_matches_text:
        if int(os.environ['LLM_DEBUG']):
            print('=' * 100)
            print(gpt35t_resp)
            print('=' * 100)
        return ServiceResponse(success=False, status_code=503, msg='Failed to Compute Generated Text')
    text = re_matches_text.group()
    text = re.sub(r"MODIFIED_TEXT:","",text).strip()
    
    re_matches_score = re.search(r'NEW_COMPLIANCE_SCORE:\s+(\d{1,3})|\*\*NEW_COMPLIANCE_SCORE:\*\*\s+(\d{1,3})', gpt35t_resp)
    re_matches_tag = re.search(r'NEW_COMPLIANCE_TAG:(\**)\s+Non Compliant|NEW_COMPLIANCE_TAG:(\**)\s+Partially Compliant|NEW_COMPLIANCE_TAG:(\**)\s+Fully Compliant', gpt35t_resp)

    if not re_matches_score:
        if int(os.environ['LLM_DEBUG']):
            print('=' * 100)
            print(gpt35t_resp)
            print('=' * 100)
        return ServiceResponse(success=False, status_code=503, msg='Failed to Compute Compliance Score')
    
    if not re_matches_tag:
        if int(os.environ['LLM_DEBUG']):
            print('=' * 100)
            print(gpt35t_resp)
            print('=' * 100)
        return ServiceResponse(success=False, status_code=503, msg='Failed to Compute Compliance Tag')

    re_matches_tag = " ".join(re_matches_tag.group().split()[-2:]).strip()

    if re_matches_tag not in ("Fully Compliant","Partially Compliant","Non Compliant"):
        return ServiceResponse(success=False, status_code=503, msg='Failed to Compute Compliance Tag')
    ovcomp_tag = str(re_matches_tag)

    re_matches_score = re_matches_score.groups()
    first_match = next((x for x in re_matches_score if x is not None), None)
    if not first_match:
        return ServiceResponse(success=False, status_code=503, msg='Failed to Compute Compliance Score')
    ovcomp_score = int(first_match)


    return ServiceResponse(data={
        'llm_resp': text,
        'overall_compliance_score': ovcomp_score,
        'overall_compliance_tag': ovcomp_tag,
        'conversation': gpt35t_context.conversation,
    })

async def iosa_generate_text(iosa_item: IOSAItem) -> ServiceResponse:

    gpt35t_enable = int(os.environ['GPT_35T_ENABLE'])
    if not gpt35t_enable:
        dummy_scores_map = {
            'FLT 3.1.1': 90,
            'FLT 2.1.35': 20,
        }
        return ServiceResponse(data={
            'llm_resp': 'LLM 35T-1106 Disabled',
            'overall_compliance_score': dummy_scores_map.get(iosa_item.code, 0),
            'overall_compliance_tag': GPT35TAuditTag.FULLY_COMPLIANT,
            'context_id': "",
            'conversation':[]
        })

    res = await gpt35t_generate_iosa(iosa_item.paragraph)
    if not res.success:
        return res

    # post processing
    gpt35t_resp: str = res.data['gpt35t_resp']

    # extract NEW_TEXT value
    if 'NEW_TEXT' not in gpt35t_resp:
        return ServiceResponse(success=False, status_code=503, msg='Missing NEW_TEXT Key')
    # extract OVERALL_COMPLIANCE_SCORE value
    if 'OVERALL_COMPLIANCE_SCORE' not in gpt35t_resp:
        return ServiceResponse(success=False, status_code=503, msg='Missing OVERALL_COMPLIANCE_SCORE Key')
    # extract OVERALL_COMPLIANCE_TAG value
    if 'OVERALL_COMPLIANCE_TAG' not in gpt35t_resp:
        return ServiceResponse(success=False, status_code=503, msg='Missing OVERALL_COMPLIANCE_TAG Key')

    re_matches_text = re.search(r"NEW_TEXT:(.*)?", gpt35t_resp)
    if not re_matches_text:
        if int(os.environ['LLM_DEBUG']):
            print('=' * 100)
            print(gpt35t_resp)
            print('=' * 100)
        return ServiceResponse(success=False, status_code=503, msg='Failed to Compute Generated Text')
    text = re_matches_text.group()
    text = re.sub(r"NEW_TEXT:","",text).strip()

    re_matches_score = re.search(r'OVERALL_COMPLIANCE_SCORE:\s+(\d{1,3})|\*\*OVERALL_COMPLIANCE_SCORE:\*\*\s+(\d{1,3})', gpt35t_resp)
    re_matches_tag = re.search(r'OVERALL_COMPLIANCE_TAG:(\**)\s+Non Compliant|OVERALL_COMPLIANCE_TAG:(\**)\s+Partially Compliant|OVERALL_COMPLIANCE_TAG:(\**)\s+Fully Compliant', gpt35t_resp)

    if not re_matches_score:
        if int(os.environ['LLM_DEBUG']):
            print('=' * 100)
            print(gpt35t_resp)
            print('=' * 100)
        return ServiceResponse(success=False, status_code=503, msg='Failed to Compute Compliance Score')
    
    if not re_matches_tag:
        if int(os.environ['LLM_DEBUG']):
            print('=' * 100)
            print(gpt35t_resp)
            print('=' * 100)
        return ServiceResponse(success=False, status_code=503, msg='Failed to Compute Compliance Tag')

    re_matches_tag = " ".join(re_matches_tag.group().split()[-2:]).strip()

    if re_matches_tag not in ("Fully Compliant","Partially Compliant","Non Compliant"):
        return ServiceResponse(success=False, status_code=503, msg='Failed to Compute Compliance Tag')
    ovcomp_tag = str(re_matches_tag)

    re_matches_score = re_matches_score.groups()
    first_match = next((x for x in re_matches_score if x is not None), None)
    if not first_match:
        return ServiceResponse(success=False, status_code=503, msg='Failed to Compute Compliance Score')
    ovcomp_score = int(first_match)

    return ServiceResponse(data={
        'llm_resp': text,
        'overall_compliance_score': ovcomp_score,
        'overall_compliance_tag':ovcomp_tag,
        'conversation': res.data['conversation'],
    })
