import random
import requests
import json
import os
from pymongo import MongoClient
import hmac
import hashlib

_SERVER_ADDR = "127.0.0.1"
_SERVER_PORT = 8081
_hmac_key: str = os.getenv('HMAC_KEY')


def get_api_url():
    return f"http://{_SERVER_ADDR}:{_SERVER_PORT}/api"


def get_file_server_url():
    return f"http://{_SERVER_ADDR}:{_SERVER_PORT}"


def login_user(username: str, password: str) -> str:
    api_url = f"{get_api_url()}/auth/login"
    http_res = requests.post(
        api_url,
        json={
            "username": username,
            "password": password,
        },
    )
    json_res_body = json.loads(http_res.content.decode())
    return json_res_body["data"]["access_token"]


def get_database():
    connection_string = (
        f"mongodb://{os.environ['MDB_USERNAME']}:{os.environ['MDB_PASSWORD']}@127.0.0.1"
    )
    mdb_client = MongoClient(connection_string)

    if mdb_client:
        return mdb_client[os.environ["IVDMS_DB"]]
    return None


def hash_password(password: str) -> str:
    return hmac.new(_hmac_key.encode(), password.encode(), hashlib.sha512).hexdigest()


# FLT 3.1.1
text = "The Operator shall ensure the designation of a common language(s) for use by all flight crew members for communication: (i) On the flight deck during line operations; (ii) If the Operator conducts passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and evaluation activities."
random_sentences = [
    "The importance of effective communication in aviation cannot be overstated.",
    "Pilots undergo rigorous training to handle various scenarios during flights.",
    "Weather conditions play a crucial role in flight planning and execution.",
    "Modern aircraft are equipped with advanced avionics systems for navigation and communication.",
    "Air traffic control guides pilots through crowded airspace to ensure safe flights.",
    "Maintaining situational awareness is paramount for flight crew members.",
    "Crew resource management techniques enhance teamwork and decision-making in aviation.",
    "Emergency procedures are practiced regularly to ensure quick and effective responses.",
    "Pilots rely on a combination of instruments and visual cues for navigation.",
    "International flights require adherence to specific protocols and regulations.",
    "Simulators provide realistic training environments for pilots to practice various scenarios.",
    "Fatigue management is a critical aspect of pilot training and operations.",
    "The aviation industry continually evolves with advancements in technology.",
    "Crosswind landings require skillful handling by experienced pilots.",
    "Aircraft maintenance schedules are meticulously planned and executed.",
    "Flight attendants play a vital role in ensuring passenger safety and comfort.",
    "Airports implement security measures to safeguard passengers and personnel.",
    "Communication breakdowns can lead to misunderstandings and errors in flight operations.",
    "Aircraft manufacturers prioritize safety and reliability in aircraft design.",
    "Pilots undergo recurrent training to stay current with regulations and procedures.",
    "Flight planning involves consideration of fuel requirements, weather, and alternate routes."
]

partial_compliant_text = []
for i in range(20):
    for sentence in text.split(';'):
        sentence = sentence.strip()
        if sentence:
            paragraph = [sentence] + random.sample(random_sentences, 3)
            partial_compliant_text.append(' '.join(paragraph))

