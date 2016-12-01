"""Script to transform the yago downloads to label file for annotation.

The output format is:

{
    "labels": {yago_class: color, ...},
    "YAGO uri": [yago_label1, yago_label2, ...]
}

Usage:
    get_annotation_labels.py <directory_name> <output_file>
"""

import json
import os
import utils
from docopt import docopt


def get_entity_clean_name(entity):
    return entity.split('/')[-1].encode('utf-8')


def main(directory_name, output_file):
    """Main script function."""
    labels = {
        'labels': {},
        'YAGO uri': []
    }
    for filename in utils.get_input_files(directory_name, r'.*pickle'):
        class_name = os.path.basename(filename).split('.pickle')[0]
        entities = utils.pickle_from_file(filename)
        labels['labels'][class_name] = 'lightcoralLabel'
        labels['YAGO uri'].extend([get_entity_clean_name(entity[0])
                                   for entity in entities[1:]])
    with open(output_file, 'w') as out_file:
        json.dump(labels, out_file, ensure_ascii=False)


if __name__ == '__main__':
    args = docopt(__doc__, version=1.0)
    main(args['<directory_name>'], args['<output_file>'])
