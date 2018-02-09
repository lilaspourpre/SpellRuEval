# -*- coding: utf-8 -*-
import bisect
import os
import re
from basic_functions import *
from basic_functions import _create_folder_if_absent
from basic_functions import _get_data_from_cmd
from basic_functions import _read_file_lines


# --------------------------------------------------------------------
# DELETE TRASH AND WRITE
# --------------------------------------------------------------------
def _write_cut_data(dirname, vocab_wiki):
    # create output path
    cut_vocab_wiki_path = os.path.join(dirname, "cut_vocab_wiki.txt")

    # opening file and write data
    with open(cut_vocab_wiki_path, 'w', encoding='utf-8') as vocab_output:
        for word, count in vocab_wiki:
            if _check(word):
                vocab_output.write(word +" "+count+ '\n')


def _split_lines(lines, separator=" "):
    return [tuple(line.split(separator)) for line in lines]

def _check(word):
    regex = re.compile(u"[А-я]+")
    return word.isalpha() and regex.fullmatch(word)

# --------------------------------------------------------------------
# main
# --------------------------------------------------------------------

def main():
    # get data from cmd
    _, vocab_path, output_dir = _get_data_from_cmd(3, 'Usage: {} <input_directory_vocab> <output_directory>')

    # open full version files
    vocab_wiki = _read_file_lines(vocab_path)
    split_vocab_wiki = _split_lines(vocab_wiki, '\t')
    # write data
    _create_folder_if_absent(output_dir)
    _write_cut_data(output_dir, split_vocab_wiki)


if __name__ == "__main__":
    main()