# test data
full_compliant_text = ["The Operator must guarantee the choice of a shared language(s) for communication among all flight crew members: (i) While on the flight deck during line operations; (ii) If the Operator operates passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) Throughout flight crew training and assessment exercises.",
                       "The Operator is required to ensure the adoption of a common language(s) for communication among all flight crew members: (i) On the flight deck during line operations; (ii) When the Operator conducts passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) Throughout flight crew training and assessment activities.",
                       "The Operator needs to ensure the selection of a common language(s) for communication among all flight crew members: (i) On the flight deck during line operations; (ii) If the Operator operates passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and evaluation sessions.",
                       "The Operator should ensure the designation of a shared language(s) for use by all flight crew members for communication: (i) On the flight deck during line operations; (ii) If the Operator conducts passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and assessment activities.",
                       "The Operator must ensure the establishment of a common language(s) for use by all flight crew members for communication: (i) On the flight deck during line operations; (ii) If the Operator carries out passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and evaluation procedures.",
                       "The Operator is responsible for ensuring the selection of a common language(s) for communication among all flight crew members: (i) While on the flight deck during line operations; (ii) If the Operator conducts passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and evaluation activities.",
                       "The Operator must ensure the appointment of a common language(s) for communication among all flight crew members: (i) On the flight deck during line operations; (ii) If the Operator operates passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) Throughout flight crew training and assessment sessions.",
                       "The Operator should ensure the designation of a shared language(s) for use by all flight crew members for communication: (i) On the flight deck during line operations; (ii) If the Operator conducts passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and evaluation exercises.",
                       "The Operator is required to ensure the selection of a common language(s) for communication among all flight crew members: (i) While on the flight deck during line operations; (ii) If the Operator conducts passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and assessment sessions.",
                       "The Operator needs to ensure the establishment of a common language(s) for communication among all flight crew members: (i) On the flight deck during line operations; (ii) If the Operator operates passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and evaluation activities.",
                       "The Operator should ensure the appointment of a shared language(s) for use by all flight crew members for communication: (i) On the flight deck during line operations; (ii) If the Operator conducts passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and assessment procedures.",
                       "The Operator must guarantee the selection of a common language(s) for communication among all flight crew members: (i) While on the flight deck during line operations; (ii) If the Operator operates passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) Throughout flight crew training and evaluation exercises.",
                       "The Operator is responsible for ensuring the designation of a common language(s) for communication among all flight crew members: (i) On the flight deck during line operations; (ii) If the Operator conducts passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) Throughout flight crew training and assessment procedures.",
                       "The Operator must ensure the appointment of a common language(s) for use by all flight crew members for communication: (i) On the flight deck during line operations; (ii) If the Operator operates passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and evaluation sessions.",
                       "The Operator should ensure the selection of a shared language(s) for use by all flight crew members for communication: (i) On the flight deck during line operations; (ii) If the Operator conducts passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and assessment exercises.",
                       "The Operator is required to ensure the designation of a common language(s) for communication among all flight crew members: (i) While on the flight deck during line operations; (ii) If the Operator conducts passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) Throughout flight crew training and evaluation procedures.",
                       "The Operator needs to ensure the appointment of a common language(s) for communication among all flight crew members: (i) On the flight deck during line operations; (ii) If the Operator operates passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and assessment activities.",
                       "The Operator should ensure the establishment of a shared language(s) for use by all flight crew members for communication: (i) On the flight deck during line operations; (ii) If the Operator conducts passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and evaluation sessions.",
                       "The Operator is required to ensure the appointment of a common language(s) for communication among all flight crew members: (i) While on the flight deck during line operations; (ii) If the Operator conducts passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and assessment exercises.",
                       "The Operator needs to ensure the selection of a shared language(s) for use by all flight crew members for communication: (i) On the flight deck during line operations; (ii) If the Operator operates passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and evaluation procedures.",
                       "The Operator shall ensure that a mutually agreed-upon language(s) is designated for communication among all flight crew members: (i) On the flight deck during regular operations; (ii) If the Operator conducts flights with cabin crew, between the flight crew and cabin crew during regular operations; (iii) During flight crew training and assessment activities.",
                       "The Operator must guarantee the selection of a common language(s) for communication among all flight crew members: (i) On the flight deck during operational flights; (ii) If the Operator conducts flights with cabin crew, between the flight crew and cabin crew during operational flights; (iii) During flight crew training and evaluation exercises.",
                       "The Operator is responsible for ensuring the appointment of a common language(s) for communication among all flight crew members: (i) On the flight deck during scheduled operations; (ii) If the Operator conducts flights with cabin crew, between the flight crew and cabin crew during scheduled operations; (iii) Throughout flight crew training and assessment sessions.",
                       "The Operator should ensure the selection of a shared language(s) for use by all flight crew members for communication: (i) On the flight deck during routine operations; (ii) If the Operator conducts flights with cabin crew, between the flight crew and cabin crew during routine operations; (iii) During flight crew training and evaluation procedures.",
                       "The Operator is required to ensure the designation of a common language(s) for communication among all flight crew members: (i) While on the flight deck during regular flights; (ii) If the Operator conducts flights with cabin crew, between the flight crew and cabin crew during regular flights; (iii) Throughout flight crew training and assessment exercises.",
                       "The Operator needs to ensure the establishment of a common language(s) for communication among all flight crew members: (i) On the flight deck during standard operations; (ii) If the Operator operates flights with cabin crew, between the flight crew and cabin crew during standard operations; (iii) During flight crew training and evaluation activities.",
                       "The Operator should ensure the appointment of a shared language(s) for use by all flight crew members for communication: (i) On the flight deck during normal operations; (ii) If the Operator operates flights with cabin crew, between the flight crew and cabin crew during normal operations; (iii) During flight crew training and assessment exercises.",
                       "The Operator must ensure the selection of a common language(s) for communication among all flight crew members: (i) On the flight deck during everyday operations; (ii) If the Operator conducts flights with cabin crew, between the flight crew and cabin crew during everyday operations; (iii) Throughout flight crew training and assessment sessions.",
                       "The Operator is responsible for ensuring the designation of a common language(s) for communication among all flight crew members: (i) While on the flight deck during daily flights; (ii) If the Operator conducts flights with cabin crew, between the flight crew and cabin crew during daily flights; (iii) During flight crew training and evaluation procedures.",
                       "The Operator must ensure the appointment of a common language(s) for use by all flight crew members for communication: (i) On the flight deck during typical operations; (ii) If the Operator operates flights with cabin crew, between the flight crew and cabin crew during typical operations; (iii) During flight crew training and assessment activities.",
                       "The Operator should ensure the selection of a shared language(s) for use by all flight crew members for communication: (i) On the flight deck during ordinary operations; (ii) If the Operator conducts flights with cabin crew, between the flight crew and cabin crew during ordinary operations; (iii) During flight crew training and evaluation sessions.",
                       "The Operator is required to ensure the designation of a common language(s) for communication among all flight crew members: (i) While on the flight deck during usual flights; (ii) If the Operator conducts flights with cabin crew, between the flight crew and cabin crew during usual flights; (iii) Throughout flight crew training and assessment exercises.",
                       "The Operator needs to ensure the establishment of a common language(s) for communication among all flight crew members: (i) On the flight deck during typical flights; (ii) If the Operator operates flights with cabin crew, between the flight crew and cabin crew during typical flights; (iii) During flight crew training and evaluation procedures.",
                       "The Operator should ensure the appointment of a shared language(s) for use by all flight crew members for communication: (i) On the flight deck during regular flight operations; (ii) If the Operator operates flights with cabin crew, between the flight crew and cabin crew during regular flight operations; (iii) During flight crew training and assessment activities.",
                       "The Operator must ensure the selection of a common language(s) for communication among all flight crew members: (i) On the flight deck during standard flight operations; (ii) If the Operator conducts flights with cabin crew, between the flight crew and cabin crew during standard flight operations; (iii) Throughout flight crew training and assessment sessions.",
                       "The Operator is responsible for ensuring the designation of a common language(s) for communication among all flight crew members: (i) While on the flight deck during routine flights; (ii) If the Operator conducts flights with cabin crew, between the flight crew and cabin crew during routine flights; (iii) During flight crew training and evaluation exercises.",
                       "The Operator must ensure the appointment of a common language(s) for use by all flight crew members for communication: (i) On the flight deck during normal flight operations; (ii) If the Operator operates flights with cabin crew, between the flight crew and cabin crew during normal flight operations; (iii) During flight crew training and assessment activities.",
                       "The Operator should ensure the selection of a shared language(s) for use by all flight crew members for communication: (i) On the flight deck during regular flight procedures; (ii) If the Operator conducts flights with cabin crew, between the flight crew and cabin crew during regular flight procedures; (iii) During flight crew training and evaluation sessions.",
                       "The Operator is required to ensure the designation of a common language(s) for communication among all flight crew members: (i) While on the flight deck during typical flight operations; (ii) If the Operator conducts flights with cabin crew, between the flight crew and cabin crew during typical flight operations; (iii) Throughout flight crew training and assessment exercises.",
                       "The Operator needs to ensure the establishment of a common language(s) for communication among all flight crew members: (i) On the flight deck during standard flight procedures; (ii) If the Operator operates flights with cabin crew, between the flight crew and cabin crew during standard flight procedures; (iii) During flight crew training and evaluation activities.",
                       "The Operator should ensure the appointment of a shared language(s) for use by all flight crew members for communication: (i) On the flight deck during ordinary flight operations; (ii) If the Operator operates flights with cabin crew, between the flight crew and cabin crew during ordinary flight operations; (iii) During flight crew training and assessment exercises.",
                       "The Operator must ensure the selection of a common language(s) for communication among all flight crew members: (i) While on the flight deck during line operations; (ii) If the Operator operates passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and evaluation sessions. It's imperative for the Operator to regularly assess language proficiency and provide necessary language training.",
                       "In order to maintain effective communication, the Operator should establish a common language(s) for all flight crew members: (i) On the flight deck during line operations; (ii) If the Operator conducts passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and assessment activities. Additionally, the Operator may consider cultural sensitivity training to enhance communication efficiency.",
                       "The Operator is responsible for ensuring seamless communication among flight crew members by designating a common language(s): (i) While on the flight deck during line operations; (ii) If the Operator operates passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and evaluation procedures. Moreover, implementing standardized communication protocols can further enhance operational safety.",
                       "Ensuring effective communication among flight crew members is crucial for safe operations. The Operator must designate a common language(s) for use in various scenarios: (i) On the flight deck during line operations; (ii) If the Operator conducts passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and assessment activities. Additionally, incorporating language proficiency as part of recurrent training can bolster communication skills.",
                       "The Operator needs to establish clear communication protocols by designating a common language(s) for all flight crew members: (i) On the flight deck during line operations; (ii) If the Operator operates passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and evaluation sessions. Furthermore, fostering a culture of open communication can mitigate misunderstandings during critical operations.",
                       "To facilitate effective communication, the Operator should designate a common language(s) for all flight crew members: (i) On the flight deck during line operations; (ii) If the Operator conducts passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and assessment exercises. Additionally, implementing multilingual communication aids can serve as a backup during language barriers.",
                       "Effective communication among flight crew members is paramount for operational safety. Therefore, the Operator must ensure the selection of a common language(s): (i) While on the flight deck during line operations; (ii) If the Operator operates passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and evaluation procedures. Moreover, promoting a culture of linguistic diversity can enrich team collaboration.",
                       "In order to promote efficient communication, the Operator should designate a common language(s) for all flight crew members: (i) On the flight deck during line operations; (ii) If the Operator conducts passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and assessment sessions. Additionally, conducting regular communication drills can enhance response times during emergencies.",
                       "Ensuring effective communication among flight crew members requires the Operator to designate a common language(s): (i) While on the flight deck during line operations; (ii) If the Operator operates passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and evaluation activities. Furthermore, implementing real-time translation tools can facilitate communication in diverse linguistic environments.",
                       "To maintain operational efficiency, the Operator must designate a common language(s) for all flight crew members: (i) On the flight deck during line operations; (ii) If the Operator conducts passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and assessment exercises. Moreover, encouraging cross-cultural communication workshops can foster a more inclusive work environment.",
                       "In order to enhance operational safety, the Operator should establish a common language(s) for communication among flight crew members: (i) On the flight deck during line operations; (ii) If the Operator operates passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and evaluation sessions. Additionally, providing language refresher courses can help maintain proficiency levels.",
                       "Effective communication is essential for safe flight operations. Therefore, the Operator must designate a common language(s) for all flight crew members: (i) While on the flight deck during line operations; (ii) If the Operator conducts passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and assessment activities. Furthermore, fostering a supportive environment for language learning can improve communication skills over time.",
                       "To ensure smooth operations, the Operator should designate a common language(s) for communication among flight crew members: (i) On the flight deck during line operations; (ii) If the Operator operates passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and evaluation procedures. Moreover, integrating language proficiency assessments into regular performance evaluations can help track improvements.",
                       "Maintaining effective communication is crucial for aviation safety. Therefore, the Operator must designate a common language(s) for all flight crew members: (i) While on the flight deck during line operations; (ii) If the Operator conducts passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and assessment sessions. Additionally, establishing clear communication protocols can minimize the risk of misunderstandings.",
                       "The Operator must ensure seamless communication among flight crew members by designating a common language(s): (i) On the flight deck during line operations; (ii) If the Operator operates passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and evaluation activities. Additionally, organizing cross-cultural workshops can promote better understanding and cooperation among crew members.",
                       "In order to enhance operational efficiency, the Operator should designate a common language(s) for communication among flight crew members: (i) On the flight deck during line operations; (ii) If the Operator conducts passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and assessment exercises. Moreover, incorporating language proficiency as part of crew resource management training can improve teamwork and decision-making skills.",
                       "Ensuring effective communication among flight crew members is essential for operational safety. Therefore, the Operator must designate a common language(s): (i) While on the flight deck during line operations; (ii) If the Operator operates passenger flights with cabin crew, between the flight crew and cabin crew during line operations; (iii) During flight crew training and evaluation procedures. Additionally, providing language immersion programs can enhance fluency and comprehension.",
                       ]
