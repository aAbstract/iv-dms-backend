from models.regulations import IOSAItem
from models.httpio import LLMAuditResponse, LLMAuditScore
from models.runtime import ServiceResponse
import os
import httpx
import json
from collections import Counter


score_tags_text_map: dict[str, str] = {
    LLMAuditScore.IRRELEVANT: "The input regulation's topics are unrelated to the input manual",
    LLMAuditScore.PARTIAL: "Some of the input regulation's topics are related to the input manual",
    LLMAuditScore.DOCUMENTED: "The input regulations document all the topics mentioned in the manual",
    LLMAuditScore.ACTIVE: "The input regulations actively document all the topics mentioned in the manual",
}


def list_explanations(result: json, explanation_list: list[str] = []):
    if result.get("explanation"):
        explanation_list.append(result["explanation"])

    if result.get("children"):
        for i in result["children"]:
            list_explanations(i, explanation_list)


def fill_null_scores(result: json, children_score_count: list = []):
    if (not result.get("score")) and result.get("children"):
        for i in result["children"]:
            result_temp, children_score_count_temp = fill_null_scores(i)
            children_score_count.extend(children_score_count_temp)
        if len(children_score_count):
            most_repeated_string, _ = Counter(children_score_count).most_common(1)[0]
            result["score"] = most_repeated_string
        else:
            result["score"] = "SERVER_ERROR"

    elif (not result.get("score")) and (not result.get("children")):
        result["score"] = "SERVER_ERROR"
        children_score_count.append("SERVER_ERROR")

    elif result.get("score"):
        children_score_count.append(result["score"])

    return result, children_score_count


def count_score(result: json, score_count_map):
    if result.get("score"):
        score_count_map[result["score"]] += 1

    if result.get("children"):
        for i in result["children"]:
            count_score(i, score_count_map)


async def gemini_generate(manual: str, text: str):
    prompt = f"""You are a semantic simularity calculator that finds the semantic simularity result between the IOSA sections and the user's REGULATIONS
You will change the IOSA object where for each "text" key, you will add a result that belongs to four result options that represents the semantic simularity between the "text" key and the REGULATIONS as the "score" key
and an explanation for why you choose this result as the "explanation" key.
ensure to do this with all "text" keys that are present in the IOSA object.
The output strictly must be a JSON object with the same exact structure as the IOSA structure but for each and every single "text" key, there will be an additional "score" and "explanation" keys.
You can only output a "IRRELEVANT" in the result key and explain why incase they match EXAMPLE 1 or incase you don't know the answer,
and output a "PARTIAL" in the result key and explain why incase they match EXAMPLE 2,
and output a "DOCUMENTED" in the result key and explain why incase they match EXAMPLE 3,
and output a "ACTIVE" in the result key and explain why incase they match EXAMPLE 4.

### EXAMPLE 1 (The REGULATIONS only mention all topics unrelated to the IOSA)###
IOSA
- a sufficient number of workers must be assigned for each truck, workers must shower on a daily basis
REGULATIONS
- The workshop will be cleaned on a daily basis, food will be served everyday

### EXAMPLE 2 (The REGULATIONS only mention some topics unrelated to the IOSA)###
IOSA
- a sufficient number of workers must be assigned for each truck, workers must shower on a daily basis
REGULATIONS
- we will have some workers for each truck, food will be served everyday

### EXAMPLE 3 (The REGULATIONS only document all the topics mentioned in the IOSA)###
IOSA
- a sufficient number of workers must be assigned for each truck, workers must shower on a daily basis
REGULATIONS
- we will have some workers for each truck, workers will shower

### EXAMPLE 4 (The REGULATIONS only actively document all the topics mentioned in the IOSA)###
IOSA
- a sufficient number of workers must be assigned for each truck, workers must shower on a daily basis
REGULATIONS
- we will have 1 to 2 workers for each truck, workers will shower everyday at least once

### EXAMPLE IOSA FORMAT ###
The IOSA is a list of Constrain objects where each Constrain object has a "text" key which is a string
and a "children" key where the "children" key is a list of Constrain objects
Here is an example:
"constraints": [{{
"text": "Some text you need to output the semantic simularity for",
"children": [
{{
"text": "Some text you need to output the semantic simularity for",
"children": [{{ 
"text":"Some text you need to output the semantic simularity for",
"children":[]
}}]
}},
{{
"text": "Some text you need to output the semantic simularity for",
"children": [     
{{
"text": "Some text you need to output the semantic simularity for",
"children": []
}},
{{
"text": "Some text you need to output the semantic simularity for",
"children": []
}}
]
}},
]
}}
]

### IOSA ###
{manual}

### REGULATIONS ###
{text}
"""

    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={os.getenv("GEMINI_API_KEY")}'

    headers = {"Content-Type": "application/json"}

    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0, "candidate_count": 1},
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, headers=headers, content=json.dumps(data))

        if response.status_code != 200:
            return ServiceResponse(
                success=False,
                msg=response.text,
                data=response.text,
                status_code=response.status_code,
            )

        result = json.loads(
            response.json()["candidates"][0]["content"]["parts"][0]["text"]
            .strip("`")
            .strip("\n")
            .replace("'", '"')
        )
        # return response.json()["candidates"][0]["content"]["parts"][0]["text"]

        return ServiceResponse(
            success=True, msg="Gemini generation successfull", data=result
        )


async def iosa_audit_text(iosa_item: IOSAItem, text: str) -> ServiceResponse:
    llm_enable = int(os.environ['LLM_ENABLE'])
    if not llm_enable:
        return ServiceResponse(data={
            'llm_resp': LLMAuditResponse(
                score_tag='NULL',
                score_text='NULL',
                summary='LLM Disabled',
            ),
        })

    manual = iosa_item.model_dump()
    del manual["code"]
    del manual["guidance"]
    del manual["iosa_map"]
    explanation_list = []
    score_count_map: dict[str, int] = {
        LLMAuditScore.IRRELEVANT.value: 0,
        LLMAuditScore.PARTIAL.value: 0,
        LLMAuditScore.DOCUMENTED.value: 0,
        LLMAuditScore.ACTIVE.value: 0,
    }

    response = await gemini_generate(manual, text)
    # return ServiceResponse(data={"llm_resp": response})
    if not response.success:
        return response

    # count each type in the score key
    # append all the explanations key in one list
    for i in response.data["constraints"]:
        count_score(i, score_count_map)
        list_explanations(i, explanation_list)
        fill_null_scores(i, [])

    score: LLMAuditScore = max(score_count_map, key=score_count_map.get)
    summary = "\n".join(explanation_list)

    llm_resp = LLMAuditResponse(
        score_tag=score,
        score_text=score_tags_text_map[score],
        summary=summary,
        details=response.data["constraints"],
    )
    return ServiceResponse(data={"llm_resp": llm_resp})
