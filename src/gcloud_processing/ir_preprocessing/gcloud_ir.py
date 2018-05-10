import argparse
import os

import tensorflow as tf
import pandas as pd
import spacy
import en_core_web_md


if __name__ == "__main__":
    print('Main function')
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", type=str, default=None,
                        help="Questions file")
    parser.add_argument("--docs_dir", type=str, default=None,
                        help="Directory containing documents")
    parser.add_argument("--output_file", type=str, default=None,
                        help="File for storing output")
    parser.add_argument("--top_n", type=int, default=5,
                        help="Number of most similar chunks to keep")
    FLAGS, unparsed = parser.parse_known_args()

    # Spacy
    #nlp = spacy.load('en_core_web_md-2.0.0', disable=["tagger", "parser", "ner"])
    print('Load spacy model')
    nlp = en_core_web_md.load(disable=["tagger", "parser", "ner"])
    nlp.add_pipe(nlp.create_pipe('sentencizer'))

    print('Read questions')
    with tf.gfile.GFile(FLAGS.questions, 'r') as f:
        questions = pd.read_csv(f)

    print('Start processing')

    with tf.gfile.GFile(FLAGS.output_file, 'w') as f:
        prev_doc_id = ''
        
        for index, row in questions.iterrows():
            if index % 100 == 0:
                print('processing record:', index)

            doc_id, q, a = row['document_id'], row['question'], row['answer1']
            doc_q = nlp(q)

            if prev_doc_id != doc_id:
                with tf.gfile.GFile(os.path.join(FLAGS.docs_dir, doc_id+'-clean.content'), 'r') as g:
                    doc = nlp(g.read()[:999999])
                prev_doc_id = doc_id

            sent_rank = list()
            for i,sent in enumerate(doc.sents):
                sent_rank.append((i, sent.similarity(doc_q), sent.text.strip()))
                
            sent_rank.sort(key=lambda tup: tup[1], reverse=True)
            sent_rank = sent_rank[:FLAGS.top_n]
            sent_rank.sort(key=lambda tup: tup[0])

            ir_chunks = [sent for i, similarity, sent in sent_rank]
            ir_output = '<del>'.join(ir_chunks)
            ir_output += '</c>'
            f.write("{}\n".format(ir_output))
