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


def _try_value(split, dictionary, flag=True):
    try:
        s = dictionary[split]
        return split, s
    except KeyError as e:
        if flag == True:
            return _try_spaces(split, dictionary, flag=False)
        else:
            return split, 0


def _try_spaces(word, dictionary, flag=True):
    splits = [(word[:i], word[i:]) for i in range(1, len(word) + 1)]
    for split in splits:
        split0 = split[0]
        split0, split0_val = _try_value(split0, dictionary, flag=flag)

        split1 = split[1]
        split1, split1_val = _try_value(split1, dictionary, flag=flag)

        try:
            a = dictionary[split0]
            return split0 + " " + split1, dictionary[split0]
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

    print(_try_spaces("ниначто", vocab))

    # with open(outpath, "w", encoding="utf-8") as outfile:
    #     for line in data:
    #         words = get_words(line)
    #         corr_line = line
    #         for i in range(len(words)):
    #             if i != 0:
    #                 s = _check_word(words[i], vocab, bigrams, rules, slang, words[i - 1])
    #             else:
    #                 s = _check_word(words[i], vocab, bigrams, rules, slang)
    #             if s:
    #                 corr_line = corr_line.replace(words[i], s)
    #                 print(words[i], s)
    #             else:
    #                 print("**" * 3, words[i])
    #         outfile.write(corr_line)
    #         exit(0)


if __name__ == '__main__':
    main()
