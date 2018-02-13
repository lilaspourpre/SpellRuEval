# -*- coding: utf-8 -*-
import numpy as np
import sys
import os

CR_V_DATA_PATH = "cross_validation_data"
TOKENS = "tokens.txt"
CONCEPTS = "concepts.txt"
WITH_TITLES_CONCEPTS = "concepts_with_titles.txt"
TEST_WITH_TITLES_CONCEPTS = "concepts_with_titles_test.txt"


# --------------------------------------------------------------------
# sys
# --------------------------------------------------------------------
def _get_data_from_cmd(length, usage):
    args = sys.argv
    if len(args) != length:
        print(usage.format(args[0]))
        raise AttributeError("Wrong arguments")
    return sys.argv


def _create_folder_if_absent(path):
    if not os.path.exists(path):
        os.mkdir(path)

# --------------------------------------------------------------------
# read and write
# --------------------------------------------------------------------
def _read_file_lines(path):
    with open(path, 'r', encoding='utf-8') as file:
        return file.read().split("\n")

def _read_file(path):
    with open(path, 'r', encoding='utf-8') as file:
        return file.read()

def _write_to_file(dirname, name, data):
    filename = os.path.join(dirname, name)
    with open(filename, 'w', encoding="utf-8") as file_to_write:
        file_to_write.writelines(data)