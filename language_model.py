# -*- coding: utf-8 -*-
import pickle

local_path = "spellcorrection/data/ruwiki/tokens.txt"
from basic_functions import _read_file
from cut_data import _check
from nltk import word_tokenize
from nltk.util import ngrams
from collections import Counter

def _all_ngrams_types(tokens):
    bigrams = Counter(ngrams(tokens, 2))
    trigrams = Counter(ngrams(tokens, 3))
    fourgrams = Counter(ngrams(tokens, 4))
    fivegrams = Counter(ngrams(tokens, 5))
    return bigrams, trigrams, fourgrams, fivegrams


def set_ngrams():
    text = _read_file(local_path)
    tokens = word_tokenize(text)
    new_tokens = []
    for token in tokens:
        if _check(token):
            new_tokens.append(token.lower())
    bigrams, trigrams, fourgrams, fivegrams = _all_ngrams_types(new_tokens)
    with open("ngrams/bigrams_f.pickle", "wb") as bigrams_f:
        pickle.dump(bigrams, bigrams_f)
    with open("ngrams/trigrams_f.pickle", "wb") as trigrams_f:
        pickle.dump(trigrams, trigrams_f)
    #with open("ngrams/fourgrams_f.pickle", "wb") as fourgrams_f:
    #    pickle.dump(fourgrams, fourgrams_f)
    #with open("ngrams/fivegrams_f.pickle", "wb") as fivegrams_f:
    #    pickle.dump(fivegrams, fivegrams_f)

def get_bigrams():
    with open("ngrams/bigrams_f.pickle", "rb") as bigrams_f:
        bigrams = pickle.load(bigrams_f)
    return bigrams
