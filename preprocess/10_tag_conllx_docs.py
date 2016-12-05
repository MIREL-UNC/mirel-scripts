#!/usr/bin/env python
# coding: utf-8

"""Add POS tag to files in conll format.

Usage:
    10_tag_conllx_docs.py <input_file> <output_file> <total_lines>

"""

from __future__ import unicode_literals, print_function

import sys
import nltk
from tqdm import tqdm

sentence = []

with open(sys.argv[1], "r") as fi:
    with open(sys.argv[2], "w") as fo:
        for line in tqdm(fi, total=int(sys.argv[3])):
            line = line.decode("utf-8").strip().split()
            if len(line) == 5:
                sentence.append(line)
            elif len(line) == 0:
                # End of sentence
                tags = nltk.pos_tag([w[1] for w in sentence])

                if len(tags) != len(sentence):
                    sentence = []
                    continue

                for index, word in enumerate(sentence):
                    word.insert(2, tags[index][1])

                print("\n".join(
                    ["\t".join(w[:6]) for w in sentence]).encode("utf-8"),
                      end="\n\n", file=fo)
                sentence = []
