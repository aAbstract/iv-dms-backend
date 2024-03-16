# autopep8: off
import json
import os
import sys
import string
import re
import unicodedata
from PyPDF2 import PdfReader
from dotenv import load_dotenv


def load_root_path():
    file_dir = os.path.abspath(__file__)
    lv1_dir = os.path.dirname(file_dir)
    root_dir = os.path.dirname(lv1_dir)
    sys.path.append(root_dir)


load_root_path()
load_dotenv()
from models.regulations import *

# autopep8: on


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

def clean(text, allowed=list(string.printable)):
    unicode_dashes = [
        "\u2010",  # hyphen
        "\u2011",  # non-breaking hyphen
        "\u2012",  # en dash
        "\u2013",  # en dash
        "\u2014",  # em dash
        "\u2015",  # horizontal bar
        "\u2212",  # minus sign
        "\u301c",  # wave dash
        "\ufe63",  # small hyphen-minus
    ]

    filtered_text = ""

    for char in text:
        if char in allowed:
            filtered_text += char
        elif char in unicode_dashes:
            filtered_text += "-"
        elif unicodedata.category(char)[0] == "Z":
            filtered_text += " "
        elif unicodedata.category(char)[0] == "C":
            filtered_text += "\n"
        else:
            filtered_text += " "

    return filtered_text


def extract(path):
    all_pages = []
    reader = PdfReader(path)
    pages = reader.pages
    page_number = 0
    char_count = 0
    all_page_count = []

    for i in pages:
        parts = []

        def visitor_body(text, cm, tm, fontDict, fontSize):
            # crop the header and footer
            y = tm[5]
            # these sohuld be changed for different pdf headers
            if (y > 88) and (y < 770):
                parts.append(text)

        i.extract_text(visitor_text=visitor_body)
        text_body = "".join(parts)
        all_pages.append(text_body)
        all_page_count.append({"count":char_count, "page":page_number})
        char_count += len(text_body)
        page_number+=1

    return all_pages , all_page_count


def contains_span(span, span_array):
    for i in span_array:
        if span[0] == i[0]:
            return True
    return False


def contains_span_intext(span, span_array):
    for i in span_array:
        if span[0] == i[0] + 2:
            return True
    return False


def check_type(text):
    romans = "ii|iii|iv|v|vi|vii|viii|ix|x|xi|xii|xiii|xiv|xv|xvi|xvii|xviii|xix|xx|xxi|xxii|xxiii|xxiv|xxv|xxvi|xxvii|xxviii|xxix|xxx"
    alphas = "abcdefghijklmnopqrstuvwxyz"

    if text[0] == "(":
        second_brak = text[:].find(")")
        if second_brak == -1:
            return "t"
        sub = text[1:second_brak]
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
    items = [i for i in items if i]

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
    return constraints


def extract_section_header(text, first_flt_span, filename):
    section_name_reg = r"Section (\d+) - ([\w\s]+) \(([\w]+)\)\n"
    general_guidence_reg = r"General Guidance\n"
    applicability_reg = r"Applicability\n"

    section_header_text = text[0:first_flt_span].strip("\n").strip()
    section_name = (
        re.match(section_name_reg, section_header_text).group()[:-1].strip("\n").strip()
    )
    section_code = section_name[section_name.find("(") + 1 : -1].strip("\n").strip()

    gg = re.search(general_guidence_reg, section_header_text).span()[0]
    ap = re.search(applicability_reg, section_header_text).span()[0]

    return {
        "name": section_name,
        "code": section_code,
        "guidance": section_header_text[gg:].strip("\n").strip(),
        "applicability": section_header_text[ap:gg].strip("\n").strip(),
        "order": section_name.split()[1].strip("\n").strip(),
        "items": [],
    }


