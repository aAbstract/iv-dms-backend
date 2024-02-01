# manuals schema
# seed_sections = [
#     ManualSection(
#         header='1.1 Organizational Structure',
#         order=1,
#         text='''
#         The following organization chart depicts the company and the flight operations department
#         organizational structure.
#         They show the relationship between the various departments of the company and the associated
#         subordination and reporting lines and control of flight operations and the management of safety
#         and security outcomes.
#         Director of Operations ensures that communication within his department and other
#         departments are established in a way that guarantees the exchange of relevant operational
#         information.
#         ''',
#         regulations_codes=[ManualRegulationCode(type=RegulationType.IOSA, cat_code='FLT', code='FLT 1.1.1')],
#     ),
#     ManualSection(
#         header='1.2 Nominated Post Holders',
#         order=2,
#         text='''
#         - The nominated post holders must have managerial competency and appropriate
#         technical and operational qualifications;
#         - Their contract of employment must allow them to work sufficient hours, in order to be
#         able to satisfactorily perform the functions associated with the operation of
#         AIRCAIRO, apart from any flying duties;
#         - Nominated post holders and managers have the responsibility, and they are accountable,
#         for ensuring:
#             • Flight operations are conducted in accordance with the conditions and restrictions
#             of the AOC and in compliance with the applicable regulations and standards of
#             AIRCAIRO and other applicable rules and requirements (e.g., IOSA
#             Requirements);
#             • The management and supervision of all flight operations activities;
#             • The management of safety and security in flight operations;
#         - All required management Personnel and Post holders mentioned in the OM Part A
#         should fulfill the qualifications required by the ECAR (part 121) and AIRCAIRO
#         policies.
#         NOTE: Nominat
#         ''',
#         regulations_codes=[
#             ManualRegulationCode(type=RegulationType.IOSA, cat_code='FLT', code='FLT 1.1.2'),
#             ManualRegulationCode(type=RegulationType.IOSA, cat_code='FLT', code='FLT 1.3.4'),
#             ManualRegulationCode(type=RegulationType.IOSA, cat_code='FLT', code='FLT 1.5.2'),
#         ],
#     ),
# ]
# seed_manual = Manual(
#     name='Air Cairo FLT 3',
#     chapters=[
#         ManualChapter(name='Chapter 1 Organization and Responsibilities', order=1, sections=seed_sections),
#     ],
# )

# print('seeding example manual...')
# db.manuals.insert_one(seed_manual.model_dump())

