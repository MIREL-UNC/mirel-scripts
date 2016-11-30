"""Script to download wikipedia pages urls from YAGO using SPARQL.

The category_filename has one category and offset per line separated by a space.

The result is going to be stored in a file category_name.pickle inside the
directory name provided. If there is no directory name, ../data will be used
as default.

Usage:
    download_class_ids.py <category_filename> <limit> [<directory_name>] [<graph_filename>]
"""
import networkx
import os
import utils

from docopt import docopt
from tqdm import tqdm


def download_category(category_name, limit):
    """Downloads a single category and stores result in directory_name."""
    query = """SELECT DISTINCT ?entity ?wikiPage WHERE {
        ?entity rdf:type <http://yago-knowledge.org/resource/%s> .
        ?entity <http://yago-knowledge.org/resource/hasWikipediaUrl> ?wikiPage
        } LIMIT %s""" % (category_name, limit)
    return utils.query_sparql(query, utils.YAGO_ENPOINT_URL)


def get_categories_from_file(category_filename):
    """Read categories and ofsets"""
    with open(category_filename, 'r') as input_file:
        lines = input_file.read().split('\n')
    return lines


def get_graph(graph_filename, category_filename):
    if graph_filename:
        print 'Reading pickled graph'
        hierarchy_graph = utils.pickle_from_file(graph_filename)
    else:
        hierarchy_graph = networkx.DiGraph()
        categories = get_categories_from_file(category_filename)
        print 'Downloading categories'
        for category_name in tqdm(categories):
            utils.add_subcategories(category_name, hierarchy_graph)
    return hierarchy_graph


def save_entities(category_name, entities, directory_name):
    filename = '{}.pickle'.format(category_name)
    utils.pickle_to_file(entities, os.path.join(directory_name, filename))


def main(category_filename, limit, directory_name, graph_filename):
    """Main script function."""
    utils.safe_mkdir(directory_name)
    hierarchy_graph = get_graph(graph_filename, category_filename)
    sorted_categories = networkx.topological_sort(hierarchy_graph, reverse=True)

    # Download only categories without children
    seen_entities = set()
    final_counts = {}
    for category_name in tqdm(sorted_categories):
        results = download_category(category_name, limit)[1:]
        filtered_results = [entity for entity in results
                            if entity[0] not in seen_entities]
        seen_entities.update([entity[0] for entity in filtered_results])
        if len(filtered_results):
            save_entities(category_name, filtered_results, directory_name)
        final_counts[category_name] = len(filtered_results)

    for category_name, count in final_counts.iteritems():
        print category_name, count



if __name__ == '__main__':
    args = docopt(__doc__, version=1.0)
    directory_name = args['<directory_name>']
    if not directory_name:
        directory_name = '../../data/'
    main(args['<category_filename>'], args['<limit>'], directory_name,
         args['<graph_filename>'])

