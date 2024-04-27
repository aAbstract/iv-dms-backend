import re
import time
import os
from openai import AsyncOpenAI
from models.runtime import ServiceResponse
from models.regulations import IOSAItem, RegulationType, RegulationTypeDefinitions
from models.gpt_35t import *
from lib.pdf import count_tokens
import anthropic


client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

async def llm_audit(iosa_checklist: str, input_text: str,definitions:str) -> ServiceResponse:

    system_prompt = f"""
    You're an aviation professional with a robust 20-year background in both the business and commercial sectors of the industry. Your expertise extends to a deep-rooted understanding of aviation regulations the world over, a strong grasp of safety protocols, and a keen perception of the regulatory differences that come into play internationally.
    Your experience is underpinned by a solid educational foundation and specialized professional training. This has equipped you with a thorough and detailed insight into the technical and regulatory dimensions of aviation. Your assessments are carried out with attention to detail and a disciplined use of language that reflects a conscientious approach to legal responsibilities.
    In your role, you conduct audits of airlines to ensure they align with regulatory mandates, industry benchmarks, and established best practices. You approach this task with a critical eye, paying close attention to the language used and its implications. It's your job to make sure that terminology is employed accurately in compliance with legal stipulations.
    From a technical standpoint, your focus is on precise compliance with standards, interpreting every word of regulatory requirements and standards literally and ensuring these are fully reflected within the airline's legal documentation.
    In the realm of aviation, you are recognized as a font of knowledge, possessing a breadth of experience that stretches across various departments within an aviation organization.
    Your task involves meticulously evaluating the airline's legal documents against these benchmarks, verifying that the responses provided meet the stipulated regulations or standards. You then present a detailed assessment, thoroughly outlining both strong points and areas needing improvement, and offering actionable advice for enhancements.
    Your approach to evaluating strengths and weaknesses is methodical, employing legal terminology with a level of precision and detail akin to that of a seasoned legal expert.
    Furthermore, if requested, you are adept at supplementing statements in such a way that they comprehensively address and fulfill the relevant regulatory requirements or standards, ensuring complete compliance and thoroughness in documentation.
    """
    user_prompt = f"""
    Assessment of Compliance Level:
    The provided INPUT_TEXT is to be evaluated on a compliance scale against the requirements of the REGULATION_TEXT or international standard, ranging from 0 to 10. A score of 0 indicates the text is entirely non-compliant or irrelevant to the set requirements, while a score of 10 denotes full compliance with the specified criteria.
    The INPUT_TEXT's relevance and adherence to the given standards must be analyzed, and an appropriate score within this range should be assigned based on the assessment.
    Provide a thorough justification for the assigned score. Elaborate on the specific factors and criteria that influenced your decision, detailing how the INPUT_TEXT meets or fails to meet the established requirements, which will support the numerical compliance rating you have provided
    
    Here are some definitions to remember:
    {definitions}

    REGULATION_TEXT: 
    {iosa_checklist}
    INPUT_TEXT: 
    {input_text}

    Enhancement and Compliance Explanation:
    Should your assessment yield a compliance score greater than 3, you should provide supplemental text to the original content, drawing from industry best practices and benchmarks, as well as referencing pertinent regulatory materials or standards. The supplementary text should be crafted in a human writing style, incorporating human factors principles to ensure it is clear, readable, and easily understood by crew members. It's important to note that aviation regulations emphasize ease of language and precision in communication.
    In the case where the provided text is deemed completely irrelevant, you are to utilize your expertise, industry benchmarks, best practices, and relevant regulatory references or standards to formulate a detailed exposition of processes, procedures, organizational structure, duty management, or any other facet within the aviation industry. The goal is to revise the text to achieve full compliance with the applicable legal requirements or standards.

    Your output must be in the following markdown friendly format:
    
    **ASSESSMENT:**
    In this section, thoroughly evaluate how well the provided answer meets
    the requirements specified in the given regulatory reference or industry
    standard. Focus on:
    *       Compliance with all requirements
    *       Proper syntax and semantics
    Use a detailed, itemized format with two subsections:
    *       Strengths: Aspects where the answer satisfies the requirements well
    *       Weaknesses (or Shortcomings): Areas where the answer falls short of
    fully meeting the requirements
    Write the assessment in formal, professional language, incorporating
    aviation and regulatory terminology from the provided reference when
    applicable.
    
    **Score:**
    The compliance score for the INPUT_TEXT

    **RECOMMENDATIONS:**
    In this section, you will provide specific suggestions for the
    document's author to address the identified weaknesses and bring the
    text into full compliance with the relevant regulatory requirements or
    industry standards.
    1.      Directly address each shortcoming noted in the assessment
    2.      Provide exact text that can be copied and pasted to replace or
    supplement the original, ensuring it:
    a.      Closes any gaps in meeting the specified requirements
    b.      Incorporates wording and concepts from the applicable regulatory
    reference or standard
    c.      Reflects industry best practices, benchmarks, and your aviation
    knowledge
    Adheres to human factors principles for effective technical writing in
    aviation
    3.      Write in a professional, formal tone befitting technical
    documentation
    4.      Use precise aviation and regulatory terminology
    The goal is to equip the author with the necessary content to revise the
    document to be fully compliant and align with industry conventions.
    """

    llm_debug = int(os.environ['LLM_DEBUG'])
    if llm_debug:
        print('=' * 100)
        print(f"user\n{user_prompt}")
        print(f"system\n{system_prompt}")
        print('=' * 100)

    llm_start = time.time()
    try:
        chat_context = [
            {
                'role': 'user',
                'content': user_prompt,
            },
        ]

        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            messages=chat_context,
            system=system_prompt,
            temperature=0.2
            )

        if llm_debug:
            print(f"Sonnet reponse time: {time.time() - llm_start}s")
            print('-' * 100)

        if len(message.content) > 0:
            llm_response = message.content[0]
            chat_context.append({
                'role': llm_response.type,
                'content': llm_response.text,
            })

            input_token_count = count_tokens(user_prompt+ ' ' + system_prompt)
            output_token_count = count_tokens(llm_response.text)

            return ServiceResponse(data={
                'llm_response': llm_response.text,
                'conversation': [GPT35TMessage.model_validate(x) for x in chat_context],
                'input_token_count' : input_token_count,
                'output_token_count':output_token_count
            })
        else:
            return ServiceResponse(success=False, status_code=503, msg='LLM Sonnet Empty Response')

    except Exception as e:
        return ServiceResponse(success=False, status_code=503, msg=f"LLM Sonnet Error: {e}")

