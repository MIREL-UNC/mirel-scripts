"""Auxiliary functions."""

try:
    import cPickle as pickle
except ImportError:
    import pickle
import re
import os

from SPARQLWrapper import SPARQLWrapper, JSON


YAGO_ENPOINT_URL = "https://linkeddata1.calcul.u-psud.fr/sparql"
RESOURCE_PREFIX = 'http://yago-knowledge.org/resource/'


def safe_mkdir(dir_name):
    """Checks if a directory exists, and if it doesn't, creates one."""
    try:
        os.stat(dir_name)
    except OSError:
        os.mkdir(dir_name)


def pickle_to_file(object_, filename):
    """Abstraction to pickle object with the same protocol always."""
    with open(filename, 'wb') as file_:
        pickle.dump(object_, file_, pickle.HIGHEST_PROTOCOL)


def pickle_from_file(filename):
    """Abstraction to read pickle file with the same protocol always."""
    with open(filename, 'rb') as file_:
        return pickle.load(file_)


def get_input_files(input_dirpath, pattern):
    """Returns the names of the files in input_dirpath that matches pattern."""
    all_files = os.listdir(input_dirpath)
    for filename in all_files:
        if re.match(pattern, filename) and os.path.isfile(os.path.join(
                input_dirpath, filename)):
            yield os.path.join(input_dirpath, filename)


# TODO(mili): Is is better a pandas DataFrame
def query_sparql(query, endpoint):
    """Run a query again an SPARQL endpoint.

    Returns:
        A double list with only the values of each requested variable in
        the query. The first row in the result contains the name of the
        variables.
    """
    sparql = SPARQLWrapper(endpoint)
    sparql.setReturnFormat(JSON)

    sparql.setQuery(query)
    response = sparql.query().convert()
    bindings = response['results']['bindings']
    variables = response['head']['vars']
    result = [variables]
    for binding in bindings:
        row = []
        for variable in variables:
            row.append(binding[variable]['value'])
        result.append(row)
    return result


def download_category(category_name, limit):
    """Downloads a single category and stores result in directory_name."""
    query = """SELECT DISTINCT ?entity ?wikiPage WHERE {
        ?entity rdf:type <http://yago-knowledge.org/resource/%s> .
        ?entity <http://yago-knowledge.org/resource/hasWikipediaUrl> ?wikiPage
        } LIMIT %s""" % (category_name, limit)
    return query_sparql(query, YAGO_ENPOINT_URL)


def get_categories_from_file(category_filename):
    """Read categories and ofsets"""
    with open(category_filename, 'r') as input_file:
        lines = input_file.read().split('\n')
    return lines


def query_subclasses(category_name, populated=True):
    query = """SELECT DISTINCT ?subCategory WHERE {
        ?subCategory rdfs:subClassOf <%s%s> .
        """ % (RESOURCE_PREFIX, category_name)
    if populated:
        query += """
        ?entity rdf:type ?subCategory .
        }"""
    else:
        query += '}'
    return query_sparql(query, YAGO_ENPOINT_URL)[1:]


def add_subcategories(category_name, graph, ancestors=[]):
    """Updates the children categories and level of category name.
    """
    def add_ancestor(category_name):
        graph.add_edge(ancestors[-1], category_name, path_len=len(ancestors))
    response = query_subclasses(category_name)

    for result in response:
        child_category = result[0].replace(RESOURCE_PREFIX, '')
        if 'wikicat' in child_category:
            continue
        add_subcategories(child_category, graph,
                          ancestors=ancestors + [category_name])

    if category_name not in graph:
        if len(ancestors):
            add_ancestor(category_name)
        else:
            graph.add_node(category_name)
        return

    # We have seen the node before
    if len(graph.predecessors(category_name)) == 0:  # There is no ancestor yet.
        if len(ancestors):  # it's not the first recursive call
            add_ancestor(category_name)
    else:  # There is a previous ancestor
        added = False
        for prev_ancestor in graph.predecessors(category_name):
            if prev_ancestor in ancestors:
                added = True
                if len(ancestors) > graph.get_edge_data(
                        prev_ancestor, category_name)['path_len']:
                    # The current ancestor has a longer path
                    graph.remove_edge(prev_ancestor, category_name)
                    add_ancestor(category_name)
        # The new ancestor doesn't overlap with any previous ancestor's path.
        if not added and len(ancestors):
            add_ancestor(category_name)
