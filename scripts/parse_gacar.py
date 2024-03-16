from glob import glob
from pandas import read_csv
import json
import re


def clean(text):
    new_text = text[:]
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
        "\u206f": "",
    }
    for escape, replacement in replacements.items():
        text = text.replace(escape, replacement)

    return new_text


def convert_to_listing(text):
    romans = {
        "(a)": "(i)",
        "(b)": "(ii)",
        "(c)": "(iii)",
        "(d)": "(iv)",
        "(e)": "(v)",
        "(f)": "(vi)",
        "(g)": "(vii)",
        "(h)": "(viii)",
    }
    alphas = {
        "(1)": "(a)",
        "(2)": "(b)",
        "(3)": "(c)",
        "(4)": "(d)",
        "(5)": "(e)",
        "(6)": "(f)",
        "(7)": "(g)",
        "(8)": "(h)",
    }
    for i, g in romans.items():
        text = text.replace(i, g)

    for i, g in alphas.items():
        text = text.replace(i, g)

    return text


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

    markdown_text = re.sub(r"(?<=\w)\n(?=\w)", " ", text)
    markdown_text = re.sub(r"\n\((\w+)\)", replace_listing, markdown_text)
    return markdown_text

section_columns = {
    "117":"Subpart Section",
    "109": "Subpart/ Appendix SECTION",
    "91": "Subpart/ Appendix SECTION"
}

for file in glob("data/gacar/*.csv"):

    df = read_csv(file) 
    
    gacar_code = re.split(r"[\\|/]",file)[-1].split(".")[0]

    df = df[df["REGULATION  STATEMENT"].notna()].reset_index()
    df = df[df[section_columns[gacar_code]].notna()].reset_index()

    unique_gacar_headers = {}
    header = {"name": f"GACAR Part {gacar_code}", "code": f"G-{gacar_code}", "applicability": "", "guidance": "", "items": []}
    temp_checklist_item = {"code": f"G-{gacar_code} {gacar_code}", "title": f"GACAR Part {gacar_code}", "sub_sections": []}

    for i in range(len(df)):
        
        new_code = str(df[section_columns[gacar_code]][i]).strip()
        
        header_code = header["code"] + " " + new_code

        if header_code in unique_gacar_headers:
            unique_gacar_headers[header_code]["paragraph"] += df["REGULATION  STATEMENT"][i] + ";\n"
        else:
            temp_checklist_item["sub_sections"].append(header_code)
            unique_gacar_headers[header_code] = {
                "paragraph":df["REGULATION  STATEMENT"][i] + ";\n",
                "code":header_code,
                "iosa_map": [header_code],
            }

    for i in unique_gacar_headers.values():
        i["paragraph"] = convert_to_markdown(convert_to_listing(clean(i["paragraph"])))
        header["items"].append(i)

    # write to a separate json file
    with open(rf"data/gacar/GACAR_{gacar_code}.json", "w") as fp:
        json.dump(header, fp, indent=4)

    with open(rf"data/gacar/GACAR_{gacar_code}_map.json", "w") as fp:
        json.dump([temp_checklist_item], fp, indent=4)
