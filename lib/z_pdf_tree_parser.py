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
    debug: bool
    doc: fitz.Document
    allowed_header_chars: str
    toc_headers_count: int
    coverage_metric: float
    toc_tree: list[TocTreeNode]
    _link_idx_set: set
    _last_link_idx: str

    def _parse_link(self, page: fitz.Page, link: fitz.Link) -> TocLink | None:
        src_page_number = page.number
        des_page_number = int(link.dest.page)
        # remove backward links
        if des_page_number < src_page_number:
            return None

        link_text = page.get_textbox(link.rect)
        link_text = ''.join([c for c in link_text if c in self.allowed_header_chars])
        matches = re.findall(r'^((\d+\.?(?:\.\d+)*)[A-Za-z ]+)[\.\s]+', link_text)
        if not matches:
            return None
        if len(matches[0]) < 2:
            return None

        link_text, idx = matches[0]
        # fix x. pattern in top level toc headers
        if idx.split('.')[-1] == '':
            idx = idx[:-1]
        # only keep unique toc headers
        if idx in self._link_idx_set:
            if self.debug:
                print(idx, 'Duplicate')
            return None

        self._link_idx_set.add(idx)
        return TocLink(link_idx=idx, link_label=link_text, target_page=des_page_number)

    def _fill_next_link_page(self, links: list[TocLink]) -> list[TocLink]:
        for idx, link in enumerate(links):
            if idx < len(links) - 1:
                link.next_link_page = links[idx + 1].target_page
                link.next_link_label = links[idx + 1].link_label
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

    def _build_toc_tree(self, links: list[TocLink], start_index: int, end_index: int, level: int) -> list[TocTreeNode]:
        children = []
        while start_index < end_index:
            link = links[start_index]
            link_level = sum([1 for c in link.link_idx if c == '.'])
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
                    node.end_link_label = node.children[-1].end_link_label
                else:
                    node.end_page = link.next_link_page
                    node.end_link_label = link.next_link_label
                    if node.start_page > node.end_page and self.debug and node.link_idx != self._last_link_idx:
                        print(node.link_idx, 'Invalid')
                # append node to the list of children
                children.append(node)
                start_index = next_start
            else:
                start_index += 1
        return children

    def _remove_key_overlaps(self, keys: list[str]) -> list[str]:
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
                if self.debug:
                    print(link.link_idx, 'not Found')
                not_found_links.append(link)
                continue
            if link.link_idx != node.link_idx:
                if self.debug:
                    print(link.link_idx, 'Mismatch')
                not_found_links.append(link)
        not_found_pct = len(not_found_links) / len(links)
        return 1 - not_found_pct, not_found_links

    def _get_first_link_by_parent_key(self, parent_key: str, links: list[TocLink]) -> tuple[int, TocLink] | None:
        search_res = [(idx, link) for idx, link in enumerate(links) if link.link_label.startswith(parent_key)]
        if search_res:
            return search_res[0]
        return None

    def __init__(self, file_path: str, cache: list[dict] = [], debug: bool = False):
        print('Initializing ZPDF for file:', file_path)
        self.debug = debug
        self.doc = fitz.open(file_path)
        self.allowed_header_chars = string.ascii_uppercase + string.ascii_lowercase + ' .' + string.digits
        self._link_idx_set = set()

        # load cache if exists
        if cache:
            print('Loading TOC Tree Cache...')
            self.toc_tree = [TocTreeNode.model_validate(cache_root_node) for cache_root_node in cache]
            print('Loading TOC Tree Cache...OK')
            return

        # create toc tree
        toc_links = self._extract_toc_links()
        self.toc_headers_count = len(toc_links)
        print('Found', self.toc_headers_count, 'TOC Headers')
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
            arr_idx, link = self._get_first_link_by_parent_key(root_key, toc_links)
            toc_links.insert(arr_idx, TocLink(
                link_idx=root_key,
                link_label=(root_key + ' UNTITLED'),
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

        # single page case
        end_link_idx = node.end_link_label.split(' ')[0]
        if node.start_page == node.end_page:
            start_page_text: str = self.doc.load_page(node.start_page).get_text()
            start_page_text = start_page_text.replace('\n', '')
            start_marker = f" {node.link_idx} "
            end_marker = f" {end_link_idx} "
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
                out_text += page_text.split(f" {end_link_idx} ")[0]
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
        }

    def extract_text(self, toc_keys: list[str]) -> list[str]:
        filtered_keys = self._remove_key_overlaps(toc_keys)
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

