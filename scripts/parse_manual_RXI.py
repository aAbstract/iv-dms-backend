import re
import json
from glob import glob
from PyPDF2 import PdfReader
from faker import Faker
import string



def clean(text):
    new_text= text[:]
    replacements = {
        "\u201d": "'",
        "\u201c": "'",
        "\u2019": "'",
        "\u2013": "-",
        "\u2026": "...",
        "\u2014": "--",
        "\u2018": "'",
        "\u201a": "'",
        "\u201e": "'",
        "\u200b": "",
        "\u00a0": " ",
        "\u00ae": "(R)",
        "\u2122": "(TM)",
        "\u00e9": "e",
        "\u00e2": "a",
        "\u00ae": "(R)",
        "\u2010": "-",
        "\u2011": "-",
        "\u2012": "-",
        "\u2013": "-",
        "\u2014": "--",
        "\u2015": "--",
        "\u2016": "|",
        "\u2017": "_",
        "\u2018": "'",
        "\u2019": "'",
        "\u201a": ",",
        "\u201b": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u201e": '"',
        "\u201f": '"',
        "\u2020": "*",
        "\u2021": "*",
        "\u2022": "*",
        "\u2023": "*",
        "\u2024": ".",
        "\u2025": "..",
        "\u2026": "...",
        "\u2027": ".",
        "\u2030": "%",
        "\u2031": "‰",
        "\u2032": "'",
        "\u2033": "''",
        "\u2034": "'''",
        "\u2035": "'",
        "\u2036": "''",
        "\u2037": "'''",
        "\u2038": "^",
        "\u2039": "<",
        "\u203a": ">",
        "\u203b": "*",
        "\u203c": "!!",
        "\u203d": "?",
        "\u203e": "-",
        "\u203f": "_",
        "\u2040": "-",
        "\u2041": "^",
        "\u2042": "*",
        "\u2043": "-",
        "\u2044": "/",
        "\u2045": "[",
        "\u2046": "]",
        "\u2047": "??",
        "\u2048": "?!",
        "\u2049": "!?",
        "\u204a": "-",
        "\u204b": "-",
        "\u204c": "-",
        "\u204d": "-",
        "\u204e": "*",
        "\u204f": "_",
        "\u2050": "-",
        "\u2051": "-",
        "\u2052": "%",
        "\u2053": "~",
        "\u2054": "-",
        "\u2055": "*",
        "\u2056": "^",
        "\u2057": "*",
        "\u2058": "^",
        "\u2059": "^",
        "\u205a": "-",
        "\u205b": "-",
        "\u205c": "-",
        "\u205d": "-",
        "\u205e": "-",
        "\u205f": " ",
        "\u2060": " ",
        "\u2061": " ",
        "\u2062": " ",
        "\u2063": " ",
        "\u2064": " ",
        "\u2065": " ",
        "\u2066": " ",
        "\u2067": " ",
        "\u2068": " ",
        "\u2069": " ",
        "\u206a": " ",
        "\u206b": " ",
        "\u206c": " ",
        "\u206d": " ",
        "\u206e": " ",
        "\u206f": " ",
        "\ufeff": "",
        "\u3000": " ",
        "\u200b": "",
        "\u200c": "",
        "\u200d": "",
        "\u200e": "",
        "\u200f": "",
        "\u202a": "",
        "\u202b": "",
        "\u202c": "",
        "\u202d": "",
        "\u202e": "",
        "\u2060": "",
        "\u2061": "",
        "\u2062": "",
        "\u2063": "",
        "\u2064": "",
        "\u2066": "",
        "\u2067": "",
        "\u2068": "",
        "\u2069": "",
        "\u206a": "",
        "\u206b": "",
        "\u206c": "",
        "\u206d": "",
        "\u206e": "",
        "\u206f": ""
    }
    for escape, replacement in replacements.items():
        text = text.replace(escape, replacement)

    return new_text


