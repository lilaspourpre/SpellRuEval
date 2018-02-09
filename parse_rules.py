import csv

def _read_file_lines(path):
    with open(path, 'r') as file:
        data = file.read().split("\n")
        return data

def _split_lines(lines, separator=" "):
    return dict([line.split(separator) for line in lines])

with open("exps/phoneticRules.txt", 'r', encoding='utf-8') as d:
    columns = d.read().split("\n")
    split = _split_lines(columns, "\t\t\t\t\t\t")
print(split)