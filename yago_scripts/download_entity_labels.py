"""Download labels from list of entities uris.

Usage:
    download_entity_labels.py <source_filename> <output_filename>
"""
import logging
import pickle
import urllib
import utils

from docopt import docopt
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)


def get_labels(uri):
    query = """SELECT DISTINCT ?label WHERE {
        <%s%s> rdfs:label ?label .
        filter(lang(?label) = 'eng')
    }""" % (utils.RESOURCE_PREFIX, uri)
    result = utils.query_sparql(query, utils.YAGO_ENPOINT_URL)
    return [x[0] for x in result[1:]]


def main(source_filename, output_filename):

    entities = set([uri[2:] for uri in utils.pickle_from_file(source_filename)])
    labels = {}
    for uri in tqdm(entities):
        try:
            labels[uri] = get_labels(uri)
        except urllib.error.HTTPError as error:
            logging.error('Error for uri {}'.format(uri))
            logging.error(error)
            
    utils.pickle_to_file(labels, output_filename)


if __name__ == '__main__':
    args = docopt(__doc__, version=1.0)
    main(args['<source_filename>'], args['<output_filename>'])
