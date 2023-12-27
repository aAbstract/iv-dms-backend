import string
import unicodedata
from PyPDF2 import PdfReader


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
