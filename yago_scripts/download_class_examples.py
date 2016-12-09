"""Script to download examples of classes from YAGO using SPARQL.

The result is going to be printed on the stdin.

Usage:
    download_class_examples.py <input_filename> <limit> <output_filename>
"""

import urlparse
import wikipedia
import utils

from docopt import docopt
from SPARQLWrapper import SPARQLWrapper, JSON


def make_query(category_name, limit):
    """Sends query to SPARQL backend and returns the response."""
    result = {}
    query = """SELECT DISTINCT ?entity ?wikiPage ?label WHERE {
        ?entity rdf:type <http://yago-knowledge.org/resource/%s> .
        ?entity <http://yago-knowledge.org/resource/hasWikipediaUrl> ?wikiPage .
        ?entity rdfs:label ?label. FILTER (lang(?label) = 'eng')
        } LIMIT %s""" % (category_name, limit*10)
    response = utils.query_sparql(query, utils.YAGO_ENPOINT_URL)
    for example in response[1:]:  # Ignore first element
        if example[0] in result:
            continue
        entity_name = urlparse.unquote(example[1].split('/')[-1])
        try:
            summary = wikipedia.summary(entity_name, sentences=6)
        except (wikipedia.exceptions.PageError,
                wikipedia.exceptions.DisambiguationError):
            # print u'Page for entity {} not found.'.format(entity_name)
            continue
        result[example[0]] = ({
            'yago_url': example[0],
            'wiki_url': example[1],
            'label': example[2].split('@')[0].replace('"', ''),
            'description': summary
        })
        if len(result) >= int(limit):
            break
    return result


def print_examples(response, output_file):
    """Prints in stdin the formatted example."""
    message = u''
    message += u'Entity name: {label}\n'
    message += u'Yago URL: {yago_url}\n'
    message += u'Wikipedia URL: {wiki_url}\n'
    message += u'Description: {description}\n'
    message += u'\n'
    for example in response.values():
        try:
            output_file.write(message.format(**example).encode("UTF-8"))
        except UnicodeEncodeError:
            # import ipdb; ipdb.set_trace()
            print 'Unicode error for response', response


def main(input_filename, limit, output_filename):
    """Main script function."""
    with open(input_filename, 'r') as input_file, open(output_filename, 'w') as output_file:
        for category_name in input_file:
            category_name = category_name.strip()
            response = make_query(category_name, limit)
            output_file.write('*' * 80 + '\n')
            output_file.write(u'Class name {}\n'.format(category_name))
            print_examples(response, output_file)


if __name__ == '__main__':
    args = docopt(__doc__, version=1.0)
    main(args['<input_filename>'], args['<limit>'], args['<output_filename>'])
