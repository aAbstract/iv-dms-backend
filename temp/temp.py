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
# db.manuals.insert_one(seed_manual.dict())
