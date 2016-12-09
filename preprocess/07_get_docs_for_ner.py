#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to select documents with references to the selected yago entities.

Usage:
    07_get_docs_for_ner.py <pickles_dir> <resources_dir> <links_dir> <output_dir>

pickles_dir is the directory with the pickled yago downloads
"""


from __future__ import unicode_literals, print_function

import cPickle as pickle
import os
import sys
from bs4 import BeautifulSoup
from docopt import docopt
from tqdm import tqdm

args = docopt(__doc__, version=1.0)
pickles_dir = args['<pickles_dir>']
resources_dir = args['<resources_dir>']
links_dir = args['<links_dir>']
output_dir = args['<output_dir>']

wikipages = set()
ids_urls = {}
uris_urls = {}

for pkl in tqdm(os.listdir(pickles_dir)):
    with open(os.path.join(pickles_dir, pkl)) as f:
        wikipages = wikipages.union({w[1] for w in pickle.load(f)[1:]})

with open(os.path.join(resources_dir, "ids_urls.txt"), "r") as f:
    for line in tqdm(f.readlines()):
        line = line.strip().split(",", 1)
        ids_urls[line[0]] = line[1]

with open(os.path.join(resources_dir, "parsed_uris.txt"), "r") as f:
    for line in tqdm(f.readlines()):
        line = line.strip().split(",http://", 1)
        uris_urls[line[0]] = "http://{}".format(line[1])

for wiki_doc in sorted(os.listdir(links_dir)):
    print("Extracting NE from {}".format(wiki_doc), file=sys.stderr)

    last_doc_id = None
    docs_for_ner = {}
    last_doc_in_wikipages = False

    with open(os.path.join(links_dir, wiki_doc), "r") as f:
        for line in tqdm(f):
            soup = BeautifulSoup(line.strip().decode("utf-8"), "lxml")
            if soup.find('doc') is not None:
                last_doc_id = soup.doc["id"]
                last_doc_in_wikipages = (last_doc_id in ids_urls and
                                         ids_urls[last_doc_id] in wikipages)
                if last_doc_in_wikipages:
                    docs_for_ner[last_doc_id] = ids_urls[last_doc_id]
            elif soup.find('a') is not None and not last_doc_in_wikipages:
                try:
                    a = soup.a['href']
                    if a in uris_urls and uris_urls[a] in wikipages:
                        docs_for_ner[last_doc_id] = ids_urls[last_doc_id]
                        last_doc_in_wikipages = True
                except KeyError:
                    pass

    print("Finished extracting NE from {}. Saving files.".format(wiki_doc),
          file=sys.stderr)
    with open(os.path.join(output_dir, "docs_in_ner.txt"), "a") as f:
        for doc in tqdm(sorted(docs_for_ner)):
            f.write("{},{}\n".format(doc, docs_for_ner[doc]).encode("utf-8"))
