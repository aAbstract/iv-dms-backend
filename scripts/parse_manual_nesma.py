import re
import json
from glob import glob
from PyPDF2 import PdfReader
from faker import Faker


TOC_START_PAGE = 3
Faker.seed(0)
fake = Faker("en_US") 

def generate_random_hash():
    concatid = 'NE'
    return concatid + str(fake.unique.random_int(min=111111111111, max=999999999999))

def create_parts_metadata_file():
    metadata = []
    manual_parts = glob("data/nesma_OMA/*.pdf")
    for part_path in manual_parts:
        pdf_reader = PdfReader(part_path)
        part_toc_content = pdf_reader.pages[TOC_START_PAGE - 1].extract_text()
        chapter_title = re.findall(r"Chapter \d+ [A-Za-z ]+", part_toc_content)[
            0
        ].strip()
        metadata.append(
            {
                "filename": part_path,
                "chapter_title": chapter_title,
                "toc_pages": (TOC_START_PAGE, -1),
            }
        )

    with open("data/nesma_OMA/nesma_oma_metadata.json", "w") as f:
        f.write(json.dumps(metadata, indent=2))


def create_manual_toc_tree():
    def parse_toc_txt_to_tree(toc_text: str) -> list[tuple[str, str, int]]:
        lines = toc_text.split("\n")
        toc_epattern = f" {'.'*32} "
        toc_info = []
        for line in lines:
            if toc_epattern in line:
                section_code = line.split(" ")[0]
                if section_code == "Chapter":
                    continue
                if section_code == toc_epattern:
                    continue

                section_name = re.findall(f"\s[A-Za-z ]+\s+", line)
                if not section_name:
                    continue
                section_name = section_name[0].strip()

                page_number = re.findall(r"\s(\d+)", line)
                if page_number:
                    page_number = int(page_number[0])
                else:
                    page_number = -1

                toc_info.append((section_code, section_name, page_number))

        return toc_info

    f = open("data/nesma_OMA/nesma_oma_metadata.json", "r")
    json_str = f.read()
    f.close()

    json_obj = json.loads(json_str)
    for mde in json_obj:
        if not mde["include"]:
            continue
        toc_txt = ""
        pdf_reader = PdfReader(mde["filename"])
        for pidx in mde["toc_pages"]:
            toc_txt += pdf_reader.pages[pidx - 1].extract_text()
        toc_info = parse_toc_txt_to_tree(toc_txt)
        mde["toc_info"] = toc_info

    f = open("data/nesma_OMA/nesma_oma_metadata.json", "w")
    f.write(json.dumps(json_obj, indent=2))
    f.close()