# [
#     IOSASection(
#         name="Section 2 Flight Operations",
#         code="FLT",
#         applicability="addresses safety and security requirements for flight operations, and is applicable to an operator that uses two-pilot, multi-engine aircraft with a maximum certificated takeoff mass in excess of 5,700 kg (12,566 lbs.).",
#         guidance="The definitions of technical terms used in this ISM Section 2, as well as the list of abbreviations and acronyms, are found in the IATA Reference Manual for Audit Programs (IRM).",
#         order=2,
#         items=[
#             IOSAItem(
#                 code='FLT 1.1.1',
#                 guidance='Refer to the IRM for the definitions of Operations and Operator.',
#                 iosa_map=['1 Management and Control', '1.1 Management System Overview'],
#                 constraints=[
#                     Constrain(text='The Operator shall have a management system for the flight operations organization that ensures control of flight operations and the management of safety and security outcomes.'),
#                     Constrain(text='Sample Constain'),
#                 ],
#             ),
#             IOSAItem(
#                 code='FLT 1.1.2',
#                 guidance='Refer to the IRM for the definitions of Accountability, Authority, Post Holder and Responsibility.',
#                 iosa_map=['1 Management and Control', '1.1 Management System Overview'],
#                 constraints=[Constrain(
#                     text='The Operator shall have one or more designated managers in the flight operations organization that, if required, are post holders acceptable to the Authority, and have the responsibility for ensuring:',
#                     children=[
#                         Constrain(text='The management and supervision of all flight operations activities.'),
#                         Constrain(text='The management of safety and security risks to flight operations.'),
#                         Constrain(text='Flight operations are conducted in accordance with conditions and restrictions of the Air Operator Certificate (AOC), and in compliance with applicable regulations and standards of the Operator.'),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code='FLT 1.3.4',
#                 guidance='Refer to Guidance associated with ORG 1.3.3 located in ISM Section 1 regarding the need to coordinate and communicate with external entities.',
#                 iosa_map=['1 Management and Control', '1.3 Accountability, Authorities and Responsibilities'],
#                 constraints=[
#                     Constrain(
#                         text='The Operator shall ensure pilot flight crew members complete an evaluation that includes a demonstration of knowledge of the operations approved as part of the Air Operator Certificate (AOC). Such evaluation shall include a demonstration of knowledge of:',
#                         children=[
#                             Constrain(text='Approaches authorized by the Authority.'),
#                             Constrain(text='Ceiling and visibility requirements for takeoff, approach and landing.'),
#                             Constrain(text='Allowance for inoperative ground components.'),
#                             Constrain(text='Wind limitations (crosswind, tailwind and, if applicable, headwind).'),
#                         ],
#                     ),
#                     Constrain(
#                         text='Sample Constrain',
#                         children=[
#                             Constrain(text='item 1'),
#                             Constrain(text='item 2'),
#                             Constrain(text='item 3'),
#                             Constrain(text='item 4'),
#                         ],
#                     ),
#                 ],
#             ),
#             IOSAItem(
#                 code='FLT 1.5.2',
#                 guidance='Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.',
#                 iosa_map=['1 Management and Control', '1.5 Provision of Resources'],
#                 constraints=[Constrain(text='The Operator shall have a selection process for management and non-management positions within the organization that require the performance of functions relevant to the safety or security of aircraft operations.')],
#             ),
#             IOSAItem(
#                 code='FLT 2.1.35',
#                 guidance='',
#                 iosa_map=[],
#                 constraints=[
#                     Constrain(
#                         text='The Operator shall have an initial training program for instructors, evaluators and line check airmen,to include:',
#                         children=[
#                             Constrain(
#                                 text='An instructor course that addresses as a minimum',
#                                 children=[
#                                     Constrain(text='The fundamentals of teaching and evaluation'),
#                                     Constrain(text='Lesson plan management'),
#                                     Constrain(text='Briefing and debriefing'),
#                                     Constrain(text='Human performance issues'),
#                                     Constrain(text='Company policies and procedures'),
#                                     Constrain(text='Simulator serviceability and training in simulator operation'),
#                                     Constrain(text='If the Operator conducts training flights, dangers associated with simulating system failures in flight'),
#                                     Constrain(text='As applicable, the simulated or actual weather and environmental conditions necessary to conduct each simulator or aircraft training/evaluation session to be administered'),
#                                 ],
#                             )
#                         ],
#                     ),
#                     Constrain(text='The Operator shall have a management system for the flight operations organization that ensures control of flight operations and the management of safety and security outcomes.'),
#                 ],
#             ),
#             IOSAItem(
#                 code='FLT 2.1.21',
#                 guidance='',
#                 iosa_map=[],
#                 constraints=[Constrain(text='The Operator shall have sufficient instructors, evaluators, line check airmen and support personnel to administer the training and evaluation programs in accordance with requirements of the Operator and/or the State, as applicable.')],
#             ),
#             IOSAItem(
#                 code="FLT 3.1.1",
#                 guidance="Refer to the IRM for the definitions of Operations and Operator.",
#                 iosa_map=["3 Line Operations", "3.1 Common Language"],
#                 constraints=[
#                     Constrain(
#                         text="The Operator shall ensure the designation of a common language(s) for use by all flight crew members for communication:",
#                         children=[
#                             Constrain(text="On the flight deck during line operations"),
#                             Constrain(text="If the Operator conducts passenger flights with cabin crew, between the flight crew and cabin crew during line operations"),
#                             Constrain(text="During flight crew training and evaluation activities"),
#                         ],
#                     ),
#                 ],
#             ),
#             IOSAItem(
#                 code="FLT 3.2.1",
#                 guidance="Refer to the IRM for the definitions of Operations and Operator.",
#                 iosa_map=["3 Line Operations", "3.2 Flight Crew Responsibilities"],
#                 constraints=[Constrain(
#                     text="The Operator shall ensure the PIC is assigned the responsibility for recording the following information for each flight:",
#                     children=[
#                         Constrain(text="Aircraft registration"),
#                         Constrain(text="Date"),
#                         Constrain(text="Flight number"),
#                         Constrain(text="Flight crew names and duty assignment"),
#                         Constrain(text="Departure and arrival airports"),
#                         Constrain(text="ATD, ATA, flight time"),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.3.1",
#                 guidance="Refer to the IRM for the definitions of Operations and Operator.",
#                 iosa_map=["3 Line Operations", "3.3 Flight Crew Qualifications"],
#                 constraints=[Constrain(text="The Operator shall specify the composition and required number of flight crew members taking into account the type of aircraft, flight crew qualification requirements and flight/duty time limitations.")],
#             ),
#             IOSAItem(
#                 code="FLT 3.3.2",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.3 Flight Crew Qualifications"],
#                 constraints=[Constrain(text="The Operator shall have guidance and criteria that address the pairing of inexperienced pilot crewmembers and ensure scheduling processes prevent inexperienced pilot flight crew members, asdefined by the Operator or the State, from operating together.")],
#             ),
#             IOSAItem(
#                 code="FLT 3.3.3",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.3 Flight Crew Qualifications"],
#                 constraints=[Constrain(text="If the Operator conducts low visibility approaches, the Operator shall define a minimum level ofcommand experience required for a pilot to be authorized to conduct such approaches as PIC toapproved Operator minima.")],
#             ),
#             IOSAItem(
#                 code="FLT 3.3.4",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.3 Flight Crew Qualifications"],
#                 constraints=[Constrain(text="The Operator shall ensure flight crew members will not operate an aircraft unless issued a medicalassessment in accordance with requirements of the State; such assessment shall not be valid for aperiod greater than 12 months.")],
#             ),
#             IOSAItem(
#                 code="FLT 3.3.5",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.3 Flight Crew Qualifications"],
#                 constraints=[Constrain(
#                     text="If the Operator conducts international flight operations, the Operator shall ensure either of the following apply to flight crew members that operate such flights:",
#                     children=[
#                         Constrain(text="The Operator has a method to prevent such crew members from acting as a pilot after having attained their 65th birthday, or"),
#                         Constrain(text="Where laws or regulations of the State do not permit maximum age limits, the Operator hasa method, which is acceptable to the State and other applicable states, for making adetermination that pilot flight crew members are no longer permitted to exercise theprivileges of their pilot license in international operations for the operator."),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.3.6",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.3 Flight Crew Qualifications"],
#                 constraints=[],
#             ),
#             IOSAItem(
#                 code="FLT 3.3.9",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.3 Flight Crew Qualifications"],
#                 constraints=[Constrain(
#                     text="The Operator shall have an airport qualification process that ensures a PIC has made an actualapproach and landing at each airport within the Operator route system accompanied by a pilot,either as a crew member or flight deck observer, that is qualified for that airport, unless:",
#                     children=[
#                         Constrain(text="The approach to the airport is not over difficult terrain and the instrument approachprocedures and aids available are similar to those with which the pilot is familiar, and thenormal operating minima are adjusted by the addition of a margin of safety that is approvedor accepted by the State, or there is reasonable certainty that approach and landing can bemade in visual meteorological conditions (VMC), or"),
#                         Constrain(text="The descent from the initial approach altitude can be made by day in VMC, or"),
#                         Constrain(text="The Operator has qualified the PIC for operations into the airport by means a pictorial representation that is approved or accepted the Authority, or"),
#                         Constrain(text="The airport is adjacent to another airport into which the PIC is currently qualified to operate."),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.3.10",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.3 Flight Crew Qualifications"],
#                 constraints=[Constrain(
#                     text="The Operator shall have a process to ensure a pilot is not used as a PIC in operations that requirethe application of special skills or knowledge within areas, on routes over difficult terrain and/or intospecial airports, as designated by the State or by the Operator, unless, within the preceding 12months, that pilot has either:",
#                     children=[
#                         Constrain(text="Made at least one trip as a pilot flight crew member, line check airman or observer on theflight deck on a route in close proximity and over similar terrain within the specified area(s),on the specified route and/or into the special airport, as applicable, or"),
#                         Constrain(text="Completed training and an evaluation in the special skills and/or knowledge required toqualify or requalify for such operations. The content of training shall ensure the PIC hasadequate knowledge of the elements specified in Table 2.5 as applicable to the areas,routes, route segments and special airports of intended operation."),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.4.1",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.4 Flight Crew Scheduling"],
#                 constraints=[Constrain(
#                     text="The Operator shall have a means to ensure flight crew members are qualified and current prior toaccepting and/or being assigned to duty. Such means shall consist of:",
#                     children=[
#                         Constrain(text="A requirement that prohibits flight crew members from operating an aircraft if not qualified forduty in accordance with requirements contained in Table 2.3"),
#                         Constrain(text="A scheduling process that ensures flight crew members, prior to being assigned to duty, arequalified and current in accordance with the applicable flight crew qualification requirementscontained in Table 2.3 and, if applicable, additional requirements of the State."),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.4.2",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.4 Flight Crew Scheduling"],
#                 constraints=[Constrain(
#                     text="The Operator shall have a scheduling policy that ensures flight crew members, prior to beingassigned to duty, will not be adversely affected by factors that could impair human performance, toinclude, as a minimum:",
#                     children=[
#                         Constrain(text="Pregnancy"),
#                         Constrain(text="Illness, surgery or use of medication"),
#                         Constrain(text="Blood donation"),
#                         Constrain(text="Deep underwater diving"),
#                         Constrain(text="Fatigue whether occurring in one flight, successive flights or accumulated over a period of time."),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.4.3A",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.4 Flight Crew Scheduling"],
#                 constraints=[Constrain(
#                     text="The Operator shall have a methodology for the purpose of managing fatigue-related safety risks toensure fatigue occurring in one flight, successive flights or accumulated over a period of time doesnot impair a flight crew member's alertness and ability to safely operate an aircraft or perform safety-related duties. Such methodology shall consist of:",
#                     children=[
#                         Constrain(text="Flight time, flight duty period, duty period limitations and rest period requirements that are inaccordance with the applicable prescriptive fatigue management regulations of the State,and/or"),
#                         Constrain(text="If applicable, the Operator's Fatigue Risk Management System (FRMS) approved oraccepted by the State and established in accordance with FLT 3.4.3B."),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.4.3B",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.4 Flight Crew Scheduling"],
#                 constraints=[Constrain(
#                     text="If the Operator uses an FRMS to manage flight crew fatigue-related safety risks, the Operator shallincorporate scientific principles and knowledge within the FRMS, comply with any applicablerequirements for managing flight crew fatigue as established by the State or Authority and, as a minimum:",
#                     children=[
#                         Constrain(text="Define and document the FRMS policy"),
#                         Constrain(text="Incorporate risk management processes for fatigue hazard identification, risk assessment and risk mitigation"),
#                         Constrain(text="Develop and maintain effective FRMS safety assurance processes"),
#                         Constrain(text="Establish and implement effective FRMS promotion processes."),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.4.3C",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.4 Flight Crew Scheduling"],
#                 constraints=[Constrain(text="If the Operator uses an FRMS to manage flight crew fatigue-related safety risks, the Operator shouldensure the organizational activities specified in FLT 3.4.3B related to the management of flight crewfatigue-related risks are integrated with the Operator's organizational safety management system(SMS) as specified in ORG 1.1.10.")],
#             ),
#             IOSAItem(
#                 code="FLT 3.4.4",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.4 Flight Crew Scheduling"],
#                 constraints=[Constrain(
#                     text="The Operator shall consider the following as duty time for the purposes of determining required restperiods and calculating duty time limitations for operating flight crew members:",
#                     children=[
#                         Constrain(text="Entire duration of the flight"),
#                         Constrain(text="Pre-operating deadhead time"),
#                         Constrain(text="Training periods prior to a flight"),
#                         Constrain(text="Administrative or office time prior to a flight (for flight crew members that serve in a management function)"),
#                         Constrain(text="If required by the State, flight time accrued by flight crew members in operations other than those of the Operator."),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.4.6",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.4 Flight Crew Scheduling"],
#                 constraints=[Constrain(
#                     text="If the Operator uses flight crew members that are concurrently qualified to operate aircraft of differenttypes, or operate variants within one type, and the State specifies unique training and/or recencyrequirements for such flight crew members to remain concurrently qualified, the Operator shall havea scheduling process that addresses such unique requirements, to include, as a minimum:",
#                     children=[
#                         Constrain(text="Required differences training (between type or variants)"),
#                         Constrain(text="Recency of experience necessary to maintain currency on all types or variants."),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.5.1",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.5 Flight Preparation"],
#                 constraints=[Constrain(
#                     text="The Operator shall have procedures that describe flight crew member duties and responsibilities forflight preparation and ensure flight crew members, prior to the commencement of each flight,complete a review of:",
#                     children=[
#                         Constrain(text="The Aircraft Technical Log (ATL) and the MEL/CDL"),
#                         Constrain(text="The OFP"),
#                         Constrain(text="Weather information to include en route and departure, destination and alternate airports"),
#                         Constrain(text="NOTAMS applicable to the en route phase of flight and to departure, destination and alternate airports"),
#                         Constrain(text="Aircraft performance"),
#                         Constrain(text="Aircraft weight/mass and balance"),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.5.2",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.5 Flight Preparation"],
#                 constraints=[Constrain(text="If the Operator uses aircraft with electronic navigation data capabilities, the Operator shall haveguidance and procedures for flight crew members to ensure the validity of any electronic navigationdatabase installed into aircraft navigation equipment.")],
#             ),
#             IOSAItem(
#                 code="FLT 3.5.3",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.5 Flight Preparation"],
#                 constraints=[Constrain(
#                     text="If the Operator uses electronic flight bag (EFB) devices or systems, the Operator shall, in accordancewith requirements of the Authority, have one or more processes to ensure the appropriatemanagement, control, maintenance and use of EFBs. Such process shall ensure, as a minimum:",
#                     children=[
#                         Constrain(text="Portable EFBs, if used, do not affect the performance of aircraft systems, equipment or the ability to operate the aircraft"),
#                         Constrain(text="Assessment of the safety risks associated with each EFB function used in operations in accordance with FLT 1.12.2"),
#                         Constrain(text="Establishment of procedures for the use, management and maintenance of the device, each EFB function and any database the device may use"),
#                         Constrain(text="Establishment of training requirements for the use of the device and each EFB function"),
#                         Constrain(text="In the event of an EFB failure, sufficient information is readily available to the flight crew for the flight to be conducted safely."),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.6.2",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.6 Route and Airport Planning"],
#                 constraints=[Constrain(
#                     text="The Operator shall have guidance that enables the flight crew to determine if airports of intended use meet operational requirements, to include:",
#                     children=[
#                         Constrain(text="Applicable performance requirements"),
#                         Constrain(text="Runway characteristics"),
#                         Constrain(text="Air Traffic Services and associated communications"),
#                         Constrain(text="Navigation aids and lighting"),
#                         Constrain(text="Weather reporting"),
#                         Constrain(text="Emergency services."),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.6.3",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.6 Route and Airport Planning"],
#                 constraints=[Constrain(text="The Operator shall have guidance that enables the flight crew to determine operating minima forairports of intended use.")],
#             ),
#             IOSAItem(
#                 code="FLT 3.6.4",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.6 Route and Airport Planning"],
#                 constraints=[Constrain(
#                     text="The Operator shall have guidance that enables the flight crew to determine Runway Visual Range(RVR) requirements for runways of intended use, to include, as a minimum:",
#                     children=[
#                         Constrain(text="Requirement for the availability of RVR reporting in order for CAT II and CAT III approach and landing operations to be authorized;"),
#                         Constrain(text="Required minimum RVR values for takeoff and authorized approaches"),
#                         Constrain(text="Required minimum RVR values that consider inoperative approach/runway lighting, inoperative transmissometers or inadequate visual reference."),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.6.5",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.6 Route and Airport Planning"],
#                 constraints=[Constrain(text="The Operator should have guidance that ensures approach and landing operations are notauthorized when the prevailing visibility is below 800 meters or the Converted MeteorologicalVisibility (CMV) is below 800 RVR unless RVR reporting is available for the runway of intendeduse.")],
#             ),
#             IOSAItem(
#                 code="FLT 3.6.5",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.6 Route and Airport Planning"],
#                 constraints=[Constrain(text="The Operator should have guidance that ensures approach and landing operations are notauthorized when the prevailing visibility is below 800 meters or the Converted MeteorologicalVisibility (CMV) is below 800 RVR unless RVR reporting is available for the runway of intendeduse.")],
#             ),
#             IOSAItem(
#                 code="FLT 3.7.1",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.7 Fuel, Weight/Mass and Balance, Flight Plans"],
#                 constraints=[Constrain(text="The Operator shall have a fuel policy and guidance that enables the flight crew to determine theminimum dispatch/departure fuel for each phase of flight in accordance with DSP 4.3.1.")],
#             ),
#             IOSAItem(
#                 code="FLT 3.7.2",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.7 Fuel, Weight/Mass and Balance, Flight Plans"],
#                 constraints=[Constrain(
#                     text="The Operator shall delegate the authority to the PIC to ensure:",
#                     children=[
#                         Constrain(text="A flight is not commenced unless the usable fuel required in accordance with DSP 4.3.1 ison board the aircraft and is sufficient to complete the planned flight safely"),
#                         Constrain(text="If fuel is consumed during a flight for purposes other than originally intended during pre-flightplanning, such flight is not continued without a re-analysis and, if applicable, adjustment ofthe planned operation to ensure sufficient fuel remains to complete the flight safely"),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.7.3",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.7 Fuel, Weight/Mass and Balance, Flight Plans"],
#                 constraints=[Constrain(
#                     text="The Operator shall have guidance that enables the flight crew to prepare and/or accept a load sheetwith accurate aircraft weight/mass and balance calculations for each flight. Such guidance shall:",
#                     children=[
#                         Constrain(text="Assign responsibility to the PIC for ensuring the load sheet content is satisfactory prior to each flight"),
#                         Constrain(text="Incorporate flight crew procedures for preparing or accepting last minute changes (LMC) tothe load sheet, to include guidance for the maximum allowable difference between plannedand actual weights"),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.7.5",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.7 Fuel, Weight/Mass and Balance, Flight Plans"],
#                 constraints=[Constrain(text="The Operator shall have a description of the Air Traffic Services (ATS) Flight Plan, as well asguidance and instructions for its use, that is accessible to the flight crew during flight preparation andin flight")],
#             ),
#             IOSAItem(
#                 code="FLT 3.7.6",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.7 Fuel, Weight/Mass and Balance, Flight Plans"],
#                 constraints=[Constrain(text="")],
#             ),
#             IOSAItem(
#                 code="FLT 3.7.7",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.7 Fuel, Weight/Mass and Balance, Flight Plans"],
#                 constraints=[Constrain(text="The Operator shall ensure the OFP or equivalent document is accepted and signed, using eithermanuscript or an approved electronic method, by the PIC during flight preparation")],
#             ),
#             IOSAItem(
#                 code="FLT 3.7.8",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.7 Fuel, Weight/Mass and Balance, Flight Plans"],
#                 constraints=[Constrain(text="The Operator shall have guidance that enables the flight crew to identify appropriate en route alternate airports.")],
#             ),
#             IOSAItem(
#                 code="FLT 3.7.9",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.7 Fuel, Weight/Mass and Balance, Flight Plans"],
#                 constraints=[Constrain(
#                     text="If the Operator conducts isolated airport operations, the Operator shall have guidance and instructions for the flight crew to:",
#                     children=[
#                         Constrain(text="Practically calculate or determine a point of safe return (PSR) for each flight into an isolated airport"),
#                         Constrain(text="Ensure the flight does not continue past the actual PSR unless a current assessment of meteorological conditions, traffic, and other operational conditions indicate that a safe landing can be made at the estimated time of use."),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.7.10",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.7 Fuel, Weight/Mass and Balance, Flight Plans"],
#                 constraints=[Constrain(
#                     text="The Operator should have guidance for use by the flight crew to increase fuel state awareness. Such guidance should include one or more of the following:",
#                     children=[
#                         Constrain(text="An approximate final reserve fuel value applicable to each aircraft type and variant in the Operator's fleet."),
#                         Constrain(text="A final reserve fuel value presented on the OFP for each flight."),
#                         Constrain(text="A display in the FMS of the planned or actual final reserve fuel for each flight."),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.8.1",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.8 Aircraft Preflight and Airworthiness"],
#                 constraints=[Constrain(
#                     text="The Operator shall have guidance and procedures that describe flight crew duties andresponsibilities for the use and/or application of the ATL, MEL and CDL. Such guidance andprocedures shall be included in the OM or in other documents that are available to the flight crewduring flight preparation and accessible to the flight crew during flight, and shall address, as aminimum, PIC responsibilities for:",
#                     children=[
#                         Constrain(text="Determining the airworthiness status of the aircraft"),
#                         Constrain(text="Ensuring, for each flight, a description of known or suspected defects that affect the operation of the aircraft is recorded in the ATL"),
#                         Constrain(text="Precluding a flight from departing until any defect affecting airworthiness is processed in accordance with the MEL/CDL"),
#                         Constrain(text="Ensuring the aircraft is operated in accordance with any applicable MEL/CDL Operational Procedure."),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.8.2",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.8 Aircraft Preflight and Airworthiness"],
#                 constraints=[Constrain(
#                     text="The Operator shall have guidance that is published in the OM or other document(s) and is available to the flight crew to ensure information entered in the ATL:",
#                     children=[
#                         Constrain(text="Is up to date"),
#                         Constrain(text="Legible;"),
#                         Constrain(text="Cannot be erased"),
#                         Constrain(text="Is correctable in the case of an error provided each correction is identifiable and errors remain legible"),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.8.3",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.8 Aircraft Preflight and Airworthiness"],
#                 constraints=[Constrain(text="The Operator shall assign the PIC the authority to reject an aircraft prior to departureof a flight if dissatisfied with any aspect of the airworthiness and/or maintenance status of theaircraft.")],
#             ),
#             IOSAItem(
#                 code="FLT 3.8.6A",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.8 Aircraft Preflight and Airworthiness"],
#                 constraints=[Constrain(
#                     text="The Operator shall ensure, prior to each flight, the satisfactory accomplishment of an exterior aircraft inspection (walkaround). This inspection shall be:",
#                     children=[
#                         Constrain(text="Performed by a member of the flight crew, or"),
#                         Constrain(text="Delegated to a licensed aircraft maintenance technician, or"),
#                         Constrain(text="Delegated to another individual qualified in accordance with FLT 2.2.25."),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.8.6B",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.8 Aircraft Preflight and Airworthiness"],
#                 constraints=[Constrain(text="If the Operator delegates the accomplishment of the exterior aircraft inspection (walkaround) toqualified individuals as specified in FLT 3.8.6A (iii), the Operator shall ensure such delegation wassubjected to safety risk assessment and mitigation performed in accordance with SMS principles asspecified in FLT 1.12.2.")],
#             ),
#             IOSAItem(
#                 code="FLT 3.8.7A",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.8 Aircraft Preflight and Airworthiness"],
#                 constraints=[Constrain(
#                     text="The Operator shall have guidance, published in the OM or other document(s) available to the flightcrew during flight preparation, that requires an exterior aircraft inspection (walk-around) that focuseson safety-critical areas of the aircraft and ensures, as a minimum:",
#                     children=[
#                         Constrain(text="Pitot and static ports are not damaged or obstructed"),
#                         Constrain(text="Flight controls are not locked or disabled (as applicable, depending on aircraft type)"),
#                         Constrain(text="Frost, snow or ice is not present on critical surfaces"),
#                         Constrain(text="Aircraft structure or structural components are not damaged"),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.8.7B",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.8 Aircraft Preflight and Airworthiness"],
#                 constraints=[Constrain(
#                     text="The Operator shall have a procedure to ensure the availability, accessibility and serviceability ofaircraft flight deck systems and emergency equipment. Such procedure shall include an interiorpreflight inspection of systems and equipment, which, as a minimum, is conducted by the flight crewprior to the first flight:",
#                     children=[
#                         Constrain(text="Of the flight crew on an aircraft during a duty period"),
#                         Constrain(text="On an aircraft after it has been left unattended by the flight crew, unless the Operator has a process or a procedure that ensures flight deck systems and emergency equipment remain undisturbed."),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.8.8",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.8 Aircraft Preflight and Airworthiness"],
#                 constraints=[Constrain(
#                     text="If the Operator conducts passenger flights or transports supernumeraries in the passenger cabin withor without cabin crew, the Operator shall have a procedure to ensure the availability, accessibility andserviceability of aircraft cabin emergency systems and equipment. Such procedure shall include apreflight inspection of such systems and equipment, which, as a minimum, shall be conducted by theflight crew or, if applicable, delegated to the cabin crew prior to the first flight:",
#                     children=[
#                         Constrain(text="After a new cabin crew or, if no cabin crew is used, a new flight crew has assumed control of the aircraft cabin"),
#                         Constrain(text="After an aircraft has been left unattended by a flight crew or cabin crew unless the Operator has a process or procedure that ensures aircraft cabin emergency systems and equipment remain undisturbed"),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.8.9",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.8 Aircraft Preflight and Airworthiness"],
#                 constraints=[Constrain(text="If the flight crew is required to conduct a preflight interior inspection of the cargo compartment and/orsupernumerary compartment on cargo aircraft, or the passenger cabin of an aircraft being used totransport cargo without passengers, the Operator shall have guidance, published in the OM or otherdocument available to the flight crew during the flight preparation, for the conduct of such inspectionto ensure the availability, accessibility and serviceability of restraint systems and emergencyequipment.")],
#             ),
#             IOSAItem(
#                 code="FLT 3.8.10",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.8 Aircraft Preflight and Airworthiness"],
#                 constraints=[Constrain(
#                     text="If the Operator transports passengers and/or supernumeraries without cabin crew, the Operator shallhave procedures to ensure, prior to departure of a flight, passengers and/or supernumeraries, asapplicable, have been briefed and are familiar with the location and use of safety equipment, toinclude:",
#                     children=[
#                         Constrain(text="Seat belts"),
#                         Constrain(text="Emergency exits"),
#                         Constrain(text="Life jackets (individual flotation devices), if required"),
#                         Constrain(text="Lifesaving rafts, if required"),
#                         Constrain(text="Oxygen masks"),
#                         Constrain(text="Emergency equipment for collective use"),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.9.1",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.9 Ground Handling"],
#                 constraints=[Constrain(
#                     text="If the Operator conducts passenger flights without cabin crew, the Operator shall have a procedure toensure verification that:",
#                     children=[
#                         Constrain(text="Passenger and crew baggage in the passenger cabin is securely stowed"),
#                         Constrain(text="If applicable, cargo packages and/or passenger items being transported in passenger seats are properly secured"),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.9.2",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.9 Ground Handling"],
#                 constraints=[Constrain(
#                     text="If the Operator conducts passenger flights without cabin crew, the Operator shall have a processand/or procedures to ensure a coordinated and expeditious cabin evacuation during aircraft fuelingoperations with passengers embarking, on board or disembarking. Such procedures shall require:",
#                     children=[
#                         Constrain(text="Cabin exits are designated for rapid deplaning or emergency evacuation, and routes to such exits are unobstructed"),
#                         Constrain(text="The area outside designated emergency evacuation exits is unobstructed"),
#                         Constrain(text="Qualified persons trained in emergency procedures are positioned near aircraft boardingdoor(s) or are otherwise in a position to monitor passenger safety and, if required, execute acabin evacuation"),
#                         Constrain(text="A suitable method of communication is established between qualified persons in aposition to monitor passenger safety and personnel that have responsibility for fuelingoperations."),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.9.3",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.9 Ground Handling"],
#                 constraints=[Constrain(
#                     text="If the Operator conducts passenger flights without cabin crew and transports passengers that requirespecial handling, the Operator shall have a policy and procedures for the acceptance or non-acceptance, as well as onboard handling, of such passengers by the flight crew. The policy andprocedures shall be in accordance with applicable regulations and as a minimum address, asapplicable:",
#                     children=[
#                         Constrain(text="Intoxicated and/or unruly passengers"),
#                         Constrain(text="Passengers with disabilities or reduced mobility"),
#                         Constrain(text="Passengers with injuries or illness"),
#                         Constrain(text="Infants and unaccompanied children"),
#                         Constrain(text="Inadmissible passengers"),
#                         Constrain(text="Deportees"),
#                         Constrain(text="Passengers in custody"),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.9.4",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.9 Ground Handling"],
#                 constraints=[Constrain(text="If the carriage of weapons on board an aircraft is approved as specified in SEC 3.3.1, the Operatorshall have a procedure to ensure the PIC is notified prior to the departure of a flight. Such notificationshall include the number and seat locations of authorized armed persons on board the aircraft.")],
#             ),
#             IOSAItem(
#                 code="FLT 3.9.6",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.9 Ground Handling"],
#                 constraints=[Constrain(
#                     text="If the Operator conducts flights from any airport when conditions are conducive to ground aircrafticing, the Operator shall have de-/anti-Icing policies and procedures published in the OM or in otherdocuments that are available to the flight crew during flight preparation and accessible to the flightcrew during flight. Such policies and procedures shall address any flight crew duties andresponsibilities related to de-/anti-Icing and include:",
#                     children=[
#                         Constrain(text="Holdover Time tables"),
#                         Constrain(text="A requirement for a member of the flight crew or qualified ground personnel to perform a visual check of the wings before takeoff, if any contamination is suspected"),
#                         Constrain(text="A requirement that takeoff will not commence unless the critical surfaces are clear of any deposits that might adversely affect the performance and/or controllability of the aircraft"),
#                         Constrain(text="A statement that delegates authority to the PIC to order De-/Anti-icing whenever deemed necessary."),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.9.7",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.9 Ground Handling"],
#                 constraints=[Constrain(
#                     text="If the Operator does not conduct flights from any airport when conditions are conducive to groundaircraft icing, the Operator shall have guidance published in the OM or other document that isavailable to the flight crew during flight preparation and accessible to the flight crew during flight.Such guidance shall include:",
#                     children=[
#                         Constrain(text="A description of meteorological and other conditions that are conducive to ground aircraft icing and/or the formation of ice on aircraft critical surfaces"),
#                         Constrain(text="A prohibition from operating an aircraft from any airport when conditions conducive to ground aircraft icing exist"),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.9.8",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.9 Ground Handling"],
#                 constraints=[Constrain(
#                     text="If the Operator transports dangerous goods, the Operator shall ensure information and guidance thatenable the flight crew to carry out duties and responsibilities related to the transport of dangerousgoods is published or referenced in the OM and included in the onboard library. Such guidance shallinclude, as a minimum:",
#                     children=[
#                         Constrain(text="General policies and procedures"),
#                         Constrain(text="Duties and responsibilities"),
#                         Constrain(text="As applicable, preflight acceptance requirements"),
#                         Constrain(text="Flight crew written notification requirements"),
#                         Constrain(text="Dangerous goods incident and/or emergency response procedures"),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.9.9",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.9 Ground Handling"],
#                 constraints=[Constrain(text="If the Operator does not transport dangerous goods as cargo, the Operator shall have guidance for the flight crew that includes procedures for response to dangerous goods incidents.")],
#             ),
#             IOSAItem(
#                 code="FLT 3.10.1",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.10 Airspace Rules"],
#                 constraints=[Constrain(text="The Operator shall require all commercial flights to be conducted under an IFR Flight Plan inaccordance with an IFR clearance and, if an instrument approach is required, in accordance with theapproach procedures approved or accepted by the state in which the airport of intended landing islocated.")],
#             ),
#             IOSAItem(
#                 code="FLT 3.10.2",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.10 Airspace Rules"],
#                 constraints=[Constrain(text="If the Operator is authorized to conduct certain portions of a commercial flight under VFR, theOperator shall have a policy and procedures that describe how an IFR clearance is to be obtained(departures) and/or cancelled (arrivals).")],
#             ),
#             IOSAItem(
#                 code="FLT 3.10.4",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.9 Ground Handling"],
#                 constraints=[Constrain(
#                     text="The Operator shall have guidance that addresses the use of standard radio phraseology whencommunicating with ATC, the acceptance and readback of ATC clearances and, when necessary,the clarification of such clearances to ensure understanding. Such guidance shall include, as a minimum:",
#                     children=[
#                         Constrain(text="A requirement for the use of the call sign"),
#                         Constrain(text="A requirement for at least two flight crew members to monitor and confirm clearances toensure a mutual (flight crew) understanding of accepted clearances under circumstances,as determined by the operator or flight crew, when a missed or misunderstood clearancecould pose a safety risk to the flight"),
#                         Constrain(text="A requirement to clarify clearances with ATC whenever any flight crew member is in doubt regarding the clearance or instruction received."),
#                     ],
#                 )],
#             ),
#             IOSAItem(
#                 code="FLT 3.10.6",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.10 Airspace Rules"],
#                 constraints=[Constrain(text="The Operator shall have procedures and/or limitations that address operations into and out ofuncontrolled airspace and/or airports, to include, if applicable, a prohibition if such operations are notpermitted in accordance with restrictions of the AOC or equivalent documents.")],
#             ),
#             IOSAItem(
#                 code="FLT 3.10.7",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.10 Airspace Rules"],
#                 constraints=[Constrain(text="The Operator shall have guidance that enables the flight crew to determine differences in rules andprocedures for any airspace of intended use, to include, as a minimum, an explanationof the differences between prevailing or local airspace rules and ICAO airspace rules, where applicable.")],
#             ),
#             IOSAItem(
#                 code="FLT 3.10.8",
#                 guidance="Refer to Guidance associated with ORG 1.5.3 located in ISM Section 1.",
#                 iosa_map=["3 Line Operations", "3.10 Airspace Rules"],
#                 constraints=[Constrain(text="If the Operator conducts operations in en route remote airspace for which Strategic Lateral OffsetProcedures (SLOP) are published in the relevant AIP, the Operator shall have guidance that enablesthe flight crew to implement SLOP when operating in such airspace.")],
#             ),
#         ],
#     ),
#     IOSASection(
#         name='Section 3 Operational Control and Flight Dispatch',
#         code='DSP',
#         applicability='addresses the requirements for operational control of flights conducted by multi-engine aircraft and is applicable to an operator that conducts such flights, whether operational control functions are conducted by the operator or conducted for the operator by an external organization (outsourced).',
#         guidance='For the purposes of this section authority is defined as the delegated power or right to command or direct, to make specific decisions, to grant permission and/or provide approval, or to control or modify a process.',
#         order=3,
#         items=[
#             IOSAItem(
#                 code='DSP 1.1.1',
#                 guidance='',
#                 iosa_map=['1 Management and Control', '1.1 Management System Overview'],
#                 constraints=[],
#             ),
#             IOSAItem(
#                 code='DSP 1.1.2',
#                 guidance='',
#                 iosa_map=['1 Management and Control', '1.1 Management System Overview'],
#                 constraints=[],
#             ),
#             IOSAItem(
#                 code='DSP 1.1.3',
#                 guidance='',
#                 iosa_map=['1 Management and Control', '1.1 Management System Overview'],
#                 constraints=[],
#             ),
#             IOSAItem(
#                 code='DSP 1.1.4',
#                 guidance='',
#                 iosa_map=['1 Management and Control', '1.1 Management System Overview'],
#                 constraints=[],
#             ),
#         ],
#     ),
# ]


