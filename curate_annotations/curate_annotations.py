"""Script to sanitize labels and convert annotations to the classifier format.
"""
import argparse
import json
import logging
import nltk
import os
import pandas
import utils

logging.basicConfig(level=logging.INFO)

DEFAULT_LABEL = 'O'


def read_arguments():
    """Parses the arguments from the stdin and returns an object."""
    parser = argparse.ArgumentParser()
    parser.add_argument('annotated_documents', type=str,
                        help='Path of directory with the annotated files')
    parser.add_argument('--output_directory', type=str,
                        help='Path of directory to save the files')
    parser.add_argument('--mapping_filename', type=str,
                        help='Filename to read the mappings.')
    parser.add_argument('--update_mappings', action='store_true',
                        help='Add new labels found to mapping.')
    return parser.parse_args()


def add_columns(annotation):
    new_column_index = []
    new_column_pos = []
    sentence_count = 0
    sentence = []
    for row in annotation.iterrows():
        if pandas.isnull(row[1]['labels']):
            new_column_pos += [x[1] for x in nltk.pos_tag(sentence)]
            new_column_pos.append(pandas.np.nan)
            sentence = []
            new_column_index.append(pandas.np.nan)
        else:
            new_column_index.append(len(sentence))
            sentence.append(row[1]['tokens'])

    annotation['sentence_index'] = new_column_index
    annotation['pos_tag'] = new_column_pos


def separate_labels(annotation):
    """Adds columns with raw lkif and yago uri labels"""
    def split_function(row):
        if row == DEFAULT_LABEL:
            return pandas.Series([DEFAULT_LABEL] * 3)
        uri, lkif = row.split('##')
        ner_tag = uri[0]
        return pandas.Series([ner_tag, uri, ner_tag + '-' + lkif])

    annotation[['ner_tag', 'uri_tag', 'lkif_tag']] = annotation['labels'].apply(
        split_function)


def apply_mappings(annotation, mappings):
    """Replace labels according to mappings."""
    def get_or_update_label(mapping_key, label_name, row):
        original_label = row[label_name]
        if original_label not in mappings[mapping_key]:
            # Add missing label
            mappings[mapping_key][original_label] = None
        if mappings[mapping_key][original_label] is not None:
            return mappings[mapping_key][original_label]
        return original_label
        
    def apply_function(row):
        if row['lkif_tag'] == DEFAULT_LABEL:
            return pandas.Series([DEFAULT_LABEL] * 3)
        new_row = []
        new_row.append(get_or_update_label('lkif', 'lkif_tag', row))
        new_row.append(get_or_update_label('uri', 'uri_tag', row))
        new_row.append(get_or_update_label('yago', 'lkif_tag', row))
        
        return pandas.Series(new_row)
    annotation[['lkif_tag', 'uri_tag', 'yago_tag']] = annotation[
        ['lkif_tag', 'uri_tag']].apply(apply_function, axis=1)


def write_file(filename, annotation):
    """Writes annotation to filename"""
    columns = ['sentence_index', 'tokens', 'pos_tag', 'ner_tag',
               'lkif_tag', 'uri_tag']
    annotation.to_csv(filename, sep='\t',
                      columns=columns, index=None, header=False) 


def process_directory(directory_name, output_directory, mappings):
    for filename in utils.get_input_files(directory_name, r'.*\.conll'):
        logging.info('Processing file {}'.format(filename))
        annotation = pandas.read_csv(
            filename, sep='\t', header=None, skip_blank_lines=False,
            usecols=[0, 5], names=['labels', 'tokens'])
        add_columns(annotation)
        annotation.dropna(how='all', inplace=True)
        separate_labels(annotation)
        apply_mappings(annotation, mappings)
        output_filename = os.path.join(
            output_directory, os.path.basename(filename))
        write_file(output_filename, annotation)


def main():
    args = read_arguments()
    try:
        with open(args.mapping_filename, 'r') as mapfile:
            mappings = json.load(mapfile)
    except (TypeError, FileNotFoundError):
        mappings = {
            'lkif': {},
            'yago': {},
            'uri': {}
        }
    directories = utils.get_input_directories(args.annotated_documents,
                                              r'.*-annotation-.*')
    for directory in directories:
        output_directory = os.path.join(
            args.output_directory, os.path.basename(directory))
        utils.safe_mkdir(output_directory)
        process_directory(directory, output_directory, mappings)
    if args.update_mappings:
        with open(args.mapping_filename, 'w') as mapfile:
            json.dump(mappings, mapfile)

if __name__ == '__main__':
    main()
