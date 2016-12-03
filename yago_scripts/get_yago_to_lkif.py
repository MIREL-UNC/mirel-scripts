"""Build the yago to lkif mapping using lkif_to_yago mapping and the
yago hierarchy graph.


Usage:
    get_yago_to_lkif.py <mapping_filename> <graph_filename> <output_file>
"""

import utils

from collections import defaultdict
from docopt import docopt


def get_oldest_ancestors(node, graph):
    """Returns the oldest ancestor (without ancestors) of node in graph."""
    # Base case
    ancestors = graph.predecessors(node)
    if not len(ancestors):
        return [node]
    # Recursive case
    result = []
    for parent in ancestors:
        result.extend(get_oldest_ancestor(parent, graph))
    return result


def invert_mapping(mapping):
    """Returns a new mapping from values to keys.

    If values is a list, a new key is created for each element."""
    new_map = defaultdict(set)
    for key, values in mapping.iteritems():
        for value in values:
            new_map[value].add(key)
    return new_map


def main():
    args = docopt(__doc__, version=1.0)
    mapping = utils.pickle_from_file(args['<mapping_filename>'])
    graph = utils.pickle_from_file(args['<graph_filename>'])

    yago_to_lkif = invert_mapping(mapping)

    for node in graph.nodes():
        if len(yago_to_lkif[node]) != 0:
            continue
        for ancestor in get_oldest_ancestors(node, graph):
            yago_to_lkif[node].update(yago_to_lkif[ancestor])

    utils.pickle_to_file(dict(yago_to_lkif), args['<output_file>'])


if __name__ == '__main__':
    main()