def rearrange_manual_content_tree() -> list[object]:
    def get_max(obj_list):
        max_page = max(
            obj_list,
            key=lambda x: (
                x.get("pages")[0] if len(x.get("pages")) == 1 else x.get("pages")[1]
            ),
        )
        max_page = (
            max_page["pages"][0]
            if len(max_page["pages"]) == 1
            else max_page["pages"][1]
        )
        return max_page

    path_to_metadata = "data/nesma_OMA/nesma_oma_metadata.json"
    all_chapters = []
    all_sub1_sections = []
    all_sub2_section = []
    all_sub3_section = []
    all_sub4_section = []
    all_sub5_section = []

    temp_chapter = {}
    temp_sub1_section = {"children": [], "pages": []}
    temp_sub2_section = {"children": [], "pages": []}
    temp_sub3_section = {"children": [], "pages": []}
    temp_sub4_section = {"children": [], "pages": []}
    current_offset = 0
    with open(path_to_metadata, "r") as json_file:
        data = json.load(json_file)

    for chapter in range(len(data)):
        if chapter != 0:

            if temp_sub4_section.get("label") != None:

                if len(all_sub5_section) > 0:
                    temp_sub4_section["pages"].append(get_max(all_sub5_section))

                temp_sub4_section["children"] = all_sub5_section[:]
                all_sub4_section.append(dict(temp_sub4_section))
                temp_sub4_section = {"children": [], "pages": []}
                all_sub5_section = []

            if temp_sub3_section.get("label") != None:

                if len(all_sub4_section) > 0:
                    temp_sub3_section["pages"].append(get_max(all_sub4_section))

                temp_sub3_section["children"] = all_sub4_section[:]
                all_sub3_section.append(dict(temp_sub3_section))
                temp_sub3_section = {"children": [], "pages": []}
                all_sub4_section = []

            if temp_sub2_section.get("label") != None:

                if len(all_sub3_section) > 0:
                    temp_sub2_section["pages"].append(get_max(all_sub3_section))

                temp_sub2_section["children"] = all_sub3_section[:]
                all_sub2_section.append(dict(temp_sub2_section))
                temp_sub2_section = {"children": [], "pages": []}
                all_sub3_section = []

            if temp_sub1_section.get("label") != None:

                if len(all_sub2_section) > 0:
                    temp_sub1_section["pages"].append(get_max(all_sub2_section))

                temp_sub1_section["children"] = all_sub2_section[:]
                all_sub1_sections.append(dict(temp_sub1_section))
                temp_sub1_section = {"children": [], "pages": []}
                all_sub2_section = []

            temp_chapter["toc_info"] = all_sub1_sections[:]
            all_chapters.append(dict(temp_chapter))
            temp_chapter = {}
            all_sub1_sections = []

        temp_chapter = dict(data[chapter])
        current_offset = temp_chapter['start_page']

        for i in data[chapter]["toc_info"]:

            # 1.1.1.1.1.1
            if re.compile(
                r"(\d+)(\s*)\.(\s*)(\d+)(\s*)\.(\s*)(\d+)(\s*)\.(\s*)(\d+)(\s*)\.(\s*)(\d+)(\s*)\.(\s*)(\d+)(.*)"
            ).fullmatch(i[0]):
                all_sub5_section.append({"label": i[0].strip(), "pages": [i[1]+current_offset],"key":generate_random_hash()})

            # 1.1.1.1.1
            elif re.compile(
                r"(\d+)(\s*)\.(\s*)(\d+)(\s*)\.(\s*)(\d+)(\s*)\.(\s*)(\d+)(\s*)\.(\s*)(\d+)(.*)"
            ).fullmatch(i[0]):

                if temp_sub4_section.get("label") != None:

                    if len(all_sub5_section) > 0:
                        temp_sub4_section["pages"].append(get_max(all_sub5_section))

                    temp_sub4_section["children"] = all_sub5_section[:]
                    all_sub4_section.append(dict(temp_sub4_section))
                    temp_sub4_section = {"children": [], "pages": []}
                    all_sub5_section = []

                # current level
                temp_sub4_section["label"] = i[0].strip()
                temp_sub4_section["pages"].append(i[1]+current_offset)
                temp_sub4_section['key'] = generate_random_hash()

            # 1.1.1.1
            elif re.compile(
                r"(\d+)(\s*)\.(\s*)(\d+)(\s*)\.(\s*)(\d+)(\s*)\.(\s*)(\d+)(.*)"
            ).fullmatch(i[0]):

                if temp_sub4_section.get("label") != None:

                    if len(all_sub5_section) > 0:
                        temp_sub4_section["pages"].append(get_max(all_sub5_section))

                    temp_sub4_section["children"] = all_sub5_section[:]
                    all_sub4_section.append(dict(temp_sub4_section))
                    temp_sub4_section = {"children": [], "pages": []}
                    all_sub5_section = []

                if temp_sub3_section.get("label") != None:

                    if len(all_sub4_section) > 0:
                        temp_sub3_section["pages"].append(get_max(all_sub4_section))

                    temp_sub3_section["children"] = all_sub4_section[:]
                    all_sub3_section.append(dict(temp_sub3_section))
                    temp_sub3_section = {"children": [], "pages": []}
                    all_sub4_section = []

                # current level
                temp_sub3_section["label"] = i[0].strip()
                temp_sub3_section["pages"].append(i[1]+current_offset)
                temp_sub3_section['key'] = generate_random_hash()

            # 1.1.1
            elif re.compile(r"(\d+)(\s*)\.(\s*)(\d+)(\s*)\.(\s*)(\d+)(.*)").fullmatch(
                i[0]
            ):

                if temp_sub4_section.get("label") != None:

                    if len(all_sub5_section) > 0:
                        temp_sub4_section["pages"].append(get_max(all_sub5_section))

                    temp_sub4_section["children"] = all_sub5_section[:]
                    all_sub4_section.append(dict(temp_sub4_section))
                    temp_sub4_section = {"children": [], "pages": []}
                    all_sub5_section = []

                if temp_sub3_section.get("label") != None:

                    if len(all_sub4_section) > 0:
                        temp_sub3_section["pages"].append(get_max(all_sub4_section))

                    temp_sub3_section["children"] = all_sub4_section[:]
                    all_sub3_section.append(dict(temp_sub3_section))
                    temp_sub3_section = {"children": [], "pages": []}
                    all_sub4_section = []

                if temp_sub2_section.get("label") != None:

                    if len(all_sub3_section) > 0:
                        temp_sub2_section["pages"].append(get_max(all_sub3_section))

                    temp_sub2_section["children"] = all_sub3_section[:]
                    all_sub2_section.append(dict(temp_sub2_section))
                    temp_sub2_section = {"children": [], "pages": []}
                    all_sub3_section = []
                # current level
                temp_sub2_section["label"] = i[0].strip()
                temp_sub2_section["pages"].append(i[1]+current_offset)
                temp_sub2_section['key'] = generate_random_hash()

            # 1.1
            elif re.compile(r"(\d+)(\s*)\.(\s*)(\d+)(\s*)(.*)").fullmatch(i[0]):

                if temp_sub4_section.get("label") != None:

                    if len(all_sub5_section) > 0:
                        temp_sub4_section["pages"].append(get_max(all_sub5_section))

                    temp_sub4_section["children"] = all_sub5_section[:]
                    all_sub4_section.append(dict(temp_sub4_section))
                    temp_sub4_section = {"children": [], "pages": []}
                    all_sub5_section = []

                if temp_sub3_section.get("label") != None:

                    if len(all_sub4_section) > 0:
                        temp_sub3_section["pages"].append(get_max(all_sub4_section))

                    temp_sub3_section["children"] = all_sub4_section[:]
                    all_sub3_section.append(dict(temp_sub3_section))
                    temp_sub3_section = {"children": [], "pages": []}
                    all_sub4_section = []

                if temp_sub2_section.get("label") != None:

                    if len(all_sub3_section) > 0:
                        temp_sub2_section["pages"].append(get_max(all_sub3_section))

                    temp_sub2_section["children"] = all_sub3_section[:]
                    all_sub2_section.append(dict(temp_sub2_section))
                    temp_sub2_section = {"children": [], "pages": []}
                    all_sub3_section = []

                if temp_sub1_section.get("label") != None:

                    if len(all_sub2_section) > 0:
                        temp_sub1_section["pages"].append(get_max(all_sub2_section))

                    temp_sub1_section["children"] = all_sub2_section[:]
                    all_sub1_sections.append(dict(temp_sub1_section))
                    temp_sub1_section = {"children": [], "pages": []}
                    all_sub2_section = []
                # current level
                temp_sub1_section["label"] = i[0].strip()
                temp_sub1_section["pages"].append(i[1]+current_offset)
                temp_sub1_section['key'] = generate_random_hash()
                
            else:
                print("problem in manually parsing chapter")


    if temp_sub4_section.get("label") != None:

        if len(all_sub5_section) > 0:
            temp_sub4_section["pages"].append(get_max(all_sub5_section))

        temp_sub4_section["children"] = all_sub5_section[:]
        all_sub4_section.append(dict(temp_sub4_section))
        temp_sub4_section = {"children": [], "pages": []}
        all_sub5_section = []

    if temp_sub3_section.get("label") != None:

        if len(all_sub4_section) > 0:
            temp_sub3_section["pages"].append(get_max(all_sub4_section))

        temp_sub3_section["children"] = all_sub4_section[:]
        all_sub3_section.append(dict(temp_sub3_section))
        temp_sub3_section = {"children": [], "pages": []}
        all_sub4_section = []

    if temp_sub2_section.get("label") != None:

        if len(all_sub3_section) > 0:
            temp_sub2_section["pages"].append(get_max(all_sub3_section))

        temp_sub2_section["children"] = all_sub3_section[:]
        all_sub2_section.append(dict(temp_sub2_section))
        temp_sub2_section = {"children": [], "pages": []}
        all_sub3_section = []

    if temp_sub1_section.get("label") != None:

        if len(all_sub2_section) > 0:
            temp_sub1_section["pages"].append(get_max(all_sub2_section))

        temp_sub1_section["children"] = all_sub2_section[:]
        all_sub1_sections.append(dict(temp_sub1_section))
        temp_sub1_section = {"children": [], "pages": []}
        all_sub2_section = []

    temp_chapter["toc_info"] = all_sub1_sections[:]
    all_chapters.append(dict(temp_chapter))

    with open("data/nesma_OMA/nesma_oma_metadata_tree.json", "w") as json_file:
        json.dump(all_chapters, json_file, indent=4)


def create_manual_content_tree() -> list[tuple[str, int]]:
    f = open("data/nesma_OMA/nesma_oma_metadata.json", "r")
    json_str = f.read()
    f.close()
    json_obj = json.loads(json_str)
    for mde in json_obj:
        if not mde["include"]:
            continue

        toc_info = []
        pdf_reader = PdfReader(mde["filename"])
        for pidx, page in enumerate(pdf_reader.pages):
            page_content = page.extract_text()
            toc_epattern = f" {'.'*32} "
            if toc_epattern in page_content:
                continue

            chapter_number = mde["chapter_title"].split(" ")[1]
            page_lines = page_content.split("\n")
            for line in page_lines:
                reps = "{1,2}"
                if re.findall(rf"^({chapter_number}(?:\.\d{reps})+)", line):
                    toc_info.append((line, pidx + 1))
        mde["toc_info"] = toc_info

    f = open("data/nesma_OMA/nesma_oma_metadata.json", "w")
    f.write(json.dumps(json_obj, indent=2))
    f.close()


# create_manual_content_tree()
# create_parts_metadata_file()
# create_manual_toc_tree()
# create_manual_content_tree()
# rearrange_manual_content_tree()
