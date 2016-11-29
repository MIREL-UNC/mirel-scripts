"""Auxiliary functions."""

import cPickle
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
    file_ = open(filename, 'w')
    cPickle.dump(object_, file_, cPickle.HIGHEST_PROTOCOL)
    file_.close()


def pickle_from_file(filename):
    """Abstraction to read pickle file with the same protocol always."""
    with open(filename, 'r') as file_:
        return cPickle.load(file_)


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


def get_subcategories(category_name, subcategories, levels):
    """Updates the children categories and level of category name.

    Params:
        category_name String
        children Dict map from the category names to a set of its subcategories.
        levels Dict a map from the category to its level. Level 0 means no
            parent (root category), level 1 means only one ancestor in the
            total set of categories, etc.
    """
    # Base case
    if category_name in subcategories:
        return
    # Recursive case
    query = """SELECT DISTINCT ?subCategory WHERE {
        ?subCategory rdfs:subClassOf <%s%s> .
        ?entity rdf:type ?subCategory .
        }""" % (RESOURCE_PREFIX, category_name)
    response = query_sparql(query, YAGO_ENPOINT_URL)
    for result in response[1:]:
        category = result[0].replace(RESOURCE_PREFIX, '')
        if 'wikicat' in category:
            continue
        subcategories[category_name].append(category)
        levels[category] = levels[category_name] + 1
        subcategories[category] = []
        get_subcategories(category, subcategories, levels)