def extract_section_text(text,section_code,all_page_count, page_start):

    flts = rf"({section_code}\s*)([0-9]+(\.[0-9]+)*)([A-Za-z]*)(\-([0-9]+(\.[0-9]+)*)([A-Za-z]*))*"

    in_text_flts_beg = rf". ({section_code}\s*)([0-9]+(\.[0-9]+)*)([A-Za-z]*)(\-([0-9]+(\.[0-9]+)*)([A-Za-z]*))*"
    in_text_flts_end = rf"({section_code}\s*)([0-9]+(\.[0-9]+)*)([A-Za-z]*)(\-([0-9]+(\.[0-9]+)*)([A-Za-z]*))* ."
    auditor_actions_reg = r"\nAuditor Actions\n"
    Guidence_reg = r"\nGuidance\n"
    gm_reg = r"\(GM\)"
    sms_reg = r"\[SMS\]"
    all_sections = []
    in_text_spans_beg = []
    in_text_spans_end = []
    flts_spans = []
    flts_spans_clean = []

    # parse header source map
    header_source_map = None
    with open(f"data/parsed_iosa/{filename}_map.json", "r") as f:
        header_source_map = json.loads(f.read())

    for i in re.finditer(flts, text):
        flts_spans.append(i.span())
    for i in re.finditer(in_text_flts_beg, text):
        in_text_spans_beg.append(i.span())
    for i in re.finditer(in_text_flts_end, text):
        in_text_spans_end.append(i.span())

    flts_spans_clean = []
    for i in flts_spans:
        if not (
            (contains_span_intext(i, in_text_spans_beg))
            or (contains_span(i, in_text_spans_end))
        ):
            flts_spans_clean.append(i)

    flts_spans = flts_spans_clean[:]

    for i in range(0, len(flts_spans) - 1):
        header = text[flts_spans[i][0] : flts_spans[i][1]].strip("\n").strip()

        paragraph = text[flts_spans[i][1] : flts_spans[i + 1][0]]

        gg = re.search(Guidence_reg, paragraph)
        if gg:
            guidence = paragraph[gg.span()[0] :].strip("\n").strip()
            paragraph = paragraph[: gg.span()[0]]

        aa = re.search(auditor_actions_reg, paragraph)
        if aa:
            auditor_actions = paragraph[aa.span()[0] :].strip("\n").strip()
            paragraph = paragraph[: aa.span()[0]]

        gm = re.search(gm_reg, paragraph)
        if gm:
            gm_text = paragraph[gm.span()[0] :].strip("\n").strip()
            paragraph = paragraph[: gm.span()[0]]

        sms = re.search(sms_reg, paragraph)
        if sms:
            sms_text = paragraph[sms.span()[0] :].strip("\n").strip()
            paragraph = paragraph[: sms.span()[0]]

        page_number = None
        # find the page number
        for char_range in range(len(all_page_count)):
            if(all_page_count[char_range]['count'] >= flts_spans[i][1]):
                page_number = all_page_count[char_range-1]['page']
                break
        if(page_number == None):
            page_number = all_page_count[-1]['page']

        # parse header source map
        idxs = header.split(" ")[1].split(".")
        section_index = int(idxs[0]) - 1
        sub_section_index = int(idxs[1]) - 1

        all_sections.append(
            {
                "code": header,
                "guidence": guidence if guidence else None,
                "iosa_map": [
                    header_source_map[section_index]["title"],
                    header_source_map[section_index]["sub_sections"][sub_section_index],
                ],
                "paragraph": convert_to_markdown(paragraph.strip()),
                "page": page_number + page_start,
                # "constraints": parse_paragraph(paragraph),
            }
        )
    header = text[flts_spans[-1][0] : flts_spans[-1][1]].strip("\n").strip()
    paragraph: str = text[flts_spans[-1][1] :]
    gg = re.search(Guidence_reg, paragraph)
    if gg:
        guidence = paragraph[gg.span()[0] :].strip("\n").strip()
        paragraph = paragraph[: gg.span()[0]]

    aa = re.search(auditor_actions_reg, paragraph)
    if aa:
        auditor_actions = paragraph[aa.span()[0] :].strip("\n").strip()
        paragraph = paragraph[: aa.span()[0]]

    gm = re.search(gm_reg, paragraph)
    if gm:
        gm_text = paragraph[gm.span()[0] :].strip("\n").strip()
        paragraph = paragraph[: gm.span()[0]]

    sms = re.search(sms_reg, paragraph)
    if sms:
        sms_text = paragraph[sms.span()[0] :].strip("\n").strip()
        paragraph = paragraph[: sms.span()[0]]

    # parse header source map
    idxs = header.split(" ")[1].split(".")
    section_index = int(idxs[0]) - 1
    sub_section_index = int(idxs[1]) - 1

    page_number = None
    # find the page number
    for char_range in range(len(all_page_count)):
        if all_page_count[char_range]["count"] >= flts_spans[i][1]:
            page_number = all_page_count[char_range - 1]["page"]
            break
    if page_number == None:
        page_number = all_page_count[-1]["page"]

    all_sections.append(
        {
            "code": header,
            "guidence": guidence if guidence else None,
            "iosa_map": [
                header_source_map[section_index]["title"],
                header_source_map[section_index]["sub_sections"][sub_section_index],
            ],
            "paragraph": convert_to_markdown(paragraph.strip()),
            "page": page_number + page_start,
            # "constraints": parse_paragraph(paragraph),
        }
    )

    return all_sections, flts_spans[0][0]

