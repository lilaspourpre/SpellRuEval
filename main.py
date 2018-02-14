# -*- coding: utf-8 -*-
import re
from edit_distance import get_most_likely
from language_model import get_bigrams
from basic_functions import _get_data_from_cmd
from basic_functions import _read_file_lines
from parse_rules import _get_exps
from parse_rules import _get_vocab

numbers = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0")
punctuation = (',', '.', '?', '!', ':', '-', '—', ";", '«', '»', "...", "(", ")", "``", "--")


def _try_spaces(word, dictionary, flag=True):
    splits = [(word[:i], word[i:]) for i in range(1, len(word) + 1)]
    for split in splits:
        try:
            a, b = dictionary[split[0]], dictionary[split[1]]
            return " ".join(split), dictionary[split[0]]
        except KeyError as e:
            pass
    for split in splits:
        smaller_splits0 = [(split[0][:i], split[0][i:]) for i in range(1, len(split[0]) + 1)]
        for smsp0 in smaller_splits0:
            try:
                a, b, c = dictionary[smsp0[0]], dictionary[smsp0[1]], dictionary[split[1]]
                return " ".join(smsp0) + " " + split[1], dictionary[split[1]]
            except KeyError as e:
                pass
    for split in splits:
        smaller_splits1 = [(split[1][:i], split[1][i:]) for i in range(1, len(split[1]) + 1)]
        for smsp1 in smaller_splits1:
            try:
                a, b, c = dictionary[smsp1[0]], dictionary[smsp1[1]], dictionary[split[0]]
                return split[0] + " " + " ".join(smsp1), dictionary[split[0]]
            except KeyError as e:
                pass
    return word, 0


def _check_word(word, dictionary, bigrams, rules, slang, prev_word=None):
    most_likely_word, count = get_most_likely(word=word, d=dictionary, ngrams=bigrams, prev_word=prev_word)
    if int(count) > 0:
        return most_likely_word
    else:
        most_likely_word, count = _try_spaces(word, dictionary)
        if int(count) > 0:
            return most_likely_word
    return None


def get_words(text):
    return re.findall('\w+', text.lower())


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

    with open(outpath, "w", encoding="utf-8") as outfile:
        for line in data:
            words = get_words(line)
            corr_line = line
            for i in range(len(words)):
                if i != 0:
                    s = _check_word(words[i], vocab, bigrams, rules, slang, words[i - 1])
                else:
                    s = _check_word(words[i], vocab, bigrams, rules, slang)
                if s:
                    corr_line = corr_line.replace(words[i], s)
                    print(words[i], s)
                else:
                    print("**" * 3, words[i])
            outfile.write(corr_line)


if __name__ == '__main__':
    main()