def starts_with_matching_substring(string1, string2):

    for i in range(len(string2)):
        for j in range(i+1, len(string2)+1):
            substring = string2[i:j]

            if string1.startswith(substring):
                return True
    return False

def filter_children(parent, children):
    return [
            child for child in children if starts_with_matching_substring(child['label'].strip(), parent)
        ]

  
def rearrange_manual_content_tree(metadata,code):
    Faker.seed(0)
    fake = Faker("en_US")

    def generate_random_hash():
        concatid = code
        return concatid + str(fake.unique.random_int(min=111111111111, max=999999999999))

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

    data = metadata
    for chapter in range(len(data)):
        if chapter != 0:

            if temp_sub4_section.get("label") != None:

                if len(all_sub5_section) > 0:
                    temp_sub4_section["pages"].append(get_max(all_sub5_section))

                temp_sub4_section["children"] = filter_children(temp_sub4_section['label'],all_sub5_section[:])
                all_sub4_section.append(dict(temp_sub4_section))
                temp_sub4_section = {"children": [], "pages": []}
                all_sub5_section = []

            if temp_sub3_section.get("label") != None:

                if len(all_sub4_section) > 0:
                    temp_sub3_section["pages"].append(get_max(all_sub4_section))

                temp_sub3_section["children"] = filter_children(temp_sub3_section['label'],all_sub4_section[:])
                all_sub3_section.append(dict(temp_sub3_section))
                temp_sub3_section = {"children": [], "pages": []}
                all_sub4_section = []

            if temp_sub2_section.get("label") != None:

                if len(all_sub3_section) > 0:
                    temp_sub2_section["pages"].append(get_max(all_sub3_section))

                temp_sub2_section["children"] = filter_children(temp_sub2_section['label'],all_sub3_section[:])
                all_sub2_section.append(dict(temp_sub2_section))
                temp_sub2_section = {"children": [], "pages": []}
                all_sub3_section = []

            if temp_sub1_section.get("label") != None:

                if len(all_sub2_section) > 0:
                    temp_sub1_section["pages"].append(get_max(all_sub2_section))

                temp_sub1_section["children"] = filter_children(temp_sub1_section['label'],all_sub2_section[:])
                all_sub1_sections.append(dict(temp_sub1_section))
                temp_sub1_section = {"children": [], "pages": []}
                all_sub2_section = []

            temp_chapter["toc_info"] = all_sub1_sections[:]
            all_chapters.append(dict(temp_chapter))
            temp_chapter = {}
            all_sub1_sections = []

        temp_chapter = dict(data[chapter])

        # current_offset = temp_chapter['start_page']

        for i in data[chapter]["toc_info"]:
            i[0] = i[0].strip()

            # 1.1.1.1.1
            if re.compile(
                r"(\d+)( *)\.( *)(\d+)( *)\.( *)(\d+)( *)\.( *)(\d+)( *)\.( *)(\d+)( *)((.| )+)"
            ).fullmatch(i[0]):

                all_sub5_section.append(
                    {
                        "label": i[0],
                        "pages": [i[1]],
                        "key": generate_random_hash(),
                    }
                )

            # 1.1.1.1
            elif re.compile(
                r"( *)(\d+)( *)\.( *)(\d+)( *)\.( *)(\d+)( *)\.( *)(\d+)( *)((.| )+)"
            ).fullmatch(i[0]):

                if temp_sub4_section.get("label") != None:

                    if len(all_sub5_section) > 0:
                        temp_sub4_section["pages"].append(get_max(all_sub5_section))

                    temp_sub4_section["children"] = filter_children(temp_sub4_section['label'],all_sub5_section[:])
                    all_sub4_section.append(dict(temp_sub4_section))
                    temp_sub4_section = {"children": [], "pages": []}
                    all_sub5_section = []

                # current level
                temp_sub4_section["label"] = i[0]
                temp_sub4_section["pages"].append(i[1])
                temp_sub4_section["key"] = generate_random_hash()

            # 1.1.1
            elif re.compile(
                r"( *)(\d+)( *)\.( *)(\d+)( *)\.( *)(\d+)( *)((.| )+)"
            ).fullmatch(i[0]):

                if temp_sub4_section.get("label") != None:

                    if len(all_sub5_section) > 0:
                        temp_sub4_section["pages"].append(get_max(all_sub5_section))

                    temp_sub4_section["children"] = filter_children(temp_sub4_section['label'],all_sub5_section[:])
                    all_sub4_section.append(dict(temp_sub4_section))
                    temp_sub4_section = {"children": [], "pages": []}
                    all_sub5_section = []

                if temp_sub3_section.get("label") != None:

                    if len(all_sub4_section) > 0:
                        temp_sub3_section["pages"].append(get_max(all_sub4_section))

                    temp_sub3_section["children"] = filter_children(temp_sub3_section['label'],all_sub4_section[:])
                    all_sub3_section.append(dict(temp_sub3_section))
                    temp_sub3_section = {"children": [], "pages": []}
                    all_sub4_section = []

                # current level
                temp_sub3_section["label"] = i[0]
                temp_sub3_section["pages"].append(i[1])
                temp_sub3_section["key"] = generate_random_hash()

            # 1.1
            elif re.compile(r"( *)(\d+)( *)\.( *)(\d+)( *)((.| )+)").fullmatch(
                i[0]
            ):

                if temp_sub4_section.get("label") != None:

                    if len(all_sub5_section) > 0:
                        temp_sub4_section["pages"].append(get_max(all_sub5_section))

                    temp_sub4_section["children"] = filter_children(temp_sub4_section['label'],all_sub5_section[:])
                    all_sub4_section.append(dict(temp_sub4_section))
                    temp_sub4_section = {"children": [], "pages": []}
                    all_sub5_section = []

                if temp_sub3_section.get("label") != None:

                    if len(all_sub4_section) > 0:
                        temp_sub3_section["pages"].append(get_max(all_sub4_section))

                    temp_sub3_section["children"] = filter_children(temp_sub3_section['label'],all_sub4_section[:])
                    all_sub3_section.append(dict(temp_sub3_section))
                    temp_sub3_section = {"children": [], "pages": []}
                    all_sub4_section = []

                if temp_sub2_section.get("label") != None:

                    if len(all_sub3_section) > 0:
                        temp_sub2_section["pages"].append(get_max(all_sub3_section))

                    temp_sub2_section["children"] = filter_children(temp_sub2_section['label'],all_sub3_section[:])
                    all_sub2_section.append(dict(temp_sub2_section))
                    temp_sub2_section = {"children": [], "pages": []}
                    all_sub3_section = []
                # current level
                temp_sub2_section["label"] = i[0]
                temp_sub2_section["pages"].append(i[1])
                temp_sub2_section["key"] = generate_random_hash()

            # 1
            elif re.compile(r"( *)\d+( *)((.| )+)").fullmatch(i[0]):

                if temp_sub4_section.get("label") != None:

                    if len(all_sub5_section) > 0:
                        temp_sub4_section["pages"].append(get_max(all_sub5_section))

                    temp_sub4_section["children"] = filter_children(temp_sub4_section['label'],all_sub5_section[:])
                    all_sub4_section.append(dict(temp_sub4_section))
                    temp_sub4_section = {"children": [], "pages": []}
                    all_sub5_section = []

                if temp_sub3_section.get("label") != None:

                    if len(all_sub4_section) > 0:
                        temp_sub3_section["pages"].append(get_max(all_sub4_section))

                    temp_sub3_section["children"] = filter_children(temp_sub3_section['label'],all_sub4_section[:])
                    all_sub3_section.append(dict(temp_sub3_section))
                    temp_sub3_section = {"children": [], "pages": []}
                    all_sub4_section = []

                if temp_sub2_section.get("label") != None:

                    if len(all_sub3_section) > 0:
                        temp_sub2_section["pages"].append(get_max(all_sub3_section))

                    temp_sub2_section["children"] = filter_children(temp_sub2_section['label'],all_sub3_section[:])
                    all_sub2_section.append(dict(temp_sub2_section))
                    temp_sub2_section = {"children": [], "pages": []}
                    all_sub3_section = []

                if temp_sub1_section.get("label") != None:

                    if len(all_sub2_section) > 0:
                        temp_sub1_section["pages"].append(get_max(all_sub2_section))

                    temp_sub1_section["children"] = filter_children(temp_sub1_section['label'],all_sub2_section[:])
                    all_sub1_sections.append(dict(temp_sub1_section))
                    temp_sub1_section = {"children": [], "pages": []}
                    all_sub2_section = []
                # current level
                temp_sub1_section["label"] = i[0]
                temp_sub1_section["pages"].append(i[1])
                temp_sub1_section["key"] = generate_random_hash()

            else:
                print("problem in manually parsing chapter")

    if temp_sub4_section.get("label") != None:

        if len(all_sub5_section) > 0:
            temp_sub4_section["pages"].append(get_max(all_sub5_section))
        temp_sub4_section["children"] = filter_children(temp_sub4_section['label'],all_sub5_section[:])
        all_sub4_section.append(dict(temp_sub4_section))
        temp_sub4_section = {"children": [], "pages": []}
        all_sub5_section = []

    if temp_sub3_section.get("label") != None:

        if len(all_sub4_section) > 0:
            temp_sub3_section["pages"].append(get_max(all_sub4_section))

        temp_sub3_section["children"] = filter_children(temp_sub3_section['label'],all_sub4_section[:])
        all_sub3_section.append(dict(temp_sub3_section))
        temp_sub3_section = {"children": [], "pages": []}
        all_sub4_section = []

    if temp_sub2_section.get("label") != None:

        if len(all_sub3_section) > 0:
            temp_sub2_section["pages"].append(get_max(all_sub3_section))

        temp_sub2_section["children"] = filter_children(temp_sub2_section['label'],all_sub3_section[:])
        all_sub2_section.append(dict(temp_sub2_section))
        temp_sub2_section = {"children": [], "pages": []}
        all_sub3_section = []

    if temp_sub1_section.get("label") != None:

        if len(all_sub2_section) > 0:
            temp_sub1_section["pages"].append(get_max(all_sub2_section))

        temp_sub1_section["children"] = filter_children(temp_sub1_section['label'],all_sub2_section[:])
        all_sub1_sections.append(dict(temp_sub1_section))
        temp_sub1_section = {"children": [], "pages": []}
        all_sub2_section = []

    temp_chapter["toc_info"] = all_sub1_sections[:]
    all_chapters.append(dict(temp_chapter))
    return all_chapters
    # with open(fr"data/RXI/{filename}_meta_data_tree.json", "w") as json_file:
    #     json.dump(all_chapters, json_file, indent=4)

def create_parts_metadata_file(file_path,code):
    metadata = []
    pdf_reader = PdfReader(file_path)
    all_pages = []
    page_number = 1

    for page in pdf_reader.pages:
        parts = []

        def share_common_chars(string1, string2):
            set1 = set(string1)
            set2 = set(string2)

            if set1.intersection(set2):
                return True
            else:
                return False

        def visitor_body(text, cm, tm, fontDict, fontSize):

            y = tm[5]

            if (y > 35) and (y < 720):
                parts.append(text)

        page.extract_text(visitor_text=visitor_body)
        text_body = clean("".join(parts))
        all_pages.append(["\n" + text_body + "\n", page_number])
        page_number += 1

    for i in all_pages:
        for g in re.finditer(
            r"(?<=(\n))( *)(\d+)( *)((( *)\.( *)(\d+)( *))*)( +)(([^0-9\s]| )+)", i[0]
        ):

            if share_common_chars(string.ascii_letters, g.group()):
                metadata.append([g.group(), i[1]])

    return rearrange_manual_content_tree([
                    {
                        "filename": file_path,
                        "toc_info": metadata,
                    }
                ],code)[0]['toc_info']
  