# all_pages = pdf_man.extract(file.file)
# parsed_file = UnstructuredManual(
#     name=file.filename,
#     pages=all_pages,
# )
# db_service_response = await manuals_database_api.create_unstructured_manual(parsed_file)
# res.status_code = db_service_response.status_code
# if not db_service_response.success:
#     return JsonResponse(
#         success=db_service_response.success,
#         msg=db_service_response.msg,
#     )


# def test_parse_pdf_api_success():
#     # add manual
#     access_token = _test_config.login_user('cwael', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
#     api_url = f"{_test_config.get_api_url()}/manuals/parse-pdf"
#     http_headers = {'X-Auth': f"Bearer {access_token}"}
#     http_res = requests.post(api_url, headers=http_headers, files={'file': open('data/sample_manual.pdf', 'rb')})
#     assert http_res.status_code == 200
#     json_res_body = json.loads(http_res.content.decode())
#     assert json_res_body['success']
#     assert 'doc_uuid' in json_res_body['data']
#     assert 'file_id' in json_res_body['data']
#     assert 'url_path' in json_res_body['data']
#     doc_uuid = json_res_body['data']['doc_uuid']
#     url_path = json_res_body['data']['url_path']

#     # check file index
#     http_res = requests.get(f"{_test_config.get_file_server_url()}/{url_path}")
#     assert http_res.status_code == 200

