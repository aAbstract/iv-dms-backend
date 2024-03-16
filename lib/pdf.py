import string
import unicodedata
from PyPDF2 import PdfReader
import re
from faker import Faker
from random import random
import numpy as np


def convert_to_markdown(text):
    def replace_listing(match):
        listing_type = match.group(1)

        if listing_type.lower() in [
            "i",
            "ii",
            "iii",
            "iv",
            "v",
            "vi",
            "vii",
            "viii",
            "ix",
            "x",
            "xi",
            "xii",
            "xiii",
            "xiv",
            "xv",
            "xvi",
            "xvii",
            "xviii",
            "xix",
            "xx",
            "xxi",
            "xxii",
            "xxiii",
            "xxiv",
            "xxv",
            "xxvi",
            "xxvii",
            "xxviii",
            "xxix",
            "xxx",
        ]:
            return f"\n- ({listing_type.lower()})"
        elif listing_type.lower() in [
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
            "j",
            "k",
            "l",
            "m",
            "n",
            "o",
            "p",
            "q",
            "r",
            "s",
            "t",
            "u",
            "v",
            "w",
            "x",
            "y",
            "z",
        ]:
            return f"\n  - ({listing_type.lower()})"
        else:
            return f"({listing_type})"
        
    markdown_text = re.sub(r'(?<=\w)\n(?=\w)', " ", text)
    markdown_text = re.sub(r"\n\((\w+)\)", replace_listing, markdown_text)
    return markdown_text

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

def extract(path):
    all_pages = []
    reader = PdfReader(path)
    pages = reader.pages

    for i in pages:
        parts = []

        def visitor_body(text, cm, tm, fontDict, fontSize):
            # crop the header and footer
            y = tm[5]

            if (y > 40) and (y < 742):
                parts.append(text)

        i.extract_text(visitor_text=visitor_body)
        text_body = "".join(parts)
        all_pages.append(clean(text_body))

    return all_pages

def check_type(text1):
    text = text1[:].strip()
    romans = "ii|iii|iv|v|vi|vii|viii|ix|x|xi|xii|xiii|xiv|xv|xvi|xvii|xviii|xix|xx|xxi|xxii|xxiii|xxiv|xxv|xxvi|xxvii|xxviii|xxix|xxx"
    alphas = "abcdefghijklmnopqrstuvwxyz"
    
    if text[2] == "(":
        second_brak = text[:].find(")")
        if second_brak == -1:
            return "t"
        sub = text[3:second_brak]
        if sub == "i":
            return "i"
        elif sub == "h":
            return "h"
        elif sub == "ii":
            return "ii"
        elif sub == "j":
            return "j"
        elif sub in romans:
            return "r"
        elif sub in alphas:
            return "a"
        else:
            return "t"
    else:
        return "t"

def parse_paragraph(paragraph):
    text = paragraph[:]
    splitter = r"\.\n|:\n|;\n| or\n"
    items = re.split(splitter, text)
    items = [i.strip() for i in items if i]

    items_labled = []
    last = None
    i = None
    for i in range(len(items) - 1):
        item_type_here = check_type(items[i])
        item_type_front = check_type(items[i + 1])
        # print(item_type_here)
        if item_type_here == "i":
            if last == "h" and item_type_front == "i":
                items_labled.append([items[i], "a"])
            elif last == "h" and item_type_front == "ii":
                items_labled.append([items[i], "r"])
            elif last == "h" and item_type_front == "j":
                items_labled.append([items[i], "a"])
            elif last == "h" and item_type_front == "t":
                items_labled.append([items[i], "a"])
            elif last == "t" or last == None or last == "a" or last == "r":
                items_labled.append([items[i], "r"])
        elif item_type_here == "h":
            items_labled.append([items[i], "a"])
        elif item_type_here == "ii":
            items_labled.append([items[i], "r"])
        elif item_type_here == "j":
            items_labled.append([items[i], "a"])
        elif item_type_here == "r":
            items_labled.append([items[i], "r"])
        elif item_type_here == "a":
            items_labled.append([items[i], "a"])
        elif item_type_here == "t":
            items_labled.append([items[i], "t"])
        else:
            items_labled.append([items[i], "t"])
        last = item_type_here

    if i == None:
        i = -1
    item_type_here = check_type(items[i + 1])
    if item_type_here == "i":
        if last == "h":
            items_labled.append([items[i + 1], "a"])
        elif last == "j":
            items_labled.append([items[i + 1], "r"])
        elif last == "ii":
            items_labled.append([items[i + 1], "a"])
        elif last == "t" or last == None or last == "a" or last == "r":
            items_labled.append([items[i + 1], "r"])
    elif item_type_here == "h":
        items_labled.append([items[i + 1], "a"])
    elif item_type_here == "ii":
        items_labled.append([items[i + 1], "r"])
    elif item_type_here == "j":
        items_labled.append([items[i + 1], "a"])
    elif item_type_here == "r":
        items_labled.append([items[i + 1], "r"])
    elif item_type_here == "a":
        items_labled.append([items[i + 1], "a"])
    elif item_type_here == "t":
        items_labled.append([items[i + 1], "t"])
    else:
        items_labled.append([items[i + 1], "t"])

    constraints = []
    try:
        for i in range(len(items_labled)):
            if items_labled[i][1] == "t":
                constraints.append(
                    {"text": items_labled[i][0].strip("\n").strip(), "children": []}
                )
            elif items_labled[i][1] == "r":
                constraints[-1]["children"].append(
                    {"text": items_labled[i][0].strip("\n").strip(), "children": []}
                )
            elif items_labled[i][1] == "a":
                constraints[-1]["children"][-1]["children"].append(
                    {"text": items_labled[i][0].strip("\n").strip(), "children": []}
                )
    except:
        constraints = []
        for i in range(len(items_labled)):
            constraints.append({"text": items_labled[i][0].strip("\n").strip(), "children": []})
    return constraints

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
def get_header_footer(file_path):
    pdf_reader = PdfReader(file_path)

    headers = []
    footers = []
    for page in pdf_reader.pages:
        parts = []

        def visitor_body(text, cm, tm, fontDict, fontSize):

            y = tm[5]
            parts.append(y)

        page.extract_text(visitor_text=visitor_body)
       
        if parts !=[]:
            headers.append(np.percentile(parts, 87))
            footers.append(np.percentile(parts,34))

    header= sum(headers)/ len(headers)
    footer  = sum(footers)/ len(footers)
    return header, footer

def create_parts_metadata_file(file_path):
    metadata = []
    water_marks= ["DRAFT"]
    pdf_reader = PdfReader(file_path)
    all_pages = []
    page_number = 1
    header , footer = get_header_footer(file_path)

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

            if (y > footer) and (y < header) and (text not in water_marks):
                parts.append(text)

        page.extract_text(visitor_text=visitor_body)
        text_body = clean("".join(parts))

        all_pages.append(["\n" + text_body + "\n", page_number])
        page_number += 1

    
    for i in all_pages:
        for g in re.finditer(
            r"(?<=(\n))( *)(\d+)( *)((( *)\.( *)(\d+)( *))*)( +)((([^0-9\s])| |([0-9][a-zA-Z-\.,]))+)( *)(?=(\n))", i[0]
        ):
            
            if share_common_chars(string.ascii_letters, g.group().strip()) and ("..." not in g.group()):

                metadata.append([g.group().strip(), i[1]])

    return rearrange_manual_content_tree([
                    {
                        "filename": file_path,
                        "toc_info": metadata,
                    }
                ],str(int(random()*10000)))[0]['toc_info']
  