non_compliant_text = [
    """1.3 Authorities and Responsibilities of Operations Management and Non- Management
Personnel
Ref. Corporate Manual Ch.1
Nesma Airlines has a flight operations management system that thoroughly defines the
authorities and responsibilities of management and non-management personnel that perform
functions relevant to the safety or security of aircraft operations in areas of the flight operations
organization. The management system shall also specify:
i. The levels of management with the authority to make decisions that affect the safety
and/or security of operations;
ii. Responsibilities for ensuring operations are conducted in accordance with applicable
regulations and standards of Nesma Airlines
iii. Lines of accountability throughout flight operations, including direct accountability for
safety and/or security on the part of flight operations senior management.""",
    """1.3.1 Accountable Executive
Accountable Executive Job Description (ECAR 121.71) (a)
The Accountable Executive of Nesma Airlines who has the accountability for safety and
security performance, he has the authority to take necessary actions to ensure the management
system is effective.
Responsibilities:
- Irrespective of other functions, has ultimate responsibility and accountability on behalf
of Nesma Airlines for the implementation and maintenance of the safety management
system (SMS) throughout the organization.
- Maintain an adequate organization as required by the AOC and notify the ECAA as
soon as practicable of any major changes in the organization;
- Has the authority to ensure the allocation of resources necessary to manage safety and
security risks to aircraft operations
- Management of safety risks & security threats
- To ensure that a Nesma airline continues to meet applicable requirements, the
Accountable Executive is authorized to designate a director/manager with the
responsibility for monitoring compliance. The role of such Director/manager would be
to ensure that the SMS activities of Nesma Airlines are monitored for compliance with
the applicable regulatory requirements, as well as any additional requirements as
established by Nesma Airlines, and that these activities are being carried out properly
under the supervision of the relevant head of functional area.
- Represent the company in all matters pertaining to business.
- Manages improvement projects that are proposed by Nesma Airlines Safety Review
Board.
- Allocate resources required to implement and maintain effective Safety and Quality
Management System.
- Managing major operational process within the upper management level, and
coordinating with other organizations concerned in cross functional activities and
UNCONTROLLED
processes affecting their performance.""",
    """Ref: Corp. Manual Chapter 1.
a) Nesma Airlines has communication system that enables and ensures an exchange of
operationally relevant information throughout the management system and areas where
operations and maintenance activities are conducted.
b) This effective communication system ensures an exchange of relevant operational
information throughout all areas of the organization, to include senior managers,
operational managers and front line personnel. To be completely effective, the
communication system also includes external organizations that conduct outsourced
operational functions.
c) Methods of communication are as uncomplicated and easy to use as is possible, and
facilitate the reporting of operational deficiencies, hazards or concerns by operational
personnel.
d) Communications methods include but are not limited to:
- Telephone lines, Faxes, SATCOM communications, reports, letters, internet, web
site (www.nesmaairlines.com), circulars, memos and official company email
service. This is in addition to meetings and interviews.
- FlyCo content distribution as illustrated and controlled in OM-D chapter 6.
- Intranet. Refer to 1.6.2.4 Nesma Airlines Intranet.
- As part of Nesma Airlines expansion, other electronic communication tools can be
used as long as they are managed and controlled as elaborated in 1.6.2.3
Management and Control of Electronic Communication Tools.
e) Communication with external organizations that conduct outsourced operational
functions to Nesma Airlines always will be conducted through all/any of the mentioned
communication methods in point (d).
f) The system facilitates using the safety reporting (including voluntarily and confidential
reporting) system by all operational personnel and all staff to report of operational
deficiencies, hazards or safety concerns (see SMS manual chapter 2.1)
g) Every department may issue other reporting forms in addition to the mentioned above
to facilitate collection of data to be used for performance measurements to support
operations improvements.
Safety Communication
To improve safety culture within the organization, all employees receive ongoing information
on safety issues, safety metrics, specific hazards existing through different ways which includes
but not limited to safety bulletins, safety circulars, flight crew safety notices, safety Magazine.
(Refer to SMS Manual chapter 4.2 - Safety communication)""",
    """1.8.2 Falsification, Reproduction, or Alteration of Applications, Certificates, Logbook,
Reports or Records
No person may make or cause to be made:
1. Any fraudulent or intentionally false statement on any application for a certificate rating
or duplicate thereof issued under this part.
2. Any fraudulent or intentionally false entry in any logbook, records, or report that
required to be kept, made, or used to show compliance with any requirements for the
issuance, or exercise of the privileges, or any certificate or rating under this part;
3. Any alteration of any certificate or rating under this part, or
4. Any reproduction for fraudulent purpose, of any certificate or rating issued by ECAA
is prohibited and is a basis for the ECAA to suspend or revoke any airman, ground,
instructor, dispatcher, or medical certificate or rating held by that person""",
    """1.8.2.1 Extra Crew Travel Requirements
Following extra crew travel requirements have been received from Immigration Authorities,
these requirements are subject to changes by the above-mentioned authorities. Therefore, you
are required to obtain the latest information from Flight Operations Crew Affairs before you
travel as extra crew provided that all company procedures are fulfilled and commercial
authorization is granted""",
    """1.8.4.1 Alcoholic Drinks
Alcohol concentration: No employee shall report for duty or remain on duty requiring the
performance of safety-sensitive functions while having an alcohol concentration of 0.02 or
greater. No certificate holder having actual knowledge that an employee has an alcohol
concentration of 0.02 or greater shall permit the employee to perform or continue to perform
safety-sensitive functions.
a) On-duty use: No employee shall use alcohol while performing safety-sensitive
functions. No certificate holder having actual knowledge that an employee is using
alcohol while performing safety-sensitive functions shall permit the employee to
perform or continue to perform safety-sensitive functions.
b) Pre-duty use:
1. No employee shall perform cockpit crewmember or cabin crew duties within 8
hours after using alcohol. No certificate holder having actual knowledge that such
an employee has used alcohol within 8 hours shall permit the employee to perform
or continue to perform the specified duties.
2. No employee shall perform safety-sensitive duties other than those specified in
paragraph (b) (1) of this section within 4 hours after using alcohol. No certificate
holder having actual knowledge that such an employee has used alcohol within 4
hours shall permit the employee to perform or continue to perform safety-sensitive
functions.
If as a result of the effects of alcohol, a flying crewmember is either incapable of discharging
his duties or the ability to carry them out is impaired, it will be understood that he has
committed gross misconduct, the penalty for which will be dismissal without notice or prior
warnings.
Alcoholic drinks must not be consumed by flying staff during the eight hours before reporting
for a roistered service or standby duty. There should be less than 0.02 of alcohol concentration
in the blood of crew when reporting for duty.
Crews may be requested to undergo a Breathalyzer check on a random basis. Refusal or
declination to participate in the process will be considered as gross misconduct. For Alcoholic
Testing Program (Refer to Appendix A)
""",
    """2.1.2 License and Qualification Validity
The supervision of license and qualification validity is ensured -through Crew Management
System- by:
▪ Following up qualifications, licenses validity, flight activity, and duty and rest time of
the crewmembers and of the operations personnel.
▪ Checking that crewmembers designated to fly have medical check (depending on age
and according to Egyptian Civil Aviation Regulations which laid down in the following
table):
Pilot Age (Birthday) Medical check validation
Up to 60 Years old 12 months
60-65 years old 6 months
Moreover, flight license and rate qualification valid and appropriate to the scheduled flights.
Each license entitles its holder to exercise its privilege, this as long as it remains valid. It is the
holder's responsibility to perform the required checks and tests for revalidation.
Flight crew licenses validity is checked regularly by the Crew Scheduling sections that is in
charge of scheduling, in due time, licensed personnel for appropriate retraining and checks.""",
    """2.1.3 Competence of Operations Personnel
The supervision of the competence of the operations personnel is achieved by:
▪ Ensuring that the personnel assigned to, or directly involved in, ground and flight
operations are properly instructed and have demonstrated their abilities in their
particular duties. Qualification requirements are defined in chapter 5.
▪ Ensuring that the personnel can communicate in a common language and that they are
able to understand those parts of the Operations Manual, which pertains to their duties
and responsibilities.
▪ Competence of operations personnel is monitored:
▪ For flight crewmembers: by flight inspections, check flights or simulator sessions (by
Chief Pilot, Director of Operations , Training Manager or their delegates)and automated
QAR (or DFDR)analysis managed by the Safety Manager (FOQA program).
▪ For ground personnel: by appropriate checks conducted by department managers. For
certain positions (e.g. dispatchers), a specific license or qualification ensures the
required competence is fulfilled.
▪ Regular audits (refer to 3.5 Quality Assurance Program)
Supervision and monitoring of the competence of operations personnel will be used to adapt """
]


example_prompt = """The Flight Instructors, Check Airman and Examiners are considered to be the foundation and
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
2) Understand information in the company F.O.M"""

dummy_prompt = """The module used to set the rules by which the system will restrict crew assignment. Rule set
management is used to enter crew assignment regulations and standards. Rule setting
compliance with regulations is the responsibility of the chief pilot and shall be restricted to his
access. Crew scheduling department shall have no access to change the rules."""

valid_prompt = """English and Arabic are the designated common language used by all Nesma Airlines flight
crewmembers for communication.
Personnel who demonstrate proficiency below expert level (ICAO Level 6) should be formally
evaluated at intervals in accordance with ECAR 63.9 and ICAO Annex 1 item 1.2.9.6 as
follows:
- Those demonstrated language proficiency at the operational level (Level 4) should be
evaluated at least once every three years
- Those demonstrated language proficiency at the operational level (Level 5) should be
evaluated at least once every six years
ECAA requires level four of English language as a minimum level. All operational
communications shall be established and maintained in English:
1. On the flight deck during line operation.
2. Between flight crew and cabin crew during line operation.
3. During flight crew training and evaluation activities.
4. In normal operations, abnormal and emergency situations
5. In the event of incapacitation of any crewmember"""
