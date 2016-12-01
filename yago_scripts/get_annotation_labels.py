"""Script to transform the yago downloads to label file for annotation.

The output format is:

{
    "labels": {yago_class: color, ...},
    "YAGO uri": [yago_label1, yago_label2, ...]
}

Usage:
    get_annotation_labels.py <category_filename> <output_file>
"""

import json
import os
import utils
from docopt import docopt
from tqdm import tqdm


def get_entity_clean_name(entity):
    return entity.split('/')[-1].encode('utf-8')


def get_all_entities(category):
    query = """SELECT DISTINCT ?entity WHERE {
            ?entity rdf:type <%s> .
        }""" % (category, )
    return utils.query_sparql(query, utils.YAGO_ENPOINT_URL)[1:]


def main(category_filename, output_file):
    """Main script function."""
    labels = {
        'labels': {},
        'YAGO uri': []
    }
    categories = set()
    print 'Getting subclasses'
    for category in tqdm(utils.get_categories_from_file(category_filename)):
        categories.add(utils.RESOURCE_PREFIX + category)
        subclasses = [
            x[0] for x in utils.query_subclasses(category, populated=False)
            if 'wikicat' not in x[0]]
        categories.update(subclasses)
    entities = set()
    print 'Downloading entities'
    for category in tqdm(categories):
        labels['labels'][category] = 'lightcoralLabel'
        category_entities = [get_entity_clean_name(entity[0])
                             for entity in get_all_entities(category)]
        print category, len(category_entities)
        entities.update(category_entities)
    labels['YAGO uri'] = list(entities)
    with open(output_file, 'w') as out_file:
        json.dump(labels, out_file, ensure_ascii=False)


if __name__ == '__main__':
    args = docopt(__doc__, version=1.0)
    main(args['<category_filename>'], args['<output_file>'])
