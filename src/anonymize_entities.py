# Author: John Maxwell
# Date: 2018-03-30
# TLDR: Simple heuristic to anonymize entities
# =============================================================================
import codecs
import string
import sys
import numpy as np
import pandas as pd
from spacy.lang.en import English
from spacy.tokens import Doc, Span, Token
from tqdm import tqdm


class SimpleEntityAnonymizer(object):
    """Spacy pipeline component. Used to to replace entities with anonymized tokens.
    If a word is capitalized and doesn't appear in lowercase elsewhere in the text anonymize it."""

    name = 'entity_anonymizer'

    def __init__(self, nlp, attr='entity_id'):
        Token.set_extension(attr, default=None)

    def __call__(self, doc):
        upper = set()
        lower = set()
        entity_map = dict()

        for token in doc:
            if token.text[0] in string.ascii_uppercase:
                upper.add(token.text)
            else:
                lower.add(token.text)

        entities = [token for token in upper if token.lower() not in lower]
        entity_ids = np.random.choice(len(entities), len(entities)).tolist()
        
        for token in doc:
            if token.text in entities:
                if token.text not in entity_map.keys():
                    entity_map[token.text] = '@entity' + str(entity_ids.pop())
                token._.set('entity_id', entity_map[token.text])
                
        return doc


def entity_doc_to_text(doc):
    """Prints out text with anonymized tokens.

    :param doc: spacy doc object
    :return: anonymized text
    """
    # spacy issue #2073
    # if not doc[0].has_extension('entity_id'):
    #     print('Tokens don\'t have attribute: entity_id')
    #     return None
    
    text = ''
    for token in doc:
        if token._.entity_id is not None:
            whitespace = token.text_with_ws[len(token.text):]
            text += token._.entity_id + whitespace
        else:
            text += token.text_with_ws
    return text


if __name__ == '__main__':
    doc_dir = '../data/clean/'
    output_dir = '../data/anonymized_entities/'

    nlp = English()
    component = SimpleEntityAnonymizer(nlp)
    nlp.add_pipe(component, last=True)

    docs = pd.read_csv('../data/documents.csv')
    for doc_id in tqdm(docs['document_id'], total=len(docs['document_id'])):
        # sys.stdout.write('\rProcessing doc: {}'.format(doc_id))
        # sys.stdout.flush()
        # print('Processing doc:', doc_id)

        with codecs.open(doc_dir + doc_id + '-clean.content', 'r',encoding='utf-8', errors='ignore') as f:
            doc = nlp(f.read())
        
        new_text = entity_doc_to_text(doc)
        
        with codecs.open(output_dir + doc_id + '-clean.content', 'w',encoding='utf-8', errors='ignore') as f:
            f.write(new_text)
