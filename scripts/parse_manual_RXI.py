import re
import json
from glob import glob
from PyPDF2 import PdfReader
from faker import Faker
import string
from random import random
import numpy as np

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

def check_is_upper(parent):
    string1 = parent[:]

    point_string1 = string1.find(".") if string1.find(".") != -1 else 1e+10
    space_string1 = string1.find(" ") if string1.find(" ") != -1 else 1e+10

    cut_at_string1 = min(point_string1,space_string1)

    return string1[cut_at_string1:].strip().isupper() 


def check_if_logical_increment_in_parent(parent,new_parent):
    string1 = parent[:]
    string2 = new_parent[:]

    point_string1 = string1.find(".") if string1.find(".") != -1 else 1e+10
    point_string2 = string2.find(".") if string2.find(".") != -1 else 1e+10
    space_string1 = string1.find(" ") if string1.find(" ") != -1 else 1e+10
    space_string2 = string2.find(" ") if string2.find(" ") != -1 else 1e+10

    cut_at_string1 = min(point_string1,space_string1)
    cut_at_string2 = min(point_string2,space_string2)

    new_string1  = string1[:cut_at_string1]
    new_string2  = string2[:cut_at_string2]

    try:
        accept = int(new_string1) == (int(new_string2)-1)
        return accept
    except:
        return False
    
def starts_with_matching_substring(string1, string2):
    parent = string1[:]
    child = string2[:]
    parent = re.sub(r"[^0-9\.]","",parent)
    child = re.sub(r"[^0-9\.]","",child)
    parent_parts = parent.split('.')
    child_parts = child.split('.')

    # Check if the child has more parts than the parent
    if len(child_parts) <= len(parent_parts):
        return False
    
    # Check if the parent is a prefix of the child
    for i in range(len(parent_parts)):
        if parent_parts[i] != child_parts[i]:
            return False
    
    return True

def filter_children(parent, children):

    return [
            child for child in children if starts_with_matching_substring(parent.strip(),child['label'].strip())
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

        for idx,i in enumerate(data[chapter]["toc_info"]):
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
                if not check_is_upper(i[0]):
                    continue
                if temp_sub1_section.get("label") != None:
                    if(idx+4 < len(data[chapter]["toc_info"])):
                        child_1 = starts_with_matching_substring(i[0].strip(),data[chapter]["toc_info"][idx+1][0].strip())
                        child_2 = starts_with_matching_substring(i[0].strip(),data[chapter]["toc_info"][idx+2][0].strip())
                        child_3 = starts_with_matching_substring(i[0].strip(),data[chapter]["toc_info"][idx+3][0].strip())
                        child_4 = starts_with_matching_substring(i[0].strip(),data[chapter]["toc_info"][idx+4][0].strip())
                        if not (child_1 or child_2 or child_3 or child_4):
                            continue
                    if not check_if_logical_increment_in_parent( temp_sub1_section["label"],i[0]):
                        continue
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

def create_parts_metadata_file(file_path):
    metadata = []
    water_marks= ["DRAFT"]
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

            if (y > 51) and (y < 719) and (text not in water_marks):
                parts.append(text)

        page.extract_text(visitor_text=visitor_body)
        text_body = clean("".join(parts))

        all_pages.append(["\n" + text_body + "\n", page_number])
        page_number += 1

    
    for i in all_pages:
        for g in re.finditer(
            r"( *)(\d+)( *)((( *)\.( *)(\d+)( *))*)( +)((([^0-9\s])| )+)( *)", i[0]
        ):
            
            if share_common_chars(string.ascii_letters, g.group().strip()) and ("..." not in g.group()):

                metadata.append([g.group().strip(), i[1]])

    return rearrange_manual_content_tree([
                    {
                        "filename": file_path,
                        "toc_info": metadata,
                    }
                ],str(int(random()*10000)))[0]['toc_info']
