"""Script to get t-sne vectors from gensim Word2Vec trained model.

Usage:
    tsne_vectors.py <model_filepath> <output_filename> [--gensim_save] [--sample_size=<N>]

Options:
    --sample_size=<N>   If N>0, selects N ramdom vectors from model. [default: 0]
    --gensim_save       Reads the model from gensim generic format.
"""

import docopt
import gensim
import logging
logging.basicConfig()
import numpy
import random
import re

from sklearn.manifold import TSNE


def read_arguments(doc):
    """Reads the arguments values from stdin."""
    raw_arguments = docopt.docopt(doc)
    arguments = {re.sub(r'[-,<,>,]', '', key): value
                 for key, value in raw_arguments.iteritems()}
    return arguments


def get_vectors_from_model(w2v_model, sample_size):
    """Return a numpy array of size sample_size with randomly selected vectors.
    """
    vectors = []
    if sample_size > 0:
        words = random.sample(w2v_model.index2word, k=sample_size)
    else:
        words = w2v_model
    for word in words:
        vectors.append(w2v_model[word])
    return numpy.vstack(vectors)


def main():
    """Main function of script."""
    arguments = read_arguments(__doc__)
    logger = logging.getLogger('tsne_vectors')
    logger.setLevel(logging.INFO)

    logger.info('Reading model')
    if arguments['gensim_save']:
        w2v_model = gensim.utils.SaveLoad.load(arguments['model_filepath'])
    else:
        w2v_model = gensim.models.Word2Vec.load_word2vec_format(
            arguments['model_filepath'], binary=True)
    # Read vectors
    logger.info('Selecting vectors')
    vectors = get_vectors_from_model(w2v_model, int(arguments['sample_size']))

    # Train TSNE
    logger.info('Computing t-sne tranformation')
    tsne_model = TSNE(n_components=2)
    numpy.set_printoptions(suppress=True)
    tsne_model.fit_transform(vectors)

    # Save resulting vectors
    logger.info('Saving output')
    with open(arguments['output_filename'], 'w') as output_file:
        numpy.save(output_file, vectors)


if __name__ == '__main__':
    main()
