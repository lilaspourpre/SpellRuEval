# -*- coding: utf-8 -*-
import re
from collections import Counter

from edit_distance import get_most_likely
from language_model import get_bigrams
from basic_functions import _get_data_from_cmd
from basic_functions import _read_file_lines
from parse_rules import _get_exps
from parse_rules import _get_vocab
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
            result = _check_in_dictionary(word.replace(rule, rules[rule]), dictionary)
            if result:
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


def _check_with_morphology(word, dictionary):
    w = MorphAnalyzer().word_is_known(word.lower())
    if w:
        return word
    return False


def _check_in_dictionary(word, dictionary):
    try:
        dict_word = dictionary[word]
        return word
    except KeyError:
        return False

def _check_letters(word, dictionary):
    counts = Counter(word)
    options = []
    for count in counts:
        if counts[count]>1:
            options.append(count*counts[count])
    new_w = word
    for option in options:
        if option in word:
            new_w = word.replace(option, option[0])
            try:
                a = dictionary[new_w]
                return new_w
            except KeyError:
                pass
    return False

def _check_word(word, dictionary, bigrams, rules, slang, prev_word=None):
    # check in dict
    in_dict = _check_in_dictionary(word, dictionary)
    if in_dict:
        return in_dict

    # count letters:
    less_letters = _check_letters(word, dictionary)
    if less_letters:
        return less_letters

    # check in slang
    in_slang = _check_in_slang(word, slang)
    if in_slang:
        return in_slang

    # check in rules
    in_rules = _check_in_rules(word, dictionary, rules)
    if in_rules:
        return in_rules

    # check edit distance and bigrams
    most_likely_word, count = get_most_likely(word=word, d=dictionary, ngrams=bigrams, prev_word=prev_word)
    if int(count) > 0:
        return most_likely_word

    # check with morphology
    morpho_word = _check_with_morphology(word, dictionary)
    if morpho_word:
        return morpho_word

    # check with spaces
    spacy_word, count = _try_spaces(word, dictionary)
    if int(count) > 0:
        return spacy_word
    return None


def get_words(text):
    return re.findall('[А-я]+', text)


def main():
    usage = 'Usage: {} <input_file_dir> <outut_file_dir> <exps_dir> <vocab_path>'
    _, path, outpath, excps_dir, vocab_path = _get_data_from_cmd(5, usage)

    data = _read_file_lines(path)
    print("data loaded")
    bigrams = get_bigrams()
    print("bigrams loaded")
    vocab = _get_vocab(vocab_path)
    print("vocab loaded")
    rules, slang = _get_exps(excps_dir)
    print("exceptions loaded")

    with open(outpath, "w", encoding="utf-8") as outfile, open("index_file.txt", 'w', encoding='utf-8') as indexfile:
        count=0
        for line in data:
            words = get_words(line)
            corr_line = line
            for i in range(len(words)):
                if i != 0:
                    if words[i].isupper():
                        m = _check_in_dictionary(words[i], vocab)
                        if m:
                            s = words[i]
                        else:
                            s = _check_word(words[i].lower(), vocab, bigrams, rules, slang, words[i - 1])
                    else:
                        s = _check_word(words[i].lower(), vocab, bigrams, rules, slang, words[i - 1])
                else:
                    if words[i].isupper():
                        m = _check_in_dictionary(words[i], vocab)
                        if m:
                            s = words[i]
                        else:
                            s = _check_word(words[i].lower(), vocab, bigrams, rules, slang)
                    else:
                        s = _check_word(words[i].lower(), vocab, bigrams, rules, slang)
                if s:
                    corr_line = corr_line.replace(words[i], s)
            outfile.write(corr_line + "\n")
            indexfile.write(str(count)+"\n")
            count+=1


if __name__ == '__main__':
    main()
