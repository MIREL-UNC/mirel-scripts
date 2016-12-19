"""Download labels from list of entities uris.

Usage:
    download_entity_labels.py <source_filename> <output_filename>
"""
import pickle
import utils

from docopt import docopt
from tqdm import tqdm


def get_labels(uri):
    query = """SELECT DISTINCT ?label WHERE {
        <%s%s> rdfs:label ?label .
        filter(lang(?label) = 'eng')
    }""" % (utils.RESOURCE_PREFIX, uri)
    result = utils.query_sparql(query, utils.YAGO_ENPOINT_URL)
    return [x[0] for x in result[1:]]


def main(source_filename, output_filename):

    entities = utils.pickle_from_file(source_filename)
    labels = {}
    for uri in tqdm(entities):
        uri = uri[2:]
        labels[uri] = get_labels(uri)
    utils.pickle_to_file(labels, output_filename)


if __name__ == '__main__':
    args = docopt(__doc__, version=1.0)
    main(args['<source_filename>'], args['<output_filename>'])