async def llm_audit_item(iosa_item: IOSAItem, input_text: str,regulation_type:str) -> ServiceResponse:

    llm_enable = int(os.environ['ANTHROPIC_ENABLE'])
    if not llm_enable:
        return ServiceResponse(data={
            'llm_resp': "Hello my dude",
            'overall_compliance_score': 7,
            'overall_compliance_tag':"Partially Compliant",
            'conversation': [],
            'input_token_count':200,
            'output_token_count': 500
        })

    res = await llm_audit(iosa_item.paragraph, input_text,RegulationTypeDefinitions[regulation_type])
    if not res.success:
        return res

    # # post processing
    # # replace unwanted keywords
    llm_response: str = res.data['llm_response']
    llm_response = llm_response.replace('INPUT_TEXT', 'Manual Answer')
    llm_response = llm_response.replace('REGULATION_TEXT', regulation_type + " Standard")

    if 'Score' not in llm_response:
        return ServiceResponse(success=False, status_code=503, msg='Missing OVERALL_COMPLIANCE_SCORE Key')
        
    re_matches_score = re.search(r'(?<=(\*\*Score:\*\*))(\s+)(\d{1,2})', llm_response)
   
    if not re_matches_score:
        if int(os.environ['LLM_DEBUG']):
            print('=' * 100)
            print(llm_response)
            print('=' * 100)
        return ServiceResponse(success=False, status_code=503, msg='Failed to Compute Compliance Score')

    re_groups_score = re_matches_score.group()

    if not re_groups_score:
        return ServiceResponse(success=False, status_code=503, msg='Failed to Compute Compliance Score')
        
    ovcomp_score = int(re_groups_score.strip())

    text = llm_response[:].strip()

    # check if token limit is reached
    input_token_count = res.data['input_token_count']
    output_token_count = res.data['output_token_count']

    total_token_count = input_token_count + output_token_count

    if(total_token_count >= 10000):
        text+= f"\n\n\n\n**Warning**\n\n**Your Prompt Reached {total_token_count} Tokens**\n\n**Prompts shouldn't pass 200000 Tokens.**"
    ovcomp_tag= ""
    if(ovcomp_score<=3):
        ovcomp_tag = "Non Compliant"
    elif(ovcomp_score<=7):
        ovcomp_tag = "Partially Compliant"
    elif(ovcomp_score<=10):
        ovcomp_tag = "Fully Compliant"

    return ServiceResponse(data={
        'llm_resp': text,
        'overall_compliance_score': ovcomp_score,
        'overall_compliance_tag':ovcomp_tag,
        'conversation': res.data['conversation'],
        'input_token_count': input_token_count,
        'output_token_count':output_token_count
    })