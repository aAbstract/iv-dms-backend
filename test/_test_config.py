import requests
import json


_SERVER_ADDR = '127.0.0.1'
_SERVER_PORT = 8080


def get_api_url():
    return f"http://{_SERVER_ADDR}:{_SERVER_PORT}/api"


def get_file_server_url():
    return f"http://{_SERVER_ADDR}:{_SERVER_PORT}"


def login_user(username: str, password: str) -> str:
    api_url = f"{get_api_url()}/auth/login"
    http_res = requests.post(api_url, json={
        'username': username,
        'password': password,
    })
    json_res_body = json.loads(http_res.content.decode())
    return json_res_body['data']['access_token']


# test data
example_prompt = '''The Flight Instructors, Check Airman and Examiners are considered to be the foundation and
the pillars on which the entire safe and efficient flight operations stand.
Careful selection system for Instructor Pilot, Check Airman and Examiners is developed to
ensure a high standard product of the training and checking process. The Instructor Pilot must
be basically a Role Model.
The initial selection therefore shall be based on many factors, included but not limited to:
1) Desire to do the job.
2) Self-discipline.
3) Experience and proficiency.
4) High standard of aviation knowledge.
5) Positive attitude.
6) Ability to work in a team.
7) Socially respected among colleagues.
8) Strong work ethics.
9) Leadership.
10) Teaching ability.
11) Flexibility.
Selected Instructor Pilot, Check Airman shall undergo a training program to develop teaching
skills, techniques and Right-Hand Seat training program.
The performance and adherence of flight instructors to the rules, procedures and regulations
contained in the OM - PART D shall be closely supervised by the operations director.
The Training Manager may authorize the use of external instructors for training. External
instructors shall only be utilized for training duties. In all cases, the Training Manager shall
retain responsibility for the standards of training.
Specific approval is required from the Authority for the use of external instructors
In some cases, and due to operational and training demand or when a new equipment is
entering service, foreign instructors from the manufacturer or any other ICAO approved
organization may be used to cover those specific needs.
Approval requirements to use foreign instructors
(a) A copy of the instructor license will be attached to the approval request to the ECAA.
(b) If simulator training only is required the training can be started after receiving the
approval from the ECAA.
(c) In case flight training (base training) or line training is required the provisions of the
policy in (type rated contract pilot) in 1.7.11 shall apply.
(d) Must demonstrate a sufficient level of English language proficiency of not less than 4
according to ICAO standards in order to be able to:
1) Communicate effectively during their operation.
2) Understand information in the company F.O.M'''
