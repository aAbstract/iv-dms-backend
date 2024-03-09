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
    Context	Your role is pivotal as you conduct audits to ensure strict compliance with ISARPs. Your meticulous evaluation of legal documents against ISARPs is crucial. We entrust you with the responsibility of upholding legal standards in the aviation industry. During an audit, an operator is assessed against the ISARPs contained in this manual. To determine conformity with any standard or recommended practice, an auditor will gather evidence to assess the degree to which specifications are documented and implemented by the operator. In making such an assessment, the following information is applicable.	You're an aviation professional with a robust 20-year background in both the business and commercial sectors of the industry. Your expertise extends to a deep-rooted understanding of aviation regulations the world over, a strong grasp of safety protocols, and a keen perception of the regulatory differences that come into play internationally.
    Your experience is underpinned by a solid educational foundation and specialized professional training. This has equipped you with a thorough and detailed insight into the technical and regulatory dimensions of aviation. Your assessments are carried out with attention to detail and a disciplined use of language that reflects a conscientious approach to legal responsibilities.
    In your role, you conduct audits of airlines to ensure they align with regulatory mandates, industry benchmarks, and established best practices. You approach this task with a critical eye, paying close attention to the language used and its implications. It's your job to make sure that terminology is employed accurately in compliance with legal stipulations.
    From a technical standpoint, your focus is on precise compliance with standards, interpreting every word of regulatory requirements and standards literally and ensuring these are fully reflected within the airline's legal documentation.
    In the realm of aviation, you are recognized as a font of knowledge, possessing a breadth of experience that stretches across various departments within an aviation organization.
    Your task involves meticulously evaluating the airline's legal documents against these benchmarks, verifying that the responses provided meet the stipulated regulations or standards. You then present a detailed assessment, thoroughly outlining both strong points and areas needing improvement, and offering actionable advice for enhancements.
    Your approach to evaluating strengths and weaknesses is methodical, employing legal terminology with a level of precision and detail akin to that of a seasoned legal expert.
    Furthermore, if requested, you are adept at supplementing statements in such a way that they comprehensively address and fulfill the relevant regulatory requirements or standards, ensuring complete compliance and thoroughness in documentation.
    """

    user_prompt = f"""
    OBJECTIVES:
    The provided text is to be evaluated on a compliance scale against the requirements of the regulatory text or international standard, ranging from 0 to 10. A score of 0 indicates the text is entirely non-compliant or irrelevant to the set requirements, while a score of 10 denotes full compliance with the specified criteria.
    The text's relevance and adherence to the given standards must be analyzed, and an appropriate score within this range should be assigned based on the assessment.
    Provide a thorough justification for the assigned score. Elaborate on the specific factors and criteria that influenced your decision, detailing how the text meets or fails to meet the established requirements, which will support the numerical compliance rating you have provided
    Should your assessment yield a compliance score greater than 3, you should provide supplemental text to the original content, drawing from industry best practices and benchmarks, as well as referencing pertinent regulatory materials or standards. The supplementary text should be crafted in a human writing style, incorporating human factors principles to ensure it is clear, readable, and easily understood by crew members. It's important to note that aviation regulations emphasize ease of language and precision in communication.
    In the case where the provided text is deemed completely irrelevant, you are to utilize your expertise, industry benchmarks, best practices, and relevant regulatory references or standards to formulate a detailed exposition of processes, procedures, organizational structure, duty management, or any other facet within the aviation industry. The goal is to revise the text to achieve full compliance with the applicable legal requirements or standards.

    ISARPs: 
    {iosa_checklist}
    INPUT_TEXT: 
    {input_text}

    Your output must include the following sections:
    ASSESSMENT: A detailed evaluation of the documentation's alignment with the ISARPs. It should employ technical language and aviation terminology where appropriate.
    RECOMMENDATIONS: Specific, actionable suggestions aimed at improving compliance with ISARP standards. Maintain a formal and professional tone.
    OVERALL_COMPLIANCE_SCORE: A numerical rating (0 to 100) reflecting the documentation's overall compliance with the ISARPs.
    OVERALL_COMPLIANCE_TAG: A scoring tag indicating the overall compliance level with ISARPs.
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
            top_p=1.0, 
            frequency_penalty=0.0,  
            presence_penalty=0.0,
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
    OBJECTIVES:
        1- We will present the "ISARP" from the airlines company manuals. Generate text that sufficiently addresses the requirements of the ISARP, then give a rating to the documentation from 0 to 100 such that 0 is the answer doesn't address any part of the ISARP and 100 means it fully answers all the requirements of the ISARP.
        2- Score your text on how sufficiently it addresses the requirements of the ISARP, with one of the below scoring tags.

    SCORING TAGS:
        Fully Compliant (3): All aspects are clearly and accurately addressed.
        Partially Compliant (2): Some aspects are addressed, but improvements or clarifications are needed.
        Non Compliant (1): All aspects are irrelevant and aren't related to the IOSA standards

    ISARP: 	
    {iosa_checklist}

    Your output must be in this format and contain these items:
    NEW_TEXT: This is your generated text which will be in a single paragraph and will be a complete implementation of the ISARP.
    OVERALL_COMPLIANCE_SCORE: A numerical rating (0 to 100) reflecting the documentation's overall compliance with the ISARPs.
    OVERALL_COMPLIANCE_TAG: A scoring tag indicating the overall compliance level with ISARPs.
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
            top_p=1.0, 
            frequency_penalty=0.0,  
            presence_penalty=0.0,
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
    
    # if not re_matches_tag:
    #     if int(os.environ['LLM_DEBUG']):
    #         print('=' * 100)
    #         print(gpt35t_resp)
    #         print('=' * 100)
    #     return ServiceResponse(success=False, status_code=503, msg='Failed to Compute Compliance Tag')


    # re_matches_tag = " ".join(re_matches_tag.group().split()[-2:]).strip()

    # if re_matches_tag not in ("Fully Compliant","Partially Compliant","Non Compliant"):
    #     return ServiceResponse(success=False, status_code=503, msg='Failed to Compute Compliance Tag')
    # ovcomp_tag = str(re_matches_tag)

    re_groups_score = re_matches_score.groups()
    first_match = next((x for x in re_groups_score if x is not None), None)
    if not first_match:
        return ServiceResponse(success=False, status_code=503, msg='Failed to Compute Compliance Score')
    ovcomp_score = int(first_match)

    # remove the scores and tags from the response text
    text = gpt35t_resp[:re_matches_score.span()[0]]
    ovcomp_tag= ""
    if(ovcomp_score<=3):
        ovcomp_tag = "Non Compliant"
    elif(ovcomp_score<=6):
        ovcomp_tag = "Partially Compliant"
    elif(ovcomp_score<=10):
        ovcomp_tag = "Fully Compliant"

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
            temperature=0.2,
            top_p=1.0, 
            frequency_penalty=0.0,  
            presence_penalty=0.0,
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

    re_groups_score = re_matches_score.groups()
    first_match = next((x for x in re_groups_score if x is not None), None)
    if not first_match:
        return ServiceResponse(success=False, status_code=503, msg='Failed to Compute Compliance Score')
    ovcomp_score = int(first_match)

    # remove the scores and tags from the response text
    text = gpt35t_resp[:re_matches_score.span()[0]]
    text = re.sub(r"MODIFIED_TEXT:","",text).strip()

    if(ovcomp_score<=40):
        ovcomp_tag = "Non Compliant"
    elif(ovcomp_score<=80):
        ovcomp_tag = "Partially Compliant"
    elif(ovcomp_score<=100):
        ovcomp_tag = "Fully Compliant"

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

    text = re.sub(r"NEW_TEXT:","",text).strip()

    if(ovcomp_score<=40):
        ovcomp_tag = "Non Compliant"
    elif(ovcomp_score<=80):
        ovcomp_tag = "Partially Compliant"
    elif(ovcomp_score<=100):
        ovcomp_tag = "Fully Compliant"

    return ServiceResponse(data={
        'llm_resp': text,
        'overall_compliance_score': ovcomp_score,
        'overall_compliance_tag':ovcomp_tag,
        'conversation': res.data['conversation'],
    })
