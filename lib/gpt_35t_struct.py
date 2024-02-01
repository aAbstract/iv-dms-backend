import time
import os
import json
from openai import AsyncOpenAI
from models.runtime import ServiceResponse
from models.regulations import IOSAItem
from models.gpt_35t import *


openai_client = AsyncOpenAI(api_key=os.environ['GPT_35T_API_KEY'])


def agg_score(items: list[GTP35TIOSAItemResponse]) -> GPT35TAuditScore:
    """ computes GPT35T aggregate score TODO-LATER-GALAL """
    if len(items) == 0:
        return GPT35TAuditScore.NONE

    return GPT35TAuditScore(round(sum([item.score.value for item in items]) / len(items)))


def agg_pct_score(items: list[GTP35TIOSAItemResponse]) -> float:
    """ computes GPT35T  aggregate score TODO-LATER-GALAL """
    if len(items) == 0:
        return 0

    return sum([item.pct_score for item in items]) / len(items)


def parse_scores_tree(scores_tree: dict) -> list[GTP35TIOSAItemResponse]:
    items: list[GTP35TIOSAItemResponse] = []
    for key, value in scores_tree.items():
        if isinstance(value, dict):
            parent_text = key
            child_items = parse_scores_tree(value)
            items.append(
                GTP35TIOSAItemResponse(
                    text=parent_text,
                    score=agg_score(child_items),
                    pct_score=agg_pct_score(child_items),
                    children=child_items,
                )
            )

        elif isinstance(value, int):
            items.append(
                GTP35TIOSAItemResponse(
                    text=key,
                    score=value,
                    pct_score=((value - 1) / (GPT35T_MAX_SCORE - 1)),
                )
            )

    return items


def gpt35t_parse_resp(llm_json_res: dict) -> GPT35TAuditResponse:
    scores_tree = llm_json_res['compliance_scores']
    comments = llm_json_res['comments']
    suggestions = llm_json_res['suggestions']
    modified = llm_json_res['modified']
    details = parse_scores_tree(scores_tree)
    return GPT35TAuditResponse(
        score=agg_score(details),
        pct_score=agg_pct_score(details),
        comments=comments,
        suggestions=suggestions,
        modified=modified,
        details=details,
    )


async def gpt35t_generate(iosa_checklist: str, input_text: str) -> ServiceResponse:
    prompt = f"""Objective: Evaluate the compliance of the provided paragraph with IOSA Flight Operations standards.
    "IOSA Checklist Criteria":
    {iosa_checklist}
    
    Scoring:
    Fully Compliant (3): All aspects are clearly and accurately addressed.
    Partially Compliant (2): Some aspects are addressed, but improvements or clarifications are needed.
    Non-Compliant (1): Significant deviations from IOSA standards; a thorough revision is required.
    
    "Provided Paragraph":
    {input_text}

    Additional Comments:
    Estimate compliance score for each item and sub item in the "IOSA Checklist Criteria"
    Your output must have this top level json structure:
    {{
        compliance_scores: Object, // a json object tree similar to the provided "IOSA Checklist Criteria" structure
        comments: string, // explanation for these estimated scores
        suggestions: string, // suggestions to improve compliance_scores
        modified: string, // the "Provided Paragraph" after applying these suggestions
    }}
    Do not include the "Provided Paragraph".
    Do not include "IOSA Checklist Criteria"."""

    llm_debug = int(os.environ['LLM_DEBUG'])
    if llm_debug:
        print('=' * 100)
        print(prompt)
        print('=' * 100)

    llm_start = time.time()
    try:
        gpt_res = await openai_client.chat.completions.create(
            model='gpt-3.5-turbo-1106',
            response_format={'type': 'json_object'},
            n=1,
            temperature=0.2,
            frequency_penalty=0.2,
            presence_penalty=0.3,
            timeout=int(os.environ['API_TIMEOUT']),
            messages=[
                {'role': 'system', 'content': 'You are an expert IATA Operational Safety Auditor'},
                {'role': 'user', 'content': prompt},
            ],
        )

        if llm_debug:
            print(f"GPT_35T_1106 reponse time: {time.time() - llm_start}s")
            print('-' * 100)

        if len(gpt_res.choices) > 0:
            return ServiceResponse(data={'gpt35t_resp': gpt_res.choices[0].message.content})
        else:
            return ServiceResponse(success=False, status_code=503, msg='LLM 35T-1106 Empty Response')

    except Exception as e:
        return ServiceResponse(success=False, status_code=503, msg=f"LLM 35T-1106 Error: {e}")


async def iosa_audit_text(iosa_item: IOSAItem, input_text: str) -> ServiceResponse:
    gpt35t_enable = int(os.environ['GPT_35T_ENABLE'])
    if not gpt35t_enable:
        dummy_scores_map = {
            'FLT 3.1.1': 0.8,
            'FLT 2.1.35': 0.2,
        }
        return ServiceResponse(data={
            'llm_resp': GPT35TAuditResponse(
                score=0,
                pct_score=dummy_scores_map.get(iosa_item.code, 0),
                comments='LLM 35T-1106 Disabled',
                suggestions='No Suggestions',
                modified='No Modification',
                details=[],
            ),
        })

    res = await gpt35t_generate(iosa_item.paragraph, input_text)
    if not res.success:
        return res

    try:
        gpt35t_json_res = json.loads(res.data['gpt35t_resp'])
    except:
        return ServiceResponse(success=False, status_code=503, msg='LLM 35T-1106 JSON Parse Error')

    output_keys = set(gpt35t_json_res.keys())
    if output_keys != {'compliance_scores', 'comments', 'suggestions', 'modified'}:
        return ServiceResponse(success=False, status_code=503, msg=f"LLM 35T-1106 Error: missing output key, output_keys={output_keys}")

    parsed_resp = gpt35t_parse_resp(gpt35t_json_res)
    return ServiceResponse(data={'llm_resp': parsed_resp})
