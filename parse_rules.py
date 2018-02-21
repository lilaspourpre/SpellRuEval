import csv
import os
import pickle


def _read_file_lines(path):
    with open(path, 'r', encoding='utf-8') as file:
        data = file.read().split("\n")
        return data


def _split_lines(lines, separator=" "):
    return dict([(line.split(separator)[1], line.split(separator)[0]) for line in lines])


def _get_rules(directory):
    with open(os.path.join(directory, "phoneticRules.txt"), 'r', encoding='utf-8') as d:
        columns = d.read().split("\n")
        split = _split_lines(columns, "\t\t\t\t\t\t")
    return split


def _get_slang(directory):
    with open(os.path.join(directory, "slang.txt"), 'r', encoding='utf-8') as d:
        columns = d.read().split("\n")
        slang = dict([line.split("      ") for line in columns])
    return slang

def _get_exps(directory):
    return _get_rules(directory), _get_slang(directory)

def get_vocab_nltk(path):
    with open(path, 'rb') as f:
        return pickle.load(f)

def get_vocab(path):
    columns = _read_file_lines(path)
    slang = dict([(line.split(" ")[0], int(line.split(" ")[1])) for line in columns])
    return slang
