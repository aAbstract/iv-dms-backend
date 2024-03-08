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


df = read_csv("data/gacar/gacar_117.csv")
unique_set = {}
g = {"name": "", "code": "", "applicability": "", "guidance": "", "items": []}
g_map = {"code": "", "title": "GACAR Part 117", "sub_sections": []}
# this is heavly relient on the excels structure
# revise before inputting other excel sheets
for i in df.values:
    if not g["name"] or g["code"]:
        g["code"] = "GACAR " + str(i[1])
        g_map["code"] = "GACAR " + str(i[1])
        g["name"] = "GACAR Part " + str(i[1])

    if "GACAR " + str(i[3]) in unique_set:
        unique_set["GACAR " + str(i[3])]["paragraph"] += "\n" + i[-1]
    else:
        g_map["sub_sections"].append("GACAR " + str(i[3]))
        unique_set["GACAR " + str(i[3])] = {
            "paragraph": i[6] + "\n" + i[-1],
            "code": "GACAR " + str(i[3]),
            "iosa_map":["GACAR " + str(i[3])]
        }

for i in unique_set.values():
    i["paragraph"] = convert_to_markdown(clean(i["paragraph"]))
    g["items"].append(i)

# write to a separate json file
with open(rf"data/gacar/GACAR_117.json", "w") as fp:
    json.dump(g, fp, indent=4)

with open(rf"data/gacar/GACAR_117_map.json", "w") as fp:
    json.dump([g_map], fp, indent=4)
