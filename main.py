# -*- coding: utf-8 -*-
import re
from collections import Counter

from edit_distance import get_most_likely
from language_model import get_bigrams
from basic_functions import _get_data_from_cmd
from basic_functions import _read_file_lines
from parse_rules import _get_exps
from parse_rules import *
from pymorphy2 import MorphAnalyzer

numbers = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0")
punctuation = (',', '.', '?', '!', ':', '-', '—', ";", '«', '»', "...", "(", ")", "``", "--")


def _try_spaces(word, dictionary, flag=True):
    splits = [(word[:i], word[i:]) for i in range(1, len(word) + 1)]
    for split in splits:
        try:
            a, b = dictionary[split[0]], dictionary[split[1]]
            if len(split[0]) > 3 and len(split[1]) > 3:
                return " ".join(split), dictionary[split[0]]
            elif int(a) > 5 and int(b) > 5:
                return " ".join(split), dictionary[split[0]]
        except KeyError as e:
            pass

    for split in splits:
        smaller_splits0 = [(split[0][:i], split[0][i:]) for i in range(1, len(split[0]) + 1)]
        for smsp0 in smaller_splits0:
            try:
                a, b, c = dictionary[smsp0[0]], dictionary[smsp0[1]], dictionary[split[1]]
                if int(a) > 15 and int(b) > 15 and int(c) > 15:
                    return " ".join(smsp0) + " " + split[1], dictionary[split[1]]
            except KeyError as e:
                pass

    for split in splits:
        smaller_splits1 = [(split[1][:i], split[1][i:]) for i in range(1, len(split[1]) + 1)]
        for smsp1 in smaller_splits1:
            try:
                a, b, c = dictionary[smsp1[0]], dictionary[smsp1[1]], dictionary[split[0]]
                if int(a) > 15 and int(b) > 15 and int(c) > 15:
                    return split[0] + " " + " ".join(smsp1), dictionary[split[0]]
            except KeyError as e:
                pass
    return word, 0


def _find_ruled_word(word, dictionary, rules):
    for rule in rules:
        if rule in word:
            result, count = _check_in_dictionary(word.replace(rule, rules[rule]), dictionary)
            if count > 0:
                return result
            else:
                pass
    return False


def _check_in_rules(word, dictionary, rules):
    try:
        ruled_word = _find_ruled_word(word, dictionary, rules)
        return ruled_word
    except KeyError:
        return False


def _check_in_slang(word, slang):
    try:
        slang_word = slang[word]
        return slang_word
    except KeyError as e:
        return False


def _check_with_morphology(word):
    w = MorphAnalyzer().word_is_known(word.lower())
    if w:
        return word
    return False


def _check_in_dictionary(word, dictionary):
    try:
        return word, dictionary[word]
    except KeyError:
        return False, 0


def _check_in_dictionary_all_variants(word, dictionary):
    w, p = _check_in_dictionary(word, dictionary)
    w_l, p_l = _check_in_dictionary(word.lower(), dictionary)
    w_u, p_u = _check_in_dictionary(word.upper(), dictionary)
    w_c, p_c = _check_in_dictionary(word.capitalize(), dictionary)
    words = [w, w_l, w_u, w_c]
    probs = [p, p_l, p_u, p_c]
    return words[probs.index(max(probs))]


def _check_letters(word, dictionary):
    counts = Counter(word)
    options = []
    for count in counts:
        if counts[count] > 1:
            options.append(count * counts[count])
    for option in options:
        if option in word:
            new_w = word.replace(option, option[0])
            try:
                a = dictionary[new_w]
                return new_w
            except KeyError:
                pass
    return False


# --------------------------------------------------
# main function
# --------------------------------------------------

def _check_word(word, dictionary, bigrams, rules, slang, nltk_dict, prev_word=None, next_word=None):
    # check in dict
    in_dict = _check_in_dictionary_all_variants(word, dictionary)
    if in_dict:
        return in_dict
    # ------------------------------------

    # ------------------------------------

    # count letters:
    less_letters = _check_letters(word, dictionary)
    if less_letters:
        return less_letters
    # ------------------------------------

    # check in slang
    in_slang = _check_in_slang(word, slang)
    if in_slang:
        return in_slang
    # ------------------------------------

    # check in rules
    in_rules = _check_in_rules(word, dictionary, rules)
    if in_rules:
        return in_rules
    # ------------------------------------

    # check edit distance and bigrams
    most_likely_word, count = get_most_likely(word=word, d=dictionary, ngrams=bigrams, nltk_dict=nltk_dict,
                                              prev_word=prev_word, next_word=next_word)
    if int(count) > 0:
        return most_likely_word
    # ------------------------------------

    # # check character edit distance and bigrams
    # most_likely_with_chars, char_count = get_most_likely_char(word=word, d=dictionary, ngrams=bigrams,
    #                                                           morpho_test=_check_with_morphology)
    # if char_count > 0:
    #     return most_likely_with_chars
    # #------------------------------------

    # check with morphology
    morpho_word = _check_with_morphology(word)
    if morpho_word:
        return morpho_word
    # ------------------------------------

    # check with spaces
    spacy_word, count = _try_spaces(word, dictionary)
    if int(count) > 0:
        return spacy_word



    return None
    #------------------------------------


def get_words(text):
    return re.findall('[А-я]+', text)


def _correct_line(words, line, bigrams, vocab, rules, slang, nltk_dict):
    corr_line = line
    for i in range(len(words)):
        word = words[i]
        if i != 0:
            s = _check_word(word, vocab, bigrams, rules, slang, nltk_dict, prev_word=words[i - 1])
        else:
            s = _check_word(word, vocab, bigrams, rules, slang, nltk_dict, next_word=words[i + 1])
        if s:
            corr_line = corr_line.replace(word, s)
    return corr_line


def _start_testing(outpath, data, bigrams, vocab, rules, slang, nltk_dict=None):
    with open(outpath, "w", encoding="utf-8") as outfile:
        for line in data:
            words = get_words(line)
            corrected_line = _correct_line(words, line, bigrams, vocab, rules, slang, nltk_dict)
            outfile.write(corrected_line + "\n")

def main():
    usage = 'Usage: {} <input_file_dir> <outut_file_dir> <exps_dir> <vocab_path>'
    _, path, outpath, excps_dir, vocab_path = _get_data_from_cmd(5, usage)

    data = _read_file_lines("out/outfile_test77.txt")
    print("data loaded")
    bigrams = get_bigrams()
    print("bigrams loaded")
    vocab = get_vocab(vocab_path)
    print("vocab loaded")
    rules, slang = _get_exps(excps_dir)
    print("exceptions loaded")
    no_wiki_nltk_dict = get_vocab_nltk("spell/fact_ru_idiom_freq_2.pickle")
    print("nltk_dict_loaded")

    #_start_testing(outpath, data, bigrams, vocab, rules, slang)
    _start_testing(outpath, data, bigrams, vocab, rules, slang, nltk_dict=no_wiki_nltk_dict)


if __name__ == '__main__':
    main()
