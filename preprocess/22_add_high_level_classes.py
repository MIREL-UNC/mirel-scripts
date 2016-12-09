"""Add the high level classes (person/organization/etc.) to a label file."""

import argparse
import pickle

from tqdm import tqdm


def read_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--labels_file',
                        type=unicode,
                        help='Pickled file with a list of labels')
    parser.add_argument('--mapping_file',
                        type=unicode,
                        help='Pickled file with the mapping from yago labels'
                             'to high level labels')

    return parser.parse_args()


def pickle_from_file(filename):
    with open(filename, 'r') as input_file:
        result = pickle.load(input_file)
    return result


def main():
    args = read_arguments()
    labels = pickle_from_file(args.labels_file)
    mapping = pickle_from_file(args.mapping_file)

    for index, label in tqdm(enumerate(labels)):
        assert len(labels) == 5
        if label[0].startswith('O'):
            continue
        yago_category = label[1]
        if not yago_category in mapping:
            print 'Error, unknown yago category {}'.format(yago_category)
            continue
        label[4] = mapping[yago_category]

    # Save results
    # with open(args.labels_file, 'w') as output_file:
    #     pickle.dump(labels, output_file)


if __name__ == '__main__':
    main()