#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import os
import sys
from bs4 import BeautifulSoup
from tqdm import tqdm


if __name__ == "__main__":
    for fname in tqdm(sorted(os.listdir("./corpus"))):
        with open("./corpus/{}".format(fname), "r") as f:
            soup = BeautifulSoup(f, 'html.parser')

        with open("./clean/{}".format(fname), "w") as f:
            print(soup.get_text().encode("utf-8"), file=f)
