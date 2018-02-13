import csv

def _read_file_lines(path):
    with open(path, 'r') as file:
        data = file.read().split("\n")
        return data

def _split_lines(lines, separator=" "):
    return dict([(line.split(separator)[1], line.split(separator)[0]) for line in columns])

def _get_rules():
    with open("exps/phoneticRules.txt", 'r', encoding='utf-8') as d:
        columns = d.read().split("\n")
        split = _split_lines(columns, "\t\t\t\t\t\t")
    return split

def _get_slang():
    with open("exps/slang.txt", 'r', encoding='utf-8') as d:
        columns = d.read().split("\n")
        slang = dict([line.split("      ") for line in columns])
    return slang
