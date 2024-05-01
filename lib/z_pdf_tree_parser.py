import fitz
import re
import string
from typing import Optional
from pydantic import BaseModel
from random import random
from faker import Faker
from models.fs_index import TocLink, TocTreeNode, ZTree
import json 

_CACHE_FOLDER = r"data/cache/toc_trees"

class ZPDF:
    ''' This class converts PDFs to indexable data structure '''
    doc: fitz.Document
    allowed_header_chars: str
    short_link_threshold: int
    toc_headers_count: int
    coverage_metric: float
    toc_pages: set[int]
    toc_tree: list[TocTreeNode]
    untitled_labels_count: int
    link_gap_count: int
    _link_idx_set: set
    _last_link_idx: str

    @staticmethod
    def _link_pattern_match(link_text: str) -> tuple[str, str] | None:
        # link_text contains chars and digits: T3E2ST, B737800
        if re.findall(r'\b(?=\w*\d)(?=\w*[A-Za-z])[A-Za-z0-9]+\b', link_text):
            idx = link_text.split(' ')[0]
            if re.findall(r'\d+\.?(?:\.\d+)*', idx):
                return link_text, idx

        # link_text contains only chars
        matches: list[tuple[str, str]] = re.findall(r'^((\d+\.?(?:\.\d+)*)[A-Za-z ]+)', link_text)
        if not matches or len(matches[0]) != 2:
            return None
        _link_text, idx = matches[0]
        if _link_text.strip() == idx:  # ignore garbage links: '33.3.3 '
            return None
        # fix x. pattern in top level toc headers
        if idx.split('.')[-1] == '':
            idx = idx[:-1]
        return _link_text, idx

    def _parse_link(self, page: fitz.Page, link: fitz.Link) -> TocLink | None:
        src_page_number = page.number
        des_page_number = int(link.dest.page)
        # remove backward links
        if des_page_number < src_page_number:
            return None

        link_text = page.get_textbox(link.rect)
        if len(link_text) < self.short_link_threshold:  # ignore doc intermediate short links
            return None

        link_text = ''.join([c for c in link_text if c in self.allowed_header_chars])
        self.toc_pages.add(page.number)
        link_parts_match = self._link_pattern_match(link_text.strip())
        if not link_parts_match:
            return None
        link_text, idx = link_parts_match

        # only keep unique toc headers
        if idx in self._link_idx_set:
            print(idx, 'Duplicate')
            return None
        self._link_idx_set.add(idx)
        return TocLink(link_idx=idx, link_label=link_text, target_page=des_page_number)

    def _fill_next_link_page(self, links: list[TocLink]) -> list[TocLink]:
        for idx, link in enumerate(links):
            if idx < len(links) - 1:
                link.next_link_page = links[idx + 1].target_page
                link.next_link_idx = links[idx + 1].link_idx
        self._last_link_idx = links[-1].link_idx
        return links

    def _extract_toc_links(self) -> list[TocLink]:
        toc_links = []
        for page in self.doc:
            link = page.first_link
            while link:
                toc_link = self._parse_link(page, link)
                if toc_link:
                    toc_links.append(toc_link)
                link = link.next
        toc_links = self._fill_next_link_page(toc_links)
        return toc_links

    @staticmethod
    def _compute_link_level(link_idx: str) -> int:
        return sum([1 for c in link_idx if c == '.'])

    def _build_toc_tree(self, links: list[TocLink], start_index: int, end_index: int, level: int) -> list[TocTreeNode]:
        children = []
        while start_index < end_index:
            link = links[start_index]
            link_level = ZPDF._compute_link_level(link.link_idx)
            if link_level == level:
                node = TocTreeNode(link_idx=link.link_idx, link_label=link.link_label, start_page=link.target_page)
                # find node children
                next_start = start_index + 1
                while next_start < end_index:
                    next_link_level = sum([1 for c in links[next_start].link_idx if c == '.'])
                    if next_link_level <= level:
                        break
                    next_start += 1
                # recursively build the subtree for the children
                node.children = self._build_toc_tree(links, start_index + 1, next_start, level + 1)
                # calculate end page of this node
                if node.children:
                    node.end_page = node.children[-1].end_page
                    node.end_tag = node.children[-1].end_tag
                else:
                    node.end_page = link.next_link_page
                    node.end_tag = link.next_link_idx
                    if node.start_page > node.end_page and node.link_idx != self._last_link_idx:
                        print(node.link_idx, 'Invalid')
                # append node to the list of children
                children.append(node)
                start_index = next_start
            else:
                start_index += 1
        return children

    @staticmethod
    def _remove_key_overlaps(keys: list[str]) -> list[str]:
        ''' Filter TOC index keys overlaps by removing child keys from the list and only leaving top level keys '''
        keys = keys.copy()
        keys.sort()
        non_overlapping = []
        for key in keys:
            if not non_overlapping or not any(key.startswith(v) for v in non_overlapping):
                non_overlapping.append(key)
        return non_overlapping

    def _validate_toc_tree(self, links: list[TocLink]) -> tuple[float, list[TocLink]]:
        not_found_links = []
        for link in links:
            node = self.find_toc_tree_node(link.link_idx)
            if not node:
                print(link.link_idx, 'not Found')
                not_found_links.append(link)
                continue
            if link.link_idx != node.link_idx:
                print(link.link_idx, 'Mismatch')
                not_found_links.append(link)
        not_found_pct = len(not_found_links) / len(links)
        return 1 - not_found_pct, not_found_links

    @staticmethod
    def _get_first_link_by_parent_key(parent_key: str, links: list[TocLink]) -> tuple[int, TocLink] | None:
        search_res = [(idx, link) for idx, link in enumerate(links) if link.link_label.startswith(parent_key)]
        if search_res:
            return search_res[0]
        return None

    def _try_find_untitled_header(self, link_idx: str) -> str:
        def basic_search(lines: list[str]) -> str | None:
            header_idx = [idx for idx, val in enumerate(lines) if val.strip() == link_idx or val.strip() == link_idx + '.']
            if not header_idx:
                return None
            header_idx = header_idx[-1]
            if header_idx == len(lines) - 1:
                return None
            return ''.join([lines[header_idx], lines[header_idx + 1]])

        def advanced_search(lines: list[str]) -> str | None:
            pattern = rf'^[A-Za-z]+\s+{link_idx}\s+[A-Za-z0-9 ]+'
            transformed_lines = [''.join([c for c in line if c in self.allowed_header_chars]) for line in lines]
            header_idx = [idx for idx, val in enumerate(transformed_lines) if re.findall(pattern, val)]
            if not header_idx:
                return None
            header_idx = header_idx[-1]
            return transformed_lines[header_idx]

        for toc_page in self.toc_pages:
            toc_page_text: str = self.doc.load_page(toc_page).get_text()
            lines = toc_page_text.split('\n')
            basic_search_res = basic_search(lines)
            if basic_search_res:
                return basic_search_res
            advanced_search_res = advanced_search(lines)
            if advanced_search_res:
                return advanced_search_res

        print('Can not Find Unlinked Index', link_idx)
        self.untitled_labels_count += 1
        return (link_idx + ' UNTITLED')

    @staticmethod
    def _links_gap_check_by_idx(idx_list: list[str]) -> list[str]:
        ''' Check missing index keys in a link sequence '''
        out_gap_list = []
        for i in range(len(idx_list) - 1):
            idx_1 = idx_list[i]
            idx_2 = idx_list[i + 1]
            if ZPDF._compute_link_level(idx_1) != ZPDF._compute_link_level(idx_2):
                continue
            try:
                idx_1_lsv = int(idx_1.split('.')[-1])
                idx_2_lsv = int(idx_2.split('.')[-1])
            except:
                continue
            if idx_2_lsv - idx_1_lsv != 1:
                common_part = '.'.join(idx_1.split('.')[:-1])
                out_gap_list += [common_part + f".{g}" for g in range(idx_1_lsv + 1, idx_2_lsv)]
        return out_gap_list

    def __init__(self, file_path: str, cache: list[dict] = []):
        print('Initializing ZPDF for file:', file_path)
        self.doc = fitz.open(file_path)
        self.allowed_header_chars = string.ascii_uppercase + string.ascii_lowercase + ' .' + string.digits
        self.short_link_threshold = 50
        self._link_idx_set = set()
        self.toc_pages = set()
        self.untitled_labels_count = 0
        self.link_gap_count = 0

        # load cache if exists
        if cache:
            print('Loading TOC Tree Cache...')
            self.toc_tree = [TocTreeNode.model_validate(cache_root_node) for cache_root_node in cache]
            print('Loading TOC Tree Cache...OK')
            return

        # create toc tree
        toc_links = self._extract_toc_links()
        idx_seq_gap = ZPDF._links_gap_check_by_idx([x.link_idx for x in toc_links])
        if idx_seq_gap:
            print('Found Link Gaps', idx_seq_gap)
            self.link_gap_count = len(idx_seq_gap)
        self.toc_headers_count = len(toc_links)
        print('Found', self.toc_headers_count, 'TOC Headers')
        inconsistent_links = [l for l in toc_links if not l.link_label.startswith(l.link_idx)]
        if inconsistent_links:
            print('Found Inconsistent Links', inconsistent_links)
        print('Building TOC Tree...')
        self.toc_tree = self._build_toc_tree(toc_links, 0, len(toc_links), 0)
        print('Building TOC Tree...OK')

        # generate toc coverage metric
        print('Validating TOC Tree...')
        coverage_metric, not_found_links = self._validate_toc_tree(toc_links)
        self.coverage_metric = coverage_metric
        print('TOC Coverage Metric:', self.coverage_metric)

        # post correction
        if len(not_found_links) == 0:
            return

        print('Running Post Correction...')
        missing_roots = {not_found_link.link_idx.split('.')[0] for not_found_link in not_found_links}
        for root_key in missing_roots:
            arr_idx, link = ZPDF._get_first_link_by_parent_key(root_key, toc_links)
            toc_links.insert(arr_idx, TocLink(
                link_idx=root_key,
                link_label=self._try_find_untitled_header(root_key),
                target_page=link.target_page,
            ))
        self.toc_headers_count = len(toc_links)
        print('Found', self.toc_headers_count, 'TOC Headers')
        toc_links = self._fill_next_link_page(toc_links)
        self.toc_tree = self._build_toc_tree(toc_links, 0, len(toc_links), 0)
        print('Running Post Correction...OK')

        # generate toc coverage metric
        print('Validating TOC Tree...')
        coverage_metric, not_found_links = self._validate_toc_tree(toc_links)
        self.coverage_metric = coverage_metric
        print('TOC Coverage Metric:', self.coverage_metric)

    def get_toc_node_text(self, node: TocTreeNode) -> str | None:
        if not node:
            return None

        # terminal section case
        if node.end_page == -1:
            terminal_section_text = ''
            for page in range(node.start_page, self.doc.page_count):
                page_text: str = self.doc.load_page(page).get_text()
                if page == node.start_page:
                    page_text = page_text.replace('\n', '')
                    terminal_section_text += page_text.split(f" {node.link_idx} ")[-1]
                    terminal_section_text += '\n'
                    continue
                terminal_section_text += page_text
            return terminal_section_text

        # single page case
        if node.start_page == node.end_page:
            start_page_text: str = self.doc.load_page(node.start_page).get_text()
            start_page_text = start_page_text.replace('\n', '')
            start_marker = f" {node.link_idx} "
            end_marker = f" {node.end_tag} "
            matches = re.findall(rf'{start_marker}(.*){end_marker}', start_page_text)
            if not matches:
                return None
            return matches[0]

        out_text = ''
        for page in range(node.start_page, node.end_page + 1):
            page_text: str = self.doc.load_page(page).get_text()
            if page == node.start_page:
                page_text = page_text.replace('\n', '')
                out_text += page_text.split(f" {node.link_idx} ")[-1]
                out_text += '\n'
                continue
            if page == node.end_page:
                page_text = page_text.replace('\n', '')
                out_text += '\n'
                out_text += page_text.split(f" {node.end_tag} ")[0]
                continue
            out_text += page_text
        return out_text

    def find_toc_tree_node(self, toc_key: str) -> TocTreeNode | None:
        if not self.toc_tree:
            return None

        # perform dfs traversal
        root_node_key = toc_key.split('.')[0]
        stack = [root_node for root_node in self.toc_tree if root_node.link_idx == root_node_key]
        if not stack:
            return None
        while stack:
            node = stack.pop(0)  # optimization that abuses the sorted toc_tree
            if node.link_idx == toc_key:
                return node
            stack += node.children

    def get_cache(self) -> list[dict]:
        return [root_node.model_dump() for root_node in self.toc_tree]

    def get_toc_tree(self):
        return self.toc_tree

    def get_benchmark(self) -> dict:
        return {
            'toc_headers_count': self.toc_headers_count,
            'coverage_metric': self.coverage_metric,
            'untitled_labels_count': self.untitled_labels_count,
            'link_gap_count': self.link_gap_count,
        }

    def extract_text(self, toc_keys: list[str]) -> list[str]:
        filtered_keys = ZPDF._remove_key_overlaps(toc_keys)
        toc_tree_nodes = [self.find_toc_tree_node(key) for key in filtered_keys]
        return [self.get_toc_node_text(node) for node in toc_tree_nodes]
            
    def save_cache(self, file_name : str) -> None:

        with open(fr'{_CACHE_FOLDER}/{file_name}.json', 'w') as f:
            f.write(json.dumps(self.get_cache(), indent=2))

    def get_cache_transformed(self) -> list[dict]:

        tree = self.get_cache()

        # Create random number generator
        Faker.seed(int(random()*1000000))
        fake = Faker("en_US")

        def transform_node(node):
            # function to transform the z tree into a format for display
            node["label"] = node.pop("link_label")
            node['section_label'] = node.pop("link_idx")
            node["pages"] = [node['start_page'],node["end_page"]]

            # random hash
            node["key"] = str(int(random()*1000000)) + str(fake.unique.random_int(min=111111111111, max=999999999999))

        # No Recursion as it could cause the server to shut down
        for chapter in tree:
            transform_node(chapter)
            if chapter.get("children"):
                for child in chapter.get("children"):
                    transform_node(child)
                    if child.get("children"):
                        for child in child.get("children"):
                            transform_node(child)
                            if child.get("children"):
                                for child in child.get("children"):
                                    transform_node(child)
                                    if child.get("children"):
                                        for child in child.get("children"):
                                            transform_node(child)
                                            if child.get("children"):
                                                for child in child.get("children"):
                                                    transform_node(child)
                                                    if child.get("children"):
                                                        for child in child.get("children"):
                                                            transform_node(child)
        # validate output and remove extra keys
        for idx,chapter in enumerate(tree):
            tree[idx] = ZTree.model_validate(chapter).model_dump(exclude_unset=True)      

        return tree

