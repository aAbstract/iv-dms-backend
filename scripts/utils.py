# autopep8: off
import os
import sys
from dotenv import load_dotenv
def load_root_path():
    file_dir = os.path.abspath(__file__)
    lv1_dir = os.path.dirname(file_dir)
    root_dir = os.path.dirname(lv1_dir)
    sys.path.append(root_dir)


load_root_path()
load_dotenv()
from models.gpt_35t import *
from models.regulations import *
# autopep8: on


gpt35t_json_res = {
    "compliance_scores": {
        "Operator shall have an initial training program for instructors, evaluators and line check airmen": {
            "i) An instructor course": {
                "a) The fundamentals of teaching and evaluation": 2,
                "b) Lesson plan management": 2,
                "c) Briefing and debriefing": 2,
                "d) Human performance issues": 2,
                "e) Company policies and procedures": 2,
                "f) Simulator serviceability and training in simulator operation": 2,
                "g) Dangers associated with simulating system failures in flight": 2,
                "h) Simulated or actual weather and environmental conditions": 2
            },
            "ii) A formal observation program": {
                "a) Observation by the candidate of experienced instructors": 2,
                "b) Observation of the candidate during supervised practical instruction": 2
            },
            "iii) A seat-specific qualification program": 2,
            "iv) Jump seat observation program for non-line qualified instructors": 2
        }
    },
    "comments": "The provided paragraph lacks specific details and structured training programs for instructors, evaluators, and line check airmen. It does not address the required elements in a comprehensive manner.",
    "suggestions": "To improve compliance, the training program should be structured and detailed, covering all the required elements as per the IOSA standards. Specific training content and procedures need to be clearly defined and documented.",
    "modified": "The provided paragraph does not fully comply with the IOSA Flight Operations standards. It lacks specific details and structured training programs for instructors, evaluators, and line check airmen. To improve compliance, the training program should be structured and detailed, covering all the required elements as per the IOSA standards. Specific training content and procedures need to be clearly defined and documented."
}

flt_2_1_35 = IOSAItem(
    code='FLT 2.1.35',
    guidance='',
    iosa_map=[],
    paragraph='',
    constraints=[
        Constrain(
            text='The Operator shall have an initial training program for instructors, evaluators and line check airmen,to include:',
            children=[
                Constrain(
                    text='An instructor course that addresses as a minimum',
                    children=[
                        Constrain(text='The fundamentals of teaching and evaluation'),
                        Constrain(text='Lesson plan management'),
                        Constrain(text='Briefing and debriefing'),
                        Constrain(text='Human performance issues'),
                        Constrain(text='Company policies and procedures'),
                        Constrain(text='Simulator serviceability and training in simulator operation'),
                        Constrain(text='If the Operator conducts training flights, dangers associated with simulating system failures in flight'),
                        Constrain(text='As applicable, the simulated or actual weather and environmental conditions necessary to conduct each simulator or aircraft training/evaluation session to be administered'),
                    ],
                )
            ],
        ),
        Constrain(text='The Operator shall have a management system for the flight operations organization that ensures control of flight operations and the management of safety and security outcomes.'),
    ],
)

flt_3_1_1 = IOSAItem(
    code="FLT 3.1.1",
    guidance="Refer to the IRM for the definitions of Operations and Operator.",
    iosa_map=["3 Line Operations", "3.1 Common Language"],
    paragraph='',
    constraints=[
        Constrain(
            text="The Operator shall ensure the designation of a common language(s) for use by all flight crew members for communication:",
            children=[
                Constrain(text="On the flight deck during line operations"),
                Constrain(text="If the Operator conducts passenger flights with cabin crew, between the flight crew and cabin crew during line operations"),
                Constrain(text="During flight crew training and evaluation activities"),
            ],
        ),
    ],
)


def agg_score(items: list[GTP35TIOSAItemResponse]):
    """ computes GPT35T aggregate score TODO-GALAL """
    return round(sum([item.score for item in items]) / len(items))


def parse_scores_tree(scores_tree: dict) -> list[GTP35TIOSAItemResponse]:
    items: list[GTP35TIOSAItemResponse] = []
    for key, value in scores_tree.items():
        if isinstance(value, dict):
            parent_text = key
            child_items = parse_scores_tree(value)
            items.append(GTP35TIOSAItemResponse(text=parent_text, score=agg_score(items), children=child_items))

        elif isinstance(value, int):
            items.append(GTP35TIOSAItemResponse(text=key, score=value))

    return items


def gpt35t_output_format(llm_json_res: dict) -> GPT35TAuditResponse:
    scores_tree = llm_json_res['compliance_scores']
    comments = llm_json_res['comments']
    details = parse_scores_tree(scores_tree)
    return GPT35TAuditResponse(
        score=agg_score(details),
        comments=comments,
        details=details
    )


def create_output_json_template(iosa_item: IOSAItem):
    pass

# gpt35t_output_format(gpt35t_json_res)