#     # check manual exists
#     http_res = requests.post(api_url, headers=http_headers, files={'file': open('data/sample_manual.pdf', 'rb')})
#     assert http_res.status_code == 409
#     json_res_body = json.loads(http_res.content.decode())
#     assert (not json_res_body['success'] and json_res_body['msg'] == 'File Index Already Exists')

#     # delete manual
#     access_token = _test_config.login_user('eslam', 'CgJhxwieCc7QEyN3BB7pmvy9MMpseMPV')
#     http_headers = {'X-Auth': f"Bearer {access_token}"}
#     api_url = f"{_test_config.get_api_url()}/manuals/delete-manual"
#     http_res = requests.post(api_url, headers=http_headers, json={'doc_uuid': doc_uuid})
#     assert http_res.status_code == 200
#     json_res_body = json.loads(http_res.content.decode())
#     assert (json_res_body['success'] and json_res_body['msg'] == 'OK')

#     # check manual is deleted
#     http_res = requests.post(api_url, headers=http_headers, json={'doc_uuid': doc_uuid})
#     assert http_res.status_code == 404
#     json_res_body = json.loads(http_res.content.decode())
#     assert (not json_res_body['success'] and json_res_body['msg'] == 'File Index not Found')

# 3- Your output must be a valid json object.
#         4- Here is an example output object:
#         {{
#             "compliance_scores": {{
#                 "i": {{
#                     "score": number, // estimated compliance score percentage
#                     "explanation": string // explanation for this item estimated score
#                 }},
#                 "ii": {{
#                     // sub item "a" for item "ii" in ISARPs if exists
#                     "a": {{
#                         "score": number, // estimated compliance score percentage
#                         "explanation": string // explanation for this item estimated score
#                     }},
#                     // sub item "b" for item "ii" in ISARPs if exists
#                     "b": {{
#                         "score": number, // estimated compliance score percentage
#                         "explanation": string // explanation for this item estimated score
#                     }}
#                 }}
#             }},
#             "comments": string, // general explanation for these estimated scores
#             "suggestions": string // suggestions to improve compliance_scores
#         }}