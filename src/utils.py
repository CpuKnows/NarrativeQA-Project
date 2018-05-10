import codecs
import os
import tensorflow as tf


def create_vocab_file_from_glove(embed_file, vocab_output_file):
    vocab = ['UNK', 'SOS', 'EOS']
    with codecs.open(embed_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f.readlines():
            row = line.strip().split(' ')
            vocab.append(row[0])

    with open(vocab_output_file, 'w') as f:
        for word in vocab:
            f.write('{}\n'.format(word))
    return vocab


def load_embed_txt(embed_file='../../data/glove.6B.50d.txt'):
    emb_dict = dict()
    emb_size = None
    with codecs.getreader('utf-8')(tf.gfile.GFile(embed_file, 'rb')) as f:
        for line in f:
            tokens = line.strip().split(" ")
            word = tokens[0]
            vec = list(map(float, tokens[1:]))
            emb_dict[word] = vec
            if emb_size:
                assert emb_size == len(vec), "All embedding size should be same."
            else:
                emb_size = len(vec)
    return emb_dict, emb_size
