import string
import unicodedata
from PyPDF2 import PdfReader
import re

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

    found_newline = False
    found_space = False

    for char in text:
        if char in allowed:
            filtered_text += char
            found_newline = False
            found_space = False

        elif char in unicode_dashes:
            filtered_text += "-"
            found_newline = False
            found_space = False

        elif unicodedata.category(char)[0] == "Z":
            if not found_space:
                filtered_text += " "
                found_space = True
            found_newline = False
        elif unicodedata.category(char)[0] == "C":
            if not found_newline:
                filtered_text += "\n"
                found_newline = True
            found_space = False

    return filtered_text


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