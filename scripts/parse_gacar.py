from datetime import datetime
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

    if ("\n(a)" in text) or ("\n(i)" in text) or (("\n(1)" in text)):

        first_level = "i"
        second_level = "a"
        a_level = text.find("\n(a)") if text.find("\n(a)")!= -1 else 9999
        r_level = text.find("\n(i)") if text.find("\n(i)")!= -1 else 99999
        n_level = text.find("\n(1)") if text.find("\n(1)") != -1 else 99999

        if (a_level < r_level) and (a_level < n_level):
            first_level = "a"
            if r_level < n_level:
                second_level = "i"
            else:
                second_level = "1"

        elif (n_level < r_level) and (n_level < a_level):
            first_level = "1"
            if r_level < a_level:
                second_level = "i"
            else:
                second_level = "a"
        elif (r_level < n_level) and (r_level < a_level):
            first_level = "i"
            if n_level < a_level:
                second_level = "1"
            else:
                second_level = "a"

        romans = [
            "(i)",
            "(ii)",
            "(iii)",
            "(iv)",
            "(v)",
            "(vi)",
            "(vii)",
            "(viii)",
        ]
        numbers = [
            "(1)",
            "(2)",
            "(3)",
            "(4)",
            "(5)",
            "(6)",
            "(7)",
            "(8)"
        ]
        alphas = [
            "(a)",
            "(b)",
            "(c)",
            "(d)",
            "(e)",
            "(f)",
            "(g)",
            "(h)"
        ]
        if(first_level == "a"):
            for i, g in zip(alphas,romans):
                text = text.replace(i, g)        

        elif(first_level == "r"):
            pass

        elif(first_level == "1"):
            for i, g in zip(numbers,romans):
                text = text.replace(i, g)

        if(second_level == "a"):
            pass
        elif(second_level == "r"):
            for i, g in zip(romans,alphas):
                text = text.replace(i, g)
        elif(second_level == "1"):
            for i, g in zip(numbers,alphas):
                text = text.replace(i, g)
        return text
    else:
        return text

def convert_to_markdown(text):
    romans = [
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
        ]
    alphas =  [
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
        ]

    def replace_listing(match):
 
        listing_type = match.group().replace(")","").strip().lower()
        listing_type = listing_type[listing_type.find("(")+1:]

        if listing_type in romans:
            return f"\n- ({listing_type})"
        elif listing_type in alphas:
            return f"\n  - ({listing_type})"
        else:
            return f"({listing_type})"

    markdown_text = re.sub(r"(?<=\w)\n(?=\w)", " ", text)

    markdown_text = re.sub(r"(\n\(|\n|;\(|\.\(|:\(|,\()\w{1,5}\) ", replace_listing, markdown_text)
    return markdown_text


section_columns = {
    "117": "Subpart Section",
    "109": "Subpart/ Appendix SECTION",
    "91GACAR": "Subpart/ Appendix SECTION",
    "7": "Subpart/ Appendix SECTION",
    "4":"SECTION",
    "5":"SECTION",
    "121":"SUBPART/ APPENDIX SECTION",
    "157":"Subpart Section",
    "66":"Subpart Section",
    "65":"Subpart Section",
    "47":"Subpart Section",
    "91ECAR":"Subpart Section",
    "43":"Subpart Section",
    "119":"Subpart Section"
}


regulation = {
            "type":"GACAR",
            "name":"(GACAR) General Authority of Civil Aviation of Saudi Arabia",
            "effective_date":"",
            "sections":[],
    }
regulation_map = []

for file in glob("data/gacar/*.csv"):

    df = read_csv(file)

    gacar_code = re.split(r"[\\|/]", file)[-1].split(".")[0]

    df = df[df["REGULATION  STATEMENT"].notna()].reset_index()
    df = df[df[section_columns[gacar_code]].notna()].reset_index()

    unique_headers = {}
    header = {
        "name": "",
        "code": f"G-{gacar_code}",
        "applicability": "",
        "guidance": "",
        "items": [],
    }
    gacar_map = {
        "code": f"G-{gacar_code} {gacar_code}",
        "title": f"GACAR Part {gacar_code}",
        "sub_sections": [f"GACAR Part {gacar_code}"],
    }

    for i in range(len(df)):
        new_code = str(df[section_columns[gacar_code]][i]).strip()
        if not new_code.startswith(gacar_code):
            new_code = f"{gacar_code}.{new_code}"

        header_code = f"G-{gacar_code} {new_code}"

        if header_code in unique_headers:
            unique_headers[header_code]["paragraph"] += (
                df["REGULATION  STATEMENT"][i] + "\n"
            )
        else:
            # gacar_map["sub_sections"].append(header_code)
            unique_headers[header_code] = {
                "paragraph": df["REGULATION  STATEMENT"][i] + "\n",
                "code": header_code,
                "iosa_map": [f"GACAR Part {gacar_code}"],
            }
    for i in unique_headers.values():
        i["paragraph"] = convert_to_markdown(clean(i["paragraph"]))
        header["items"].append(i)
    regulation_map.append(gacar_map)
    regulation['sections'].append(header)

# write to a separate json file
with open(rf"data/gacar/GACAR.json", "w") as fp:
    json.dump(regulation, fp, indent=4)

with open(rf"data/gacar/GACAR_map.json", "w") as fp:
    json.dump(regulation_map, fp, indent=4)
