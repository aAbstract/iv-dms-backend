from models.regulations import IOSAItem
from models.httpio import LLMAuditResponse, LLMAuditScore
from models.runtime import ServiceResponse
import os
import httpx
import json


score_tags_text_map: dict[str, str] = {
    LLMAuditScore.IRRELEVANT: "The input regulation's topics are unrelated to the input manual",
    LLMAuditScore.PARTIAL: "Some of the input regulation's topics are related to the input manual",
    LLMAuditScore.DOCUMENTED: "The input regulations document all the topics mentioned in the manual",
    LLMAuditScore.ACTIVE: "The input regulations actively document all the topics mentioned in the manual",
}


def count_score_list_explain(result: json):
    explanation_list = []
    score_count_map: dict[str, int] = {
        LLMAuditScore.IRRELEVANT.value: 0,
        LLMAuditScore.PARTIAL.value: 0,
        LLMAuditScore.DOCUMENTED.value: 0,
        LLMAuditScore.ACTIVE.value: 0,
    }

    for i in result:
        if i.get("explanation"):
            explanation_list.append(i["explanation"])
        if i.get("children"):
            for g in i["children"]:
                if g.get("explanation"):
                    explanation_list.append(g["explanation"])
                if g.get("children"):
                    for z in g["children"]:
                        if z.get("explanation"):
                            explanation_list.append(z["explanation"])
                        score_count_map[z["score"]] += 1
                else:
                    score_count_map[g["score"]] += 1
        else:
            score_count_map[i["score"]] += 1

    return score_count_map, explanation_list


# with the same exact structure as the IOSA structure
# if you encounter item with one or more item in the "children" key, then replace the <score> token of that item with the most common <score> value in children.
# if you encounter <score> tokens that has many item in the "children" key, then
async def gemini_generate(IOSA_checklist: str, user_input: str):
    prompt = f"""You are a semantic simularity calculator that finds the semantic simularity <score> between the IOSA sections and the user's REGULATIONS
You must replace each <score> token in the input IOSA object to be equal to on of four <score> options that represents the semantic simularity between the "text" key and the REGULATIONS
and must replace each <explanation> token with a text explaining why you choose this <score> in high detail.
ensure to do this with all "text" keys that are present in the IOSA object.
The output strictly must be a JSON object just like the input IOSA object but with each <score> and <explanation> token having assigned a value.
You can only output a "IRRELEVANT" in the <score> key and explain why incase they match EXAMPLE 1 or incase you don't know the answer,
and output a "PARTIAL" in the <score> key and explain why incase they match EXAMPLE 2,
and output a "DOCUMENTED" in the <score> key and explain why incase they match EXAMPLE 3,
and output a "ACTIVE" in the <score> key and explain why incase they match EXAMPLE 4.

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

### IOSA ###
{IOSA_checklist}

### REGULATIONS ###
{user_input}
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
        constraints = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip("`").strip("\n").strip()
        result = json.loads(constraints)

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
    iosa_item.code = None
    iosa_item.guidance = None
    iosa_item.iosa_map = None

    manual = iosa_item.model_dump_json(exclude_none=True)

    response = await gemini_generate(manual, text)
    if not response.success:
        return response

    # count each type in the score key
    # append all the explanations key in one list
    score_count_map, explanation_list = count_score_list_explain(
        response.data["constraints"]
    )

    score: LLMAuditScore = max(score_count_map, key=score_count_map.get)
    summary = "\n".join(explanation_list)

    llm_resp = LLMAuditResponse(
        score_tag=score,
        score_text=score_tags_text_map[score],
        summary=summary,
        details=response.data["constraints"],
    )
    return ServiceResponse(data={"llm_resp": llm_resp})
