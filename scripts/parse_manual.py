import re
import json
from glob import glob
from PyPDF2 import PdfReader


TOC_START_PAGE = 3


def create_parts_metadata_file():
    metadata = []
    manual_parts = glob('data/nesma_oma_parts/*.pdf')
    for part_path in manual_parts:
        pdf_reader = PdfReader(part_path)
        part_toc_content = pdf_reader.pages[TOC_START_PAGE - 1].extract_text()
        chapter_title = re.findall(r'Chapter \d+ [A-Za-z ]+', part_toc_content)[0].strip()
        metadata.append({
            'filename': part_path,
            'chapter_title': chapter_title,
            'toc_pages': (TOC_START_PAGE, -1),
        })

    with open('data/nesma_oma_parts/nesma_oma_metadata.json', 'w') as f:
        f.write(json.dumps(metadata, indent=2))


def create_manual_toc_tree():
    def parse_toc_txt_to_tree(toc_text: str) -> list[tuple[str, str, int]]:
        lines = toc_text.split('\n')
        toc_epattern = f" {'.'*32} "
        toc_info = []
        for line in lines:
            if toc_epattern in line:
                section_code = line.split(' ')[0]
                if section_code == 'Chapter':
                    continue
                if section_code == toc_epattern:
                    continue

                section_name = re.findall(f'\s[A-Za-z ]+\s+', line)
                if not section_name:
                    continue
                section_name = section_name[0].strip()

                page_number = re.findall(r'\s(\d+)', line)
                if page_number:
                    page_number = int(page_number[0])
                else:
                    page_number = -1

                toc_info.append((section_code, section_name, page_number))

        return toc_info

    f = open('data/nesma_oma_parts/nesma_oma_metadata.json', 'r')
    json_str = f.read()
    f.close()

    json_obj = json.loads(json_str)
    for mde in json_obj:
        if not mde['include']:
            continue
        toc_txt = ''
        pdf_reader = PdfReader(mde['filename'])
        for pidx in mde['toc_pages']:
            toc_txt += pdf_reader.pages[pidx - 1].extract_text()
        toc_info = parse_toc_txt_to_tree(toc_txt)
        mde['toc_info'] = toc_info

    f = open('data/nesma_oma_parts/nesma_oma_metadata.json', 'w')
    f.write(json.dumps(json_obj, indent=2))
    f.close()


def create_manual_content_tree() -> list[tuple[str, int]]:
    f = open('data/nesma_oma_parts/nesma_oma_metadata.json', 'r')
    json_str = f.read()
    f.close()
    json_obj = json.loads(json_str)
    for mde in json_obj:
        if not mde['include']:
            continue

        toc_info = []
        pdf_reader = PdfReader(mde['filename'])
        for pidx, page in enumerate(pdf_reader.pages):
            page_content = page.extract_text()
            toc_epattern = f" {'.'*32} "
            if toc_epattern in page_content:
                continue

            chapter_number = mde['chapter_title'].split(' ')[1]
            page_lines = page_content.split('\n')
            for line in page_lines:
                reps = '{1,2}'
                if re.findall(rf'^({chapter_number}(?:\.\d{reps})+)', line):
                    toc_info.append((line, pidx + 1))
        mde['toc_info'] = toc_info

    f = open('data/nesma_oma_parts/nesma_oma_metadata.json', 'w')
    f.write(json.dumps(json_obj, indent=2))
    f.close()


# create_parts_metadata_file()
# create_manual_toc_tree()
create_manual_content_tree()
