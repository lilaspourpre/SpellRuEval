# -*- coding: utf-8 -*-
#! python3


import re
alphabet = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЫЪЬЭЮЯфбвгдеёжзийклмнопрстуфхцчшщъыьэюя '


def _read_file_lines(path):
    with open(path, 'r', encoding='utf-8') as file:
        data = file.read().split("\n")
        return data

def _split_lines(lines, separator=" "):
    return dict([(line.split(separator)[0], int(line.split(separator)[1])) for line in lines])


def get_edits1(word):
    splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes    = [a + b[1:] for a, b in splits if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
    replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
    inserts    = [a + c + b     for a, b in splits for c in alphabet]
    return set(deletes + transposes + replaces + inserts)

def _count_max_prob(candidates, d, ngrams, prev_word=None):
    if prev_word:
        max_prob = 0
        max_cand = None
        for candidate in candidates:
            bi_prob = int(ngrams[(prev_word,candidate)])/len(ngrams)
            full_prob = int(d[prev_word])/len(d)
            con_prob = bi_prob/full_prob
            if con_prob > max_prob:
                max_prob = con_prob
                max_cand = candidate
        return max_cand
    else:
        return max(candidates, key=d.get)

def get_most_likely(word, d, ngrams, prev_word):
    candidates = []
    if word not in d:
        for w in get_edits1(word):
            if w in d:
                candidates.append(w)
        if not candidates:
            return word, 0
        cand = _count_max_prob(candidates, d, ngrams, prev_word)
        if cand:
            return cand, d[cand]
        return word, 0
    else:
        return word, d[word]