def extract_tables(text,section_code,all_page_count, page_start):

    tables = r"Table( *)([0-9]+)( *)\.( *)([0-9]+)( *)-( *)(([^\s]| )*)(?=(\n))"

  
    all_sections = []
    flts_spans = []

    # parse header source map
    header_source_map = None
    with open(f"data/parsed_iosa/{filename}_map.json", "r") as f:
        header_source_map = json.loads(f.read())

    for i in re.finditer(tables, text):
        flts_spans.append(i.span())


    for i in range(0, len(flts_spans) - 1):
        header = text[flts_spans[i][0] : flts_spans[i][1]].strip("\n").strip()

        paragraph = text[flts_spans[i][1] : flts_spans[i + 1][0]]

        page_number = None
        # find the page number
        for char_range in range(len(all_page_count)):
            if(all_page_count[char_range]['count'] >= flts_spans[i][1]):
                page_number = all_page_count[char_range-1]['page']
                break
        if(page_number == None):
            page_number = all_page_count[-1]['page']
   
        all_sections.append(
            {
                "code": section_code+' '+ header,
                "guidence": None,
                "iosa_map": [
                    header_source_map[0]["title"],
                ],
                "paragraph": convert_to_markdown(paragraph.strip()),
                "page": page_number + page_start,
                # "constraints": parse_paragraph(paragraph),
            }
        )
    header = text[flts_spans[-1][0] : flts_spans[-1][1]].strip("\n").strip()
    paragraph: str = text[flts_spans[-1][1] :]

    page_number = None
    i = len(flts_spans) - 1
    # find the page number
    for char_range in range(len(all_page_count)):
        if all_page_count[char_range]["count"] >= flts_spans[i][1]:
            page_number = all_page_count[char_range - 1]["page"]
            break
    if page_number == None:
        page_number = all_page_count[-1]["page"]

    all_sections.append(
        {
            "code":section_code+' '+  header,
            "guidence": None,
            "iosa_map": [
                header_source_map[0]["title"],
            ],
            "paragraph": convert_to_markdown(paragraph.strip()),
            "page": page_number + page_start,
            # "constraints": parse_paragraph(paragraph),
        }
    )

    return all_sections

if __name__ == "__main__":
    codes = ["cgo", "org", "dsp", "grh", "mnt", "cab", "sec", "flt"]
    page_starts = [611, 40, 288, 547, 392, 478, 646, 104]
    table_starts = {"ORG":101,"FLT":276,"DSP":381,"MNT":450,"CAB":537,"CGO":644}
    for i, g in zip(codes, page_starts):
        filename = f"iosa_{i}"
        code = i.upper()

        all_pages, all_page_count = extract(f"data/parsed_iosa/{filename}.pdf")
        # remove all unallowed chars
        for z in range(len(all_pages)):
            all_pages[z] = clean(all_pages[z])

        all_pages = " ".join(all_pages)

        all_sections, first_flt_span = extract_section_text(
            all_pages, code, all_page_count, g
        )

        if(table_starts.get(code)):
            all_tables, all_table_count =  extract(f"data/parsed_iosa/{filename}_tables.pdf")
            # remove all unallowed chars
            for z in range(len(all_tables)):
                all_tables[z] = clean(all_tables[z])
            all_tables = " ".join(all_tables)

            all_tables = extract_tables(
                all_tables, code, all_table_count, table_starts[code]
            )
            all_sections = all_sections + all_tables

        section = extract_section_header(all_pages, first_flt_span, filename)

        section["items"] = all_sections
        # validate
        section = IOSASection(
            name=section["name"],
            code=section["code"],
            applicability=section["applicability"],
            guidance=section["guidance"],
            items=section["items"],
        )

        # write to a separate json file
        file_path = f"data/parsed_iosa/{filename}.json"
        with open(file_path, "w") as fp:
            json.dump(section.model_dump(), fp, indent=4)
        print(f"output file: {file_path}")
        # TODO: change data source file names
