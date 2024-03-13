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

# def remove_duplicates_keep_highest_index(input_list):
#     index_dict = {}

#     for pair in input_list:
#         key = pair[0]
#         value = pair[1]
#         index_dict[key] = max(index_dict.get(key, -1), input_list.index(pair))

#     result_list = [[key, input_list[index][1]] for key, index in index_dict.items()]

#     return result_list
def get_header_footer(file_path):
    def find_common_numbers(list_of_lists):
        if not list_of_lists:
            return []
        common_numbers = set(list_of_lists[0])

        for sublist in list_of_lists[1:]:
            common_numbers = common_numbers.intersection(sublist)

        return list(common_numbers)
    
    def split_by_mean(numbers):
        if not numbers:
            return [], []

        # Calculate the mean of the numbers
        mean = sum(numbers) / len(numbers)

        # Initialize two lists for numbers greater than or equal to the mean and less than the mean
        greater_or_equal = []
        less_than = []

        # Iterate through the numbers and split them based on their relation to the mean
        for num in numbers:
            if num >= mean:
                greater_or_equal.append(num)
            else:
                less_than.append(num)

        return greater_or_equal, less_than

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

    # exit()
    # small after big then remove if small is bigger than big
    # temp_metadata = []
    # last_head = ""
    # ignore_first = True

    # for i in range(len(metadata)-1):

    #     # ask if header is equal to last header
    #     # ask if header is equal to last small
    #     # ((([^0-9\s])| |([0-9][a-zA-Z-\.,]))+
    #     if re.compile(r"( *)(\d+)( *)\.( *)(\d+)( *)").match(metadata[i][0]): 
    #         if not ignore_first:
    #             print(metadata[i][0])
    #             temp_metadata.append(metadata[i])

            
    #     elif(re.compile(r"( *)(\d+)( *)").match(metadata[i][0])):
    #         if ignore_first:
    #             ignore_first = False

    #             temp_metadata.append(metadata[i])
    #             last_head = metadata[i][0]

    #         elif(int(last_head[0]) != int(metadata[i][0][0])):
    #             if(int(metadata[i][0][0]) == int(metadata[i+1][0][0])):
    #                 last_head = metadata[i][0]

    #                 temp_metadata.append(metadata[i])
    #             else:
    #                 continue



        # print(last_small,i[0],last_was_small)
        # if re.compile(r"( *)(\d+)( *)\.( *)(\d+)( *)((.| )+)").fullmatch(i[0]):  
        #     last_small = i[0]
        #     last_was_small = True
        #     print("Nothing1")

        # elif(re.compile(r"( *)\d+( *)((.| )+)").fullmatch(i[0])):
        #     if(last_was_small):
        #         if(int(last_small[0]) >= int(i[0][0])):
        #             print("removed")
        #             continue
        #         else:
        #             print(int(last_small[0]), int(i[0][0]))
        #             print("error1")
        #     else:
        #         print("error2")

        #     last_was_small = False
        # else:
        #     print("Nothing2")
        #     last_small = ""
        #     last_was_small = False
        # temp_metadata.append(i)
    # print(temp_metadata)

    # metadata = temp_metadata[:]

    # metadata = remove_duplicates_keep_highest_index(metadata)

    return rearrange_manual_content_tree([
                    {
                        "filename": file_path,
                        "toc_info": metadata,
                    }
                ],str(int(random()*10000)))[0]['toc_info']
  