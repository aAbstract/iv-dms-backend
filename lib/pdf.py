import string
import unicodedata
from PyPDF2 import PdfReader
import re

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