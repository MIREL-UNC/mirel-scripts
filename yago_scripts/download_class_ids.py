"""Script to download wikipedia pages urls from YAGO using SPARQL.

The category_filename has one category and offset per line separated by a space.

The result is going to be stored in a file category_name.pickle inside the
directory name provided. If there is no directory name, ../data will be used
as default.

Usage:
    dowload_class_ids.py <category_filename> <limit> [<directory_name>]
"""
import os

import utils

from collections import defaultdict
from docopt import docopt
from tqdm import tqdm


def download_category(category_name, limit, offset, directory_name):
    """Downloads a single category and stores result in directory_name."""
    query = """SELECT DISTINCT ?entity ?wikiPage WHERE {
        ?entity rdf:type <http://yago-knowledge.org/resource/%s> .
        ?entity <http://yago-knowledge.org/resource/hasWikipediaUrl> ?wikiPage
        } LIMIT %s OFFSET %s""" % (category_name, limit, offset)
    response = utils.query_sparql(query, utils.YAGO_ENPOINT_URL)
    filename = '{}-{}.pickle'.format(category_name, offset)
    utils.pickle_to_file(response, os.path.join(directory_name, filename))
    return (category_name, len(response) - 1)


def main(category_filename, limit, directory_name):
    """Main script function."""
    utils.safe_mkdir(directory_name)
    subcategories = defaultdict(list)
    levels = defaultdict(int)
    with open(category_filename, 'r') as input_file:
        lines = input_file.read().split('\n')
    print 'Downloading subcategories'
    for line in tqdm(lines):
        splitted_line = line.split(' ')
        if len(splitted_line) == 1:
            category_name, offset = splitted_line[0], 0
        elif len(splitted_line) == 2:
            category_name, offset = splitted_line
        else:
            print 'Error in line {}'.format(line)
        utils.get_subcategories(category_name, subcategories, levels)

    results = []
    # Download only categories without children
    for category_name, children in subcategories.iteritems():
        if len(children):
            continue
        results.append(
            download_category(category_name, limit, offset, directory_name))
    for category_name, total in results:
        print '{} {}'.format(category_name, total)


if __name__ == '__main__':
    args = docopt(__doc__, version=1.0)
    directory_name = args['<directory_name>']
    if not directory_name:
        directory_name = '../../data/'
    main(args['<category_filename>'], args['<limit>'], directory_name)

