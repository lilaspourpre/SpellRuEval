# -*- coding: utf-8 -*-
#! python3
import re
alphabet = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЫЪЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя- '


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

def count_max_prob(candidates, d, ngrams, prev_word=None, next_word=None):
    if prev_word:
        max_prob = 0
        max_cand = None
        for candidate in candidates:
            bi_prob = int(ngrams[(prev_word, candidate)])/len(ngrams)
            full_prob = int(d[prev_word])/len(d)
            if full_prob > 0:
                con_prob = bi_prob/full_prob
            else:
                con_prob = 0
            if con_prob > max_prob:
                max_prob = con_prob
                max_cand = candidate
        return max_cand
    else:
        return max(candidates, key=d.get)


def _get_candidates_dict(d, edits):
    candidates = []
    for w in edits:
        if w in d:
            candidates.append(w)
    return candidates

def _check_in_morpho(word, edits, morpho):
    for edit in edits:
        res = morpho(edit.lower())
        if res:
            return res, 5
    return word, 0

def _sort_by_count(cands):
    return cands[1]

def get_most_likely(word, d, ngrams, nltk_dict, prev_word=None, next_word=None, flag=True):
    edits = get_edits1(word)
    candidates = _get_candidates_dict(nltk_dict, edits)
    if candidates != []:
        try:
            cand = count_max_prob(candidates, nltk_dict, ngrams, prev_word, next_word)
            if not cand:
                cand = count_max_prob(candidates, nltk_dict, ngrams)
        except KeyError:
            cand = count_max_prob(candidates, d, ngrams)
        if cand:
            try:
                return cand, nltk_dict[cand]
            except KeyError:
                return cand, d[cand]
    if flag:
        new_cands = []
        for candidate in edits:
            new_cands.append(get_most_likely(candidate, d, ngrams, nltk_dict, prev_word, next_word, flag=False))
        if new_cands != []:
            result = sorted(new_cands, key=_sort_by_count, reverse=True)[0]
            return result[0], result[1]
    return word, 0
