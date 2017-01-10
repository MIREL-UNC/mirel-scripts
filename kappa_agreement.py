"""Script to calculate the kappa agreement in conll documents for all labels.

Each document is expected to have the same format used for processing:
sentence_number token   PoS yago_uri    wordnet_tag   lkif_tag  entity_tag

The files must be aligned. The tokens must be the same for every line.
"""
import argparse
import numpy
import pandas
from sklearn.metrics import cohen_kappa_score, confusion_matrix


def read_arguments():
    """Parses the arguments from the stdin and returns an object."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--f1', type=str,
                        help='Path the first file to read')
    parser.add_argument('--f2', type=str,
                        help='Path the second file to read')
    return parser.parse_args()

def main():
    args = read_arguments()
    label_levels = ['yago_uri', 'wordnet_class', 'lkif_class', 'entity_class']
    columns = ['index', 'token', 'PoS'] + label_levels
    file1 = pandas.read_csv(args.f1, delimiter='\t', header=None, names=columns)
    file2 = pandas.read_csv(args.f2, delimiter='\t', header=None, names=columns)

    # Replace B and I labels
    for level in label_levels:
        file1[level] = file1[level].apply(
            lambda x: x.replace('B-', '').replace('I-', ''))
        file2[level] = file2[level].apply(
            lambda x: x.replace('B-', '').replace('I-', ''))
    concat = pandas.concat((file1, file2))

    for level in label_levels:
        agreement = cohen_kappa_score(file1[level], file2[level])
        print('Agreement on level {}: {:.4f}'.format(level, agreement))

    for level in label_levels:
        print('Labels on level {}: {} {} - Total {}'.format(
            level, numpy.unique(file1[level]).shape[0],
            numpy.unique(file2[level]).shape[0],
            numpy.unique(concat[level]).shape[0]
        ))

    for level in label_levels:
        print('Missing labels for level {}: {} {} - Total {}'.format(
            level, (file1[level] == '').sum(), (file2[level] == '').sum(),
            (concat[level] == '').sum()))

    print('Number of labeled words {} {}'.format(
        (file1[label_levels[-1]] != 'O').sum(),
        (file2[label_levels[-1]] != 'O').sum()))

    print('Confusion matrix. The rows are the file1 annotations, and columns'
          'file 2 annotations.')
    labels = numpy.unique(concat.entity_class)
    cm = confusion_matrix(file1.entity_class, file2.entity_class,
                          labels=labels)
    print('\t', '\t'.join(labels))
    for label, row in zip(labels, cm):
        print(label, '\t', '\t'.join(row.astype(numpy.str)))



if __name__ == '__main__':
    main()