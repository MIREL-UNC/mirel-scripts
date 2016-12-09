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

from collections import defaultdict
from docopt import docopt
from tqdm import tqdm


def get_graph(graph_filename, category_filename):
    if graph_filename and os.path.isfile(graph_filename):
        print 'Reading pickled graph'
        hierarchy_graph = utils.pickle_from_file(graph_filename)
    else:
        hierarchy_graph = networkx.DiGraph()
        categories = utils.get_categories_from_file(category_filename)
        print 'Downloading categories'
        for category_name in tqdm(categories):
            utils.add_subcategories(category_name, hierarchy_graph)
        if graph_filename:
            print 'Saving graph'
            utils.pickle_to_file(hierarchy_graph, category_filename)
    return hierarchy_graph


def save_entities(category_name, entities, directory_name):
    filename = '{}.pickle'.format(category_name)
    utils.pickle_to_file(entities, os.path.join(directory_name, filename))


def get_descendants(graph, category_name):
    """Gets a list with the recursive descendants of category_name"""
    descendants = set()
    for child in graph.successors(category_name):
        descendants.add(child)
        descendants.update(get_descendants(graph, child))
    return descendants


def main(category_filename, limit, directory_name, graph_filename):
    """Main script function."""
    utils.safe_mkdir(directory_name)
    hierarchy_graph = get_graph(graph_filename, category_filename)
    sorted_categories = networkx.topological_sort(hierarchy_graph, reverse=True)

    # Keep track of the entities in the category's children
    seen_entities = defaultdict(set)
    final_counts = {}
    for category_name in tqdm(sorted_categories):
        results = utils.download_category(category_name, limit)[1:]
        filtered_results = set([entity[0] for entity in results])
        for child in get_descendants(hierarchy_graph, category_name):
            filtered_results = filtered_results.difference(seen_entities[child])
        seen_entities[category_name] = filtered_results
        if len(filtered_results):
            save_entities(
                category_name, [x for x in results if x[0] in filtered_results],
                directory_name)
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

