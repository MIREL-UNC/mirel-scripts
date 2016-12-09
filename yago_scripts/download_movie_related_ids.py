"""Script to download wikipedia pages urls from YAGO using SPARQL.

The result is going to be stored in a file relation.pickle inside the
directory name provided. If there is no directory name, ../data will be used
as default. The type of each related entity is saved.

Usage:
    download_movie_related_ids.py <relation> <limit> [<offset>] [<directory_name>]
"""
import os
import utils

from collections import defaultdict
from docopt import docopt
from SPARQLWrapper import SPARQLWrapper, JSON


MOVIE_CATEGORY_NAME = "wordnet_movie_106613686"


def main(relation, limit, offset, directory_name):
    """Main script function."""

    utils.safe_mkdir(directory_name)

    query = """SELECT DISTINCT ?related ?wikiPage WHERE {
        ?movie rdf:type <http://yago-knowledge.org/resource/%s> .
        ?related <http://yago-knowledge.org/resource/%s> ?movie .
        ?related <http://yago-knowledge.org/resource/hasWikipediaUrl> ?wikiPage
        } LIMIT %s OFFSET %s""" % (MOVIE_CATEGORY_NAME, relation, limit, offset)
    response = utils.query_sparql(query, utils.YAGO_ENPOINT_URL)
    print 'Reading {} objects.'.format(len(response))
    filename = '{}-{}.pickle'.format(relation, offset)
    utils.pickle_to_file(response, os.path.join(directory_name, filename))


if __name__ == '__main__':
    args = docopt(__doc__, version=1.0)
    directory_name = args['<directory_name>']
    if not directory_name:
        directory_name = '../data/'
    offset = args['<offset>']
    if not offset:
        offset = '0'
    main(args['<relation>'], args['<limit>'], offset, directory_name)
