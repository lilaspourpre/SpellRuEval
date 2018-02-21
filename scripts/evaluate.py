import sys
import copy
import getopt
import re

import numpy as np

from collections import defaultdict, deque

def extract_words(line, make_lower=True, split_by_dots=False):
    line = line.strip()
    if split_by_dots:
        sents = re.split('[^а-яёa-z0-9\-.:/,]+', line, flags=re.I)
    else:
        sents = line.split()
    words = []
    for word in sents:
        if make_lower:
            word = word.lower().replace('ё', 'е')
        else:
            word = word.replace('ё', 'е')
            word = word.replace('Ё', 'Е')
        i = len(word) - 1
        while i >= 0 and not (word[i].isalpha() or word[i].isdigit()):
            i -= 1
        if i < 0:
            continue
        word = word[:(i+1)]
        while len(word) > 0 and not (word[0].isalpha() or word[0].isdigit()):
            word = word[1:]
        if word != "":
            words.append(word)
    return words

def levenstein_dist(source, correct, allow_transpositions=False,
                    removal_cost=1.0, insertion_cost=1.0, replace_cost=1.0, transposition_cost=1.0):
    table, _ = make_levenstein_table(source, correct, allow_transpositions=allow_transpositions,
                                  removal_cost=removal_cost, insertion_cost=insertion_cost,
                                  transposition_cost=transposition_cost)
    return table[-1][-1]


def make_levenstein_table(source, correct, allow_transpositions=False,
        removal_cost=1.0, insertion_cost=1.0, replace_cost=1.0, transposition_cost=1.0):
    """
    Строит динамическую таблицу, применяемую при вычислении расстояния Левенштейна,
    а также массив обратных ссылок, применяемый при восстановлении выравнивания

    :param source: list of strs, исходное предложение
    :param correct: list of strs, исправленное предложение
    :param allow_transpositions: bool, optional(default=False),
        разрешены ли перестановки соседних символов в расстоянии Левенштейна
    :param removal_cost: float, optional(default=1.0),
        штраф за удаление
    :param insertion_cost: float, optional(default=1.0),
        штраф за вставку
    :param replace_cost: float, optional(default=1.0),
        штраф за замену символов
    :param transposition_cost: float, optional(default=1.0),
        штраф за перестановку символов
    :return:
        table, numpy 2D-array of float, двумерная таблица расстояний между префиксами,
            table[i][j] = d(source[:i], correct[:j])
        backtraces, 2D-array of lists,
            двумерный массив обратных ссылок при вычислении оптимального выравнивания
    """
    first_length, second_length = len(source), len(correct)
    table = np.zeros(shape=(first_length + 1, second_length + 1), dtype=float)
    backtraces = [([None]  * (second_length + 1)) for _ in range(first_length + 1)]
    for i in range(1, second_length + 1):
        table[0][i] = i
        backtraces[0][i] = [(0, i-1)]
    for i in range(1, first_length + 1):
        table[i][0] = i
        backtraces[i][0] = [(i-1, 0)]
    for i, first_word in enumerate(source, 1):
        for j, second_word in enumerate(correct, 1):
            if first_word == second_word:
                table[i][j] = table[i-1][j-1]
                backtraces[i][j] = [(i-1, j-1)]
            else:
                table[i][j] = min((table[i-1][j-1] + replace_cost,
                                   table[i][j-1] + removal_cost,
                                   table[i-1][j] + insertion_cost))
                if (allow_transpositions and min(i, j) >= 2
                        and first_word == correct[j-2] and second_word == source[j-2]):
                    table[i][j] = min(table[i][j], table[i-2][j-2] + transposition_cost)
                curr_backtraces = []
                if table[i-1][j-1] + replace_cost == table[i][j]:
                    curr_backtraces.append((i-1, j-1))
                if table[i][j-1] + removal_cost == table[i][j]:
                    curr_backtraces.append((i, j-1))
                if table[i-1][j] + insertion_cost == table[i][j]:
                    curr_backtraces.append((i-1, j))
                if (allow_transpositions and min(i, j) >= 2
                    and first_word == correct[j-2] and second_word == source[j-2]
                        and table[i][j] == table[i-2][j-2] + transposition_cost):
                    curr_backtraces.append((i-2, j-2))
                backtraces[i][j] = copy.copy(curr_backtraces)
    return table, backtraces

def extract_best_alignment(backtraces):
    """
    Извлекает оптимальное выравнивание из таблицы обратных ссылок

    :param backtraces, 2D-array of lists,
        двумерный массив обратных ссылок при вычислении оптимального выравнивания
    :return: best_paths, list of lists,
        список путей, ведущих из точки (0, 0) в точку (m, n) в массиве backtraces
    """
    m, n = len(backtraces) - 1, len(backtraces[0]) - 1
    used_vertexes = {(m, n)}
    reverse_path_graph = defaultdict(list)
    vertexes_queue = [(m, n)]
    # строим граф наилучших путей в таблице
    while len(vertexes_queue) > 0:
        i, j = vertex = vertexes_queue.pop(0)
        if i > 0 or j > 0:
            for new_vertex in backtraces[i][j]:
                reverse_path_graph[new_vertex].append(vertex)
                if new_vertex not in used_vertexes:
                    vertexes_queue.append(new_vertex)
                    used_vertexes.add(new_vertex)
    # проходим пути в обратном направлении
    best_paths = []
    current_path = [(0, 0)]
    last_indexes, neighbor_vertexes_list = [], []
    while len(current_path) > 0:
        if current_path[-1] != (m, n):
            children = reverse_path_graph[current_path[-1]]
            if len(children) > 0:
                current_path.append(children[0])
                last_indexes.append(0)
                neighbor_vertexes_list.append(children)
                continue
        else:
            best_paths.append(copy.copy(current_path))
        while len(last_indexes) > 0 and last_indexes[-1] == len(neighbor_vertexes_list[-1]) - 1:
            current_path.pop()
            last_indexes.pop()
            neighbor_vertexes_list.pop()
        if len(last_indexes) == 0:
            break
        last_indexes[-1] += 1
        current_path[-1] = neighbor_vertexes_list[-1][last_indexes[-1]]
    return best_paths

def extract_basic_alignment_paths(paths_in_alignments, source, correct):
    """
    Извлекает из путей в таблице Левенштейна тождественные замены в выравнивании

    :param paths_in_alignments: list of lists, список оптимальных путей
        в таблице из точки (0, 0) в точку (len(source), len(correct))
    :param source: str, исходная строка,
    :param correct: str, строка с исправлениями
    :return:
        answer: list, список вариантов тождественных замен в оптимальных путях
    """
    m, n = len(source), len(correct)
    are_symbols_equal = np.zeros(dtype=bool, shape=(m, n))
    for i, a in enumerate(source):
        for j, b in enumerate(correct):
            are_symbols_equal[i][j] = (a == b)
    answer = set()
    for path in paths_in_alignments:
        answer.add(tuple(elem for elem in path[1:] if (elem[0] > 0 and elem[1] > 0
                                                       and are_symbols_equal[elem[0]-1][elem[1]-1])))
    return list(answer)

def extract_levenstein_alignments(source, correct, replace_cost=1.0):
    """
    Находит позиции тождественных замен
    в оптимальном выравнивании между source и correct

    :param source: str. исходная строка
    :param correct: str, исправленная строка
    :return: basic_alignment_paths, list of lists of pairs of ints
        список позиций тождественных замен в оптимальном выравнивании
    """
    table, backtraces = make_levenstein_table(source, correct, replace_cost=replace_cost)
    paths_in_alignments = extract_best_alignment(backtraces)
    basic_alignment_paths = extract_basic_alignment_paths(paths_in_alignments, source, correct)
    return basic_alignment_paths

def get_partition_indexes(first, second):
    """
    Строит оптимальное разбиение на группы (ошибка, исправление)
    Группа заканчивается после first[i] и second[j], если пара из
    концов этих слов встречается в оптимальном пути в таблице Левенштейна
    для " ".join(first) и " ".join(second)

    :param first: list of strs, список исходных слов
    :param second: list of strs, их исправление
    :return: answer, list of pairs of ints,
        список пар (f[0], s[0]), (f[1], s[1]), ...
        отрезок second[s[i]: s[i+1]] является исправлением для first[f[i]: f[i+1]]
    """
    m, n = len(first), len(second)
    answer = [(0, 0)]
    if m <= 1 or n <= 1:
        answer += [(m, n)]
    else:
        levenstein_table, backtraces = make_levenstein_table(" ".join(first), " ".join(second))
        best_paths_in_table = extract_best_alignment(backtraces)
        good_partitions, other_partitions = set(), set()
        word_ends = [0], [0]
        last = -1
        for i, word in enumerate(first):
            last = last + len(word) + 1
            word_ends[0].append(last)
        last = -1
        for i, word in enumerate(second):
            last = last + len(word) + 1
            word_ends[1].append(last)
        for path in best_paths_in_table:
            current_indexes = [(0, 0)]
            first_pos, second_pos = 0, 0
            is_partition_good = True
            for i, j in path[1:]:
                if i > word_ends[0][first_pos]:
                    first_pos += 1
                if j > word_ends[1][second_pos]:
                    second_pos += 1
                if i == word_ends[0][first_pos] and j == word_ends[1][second_pos]:
                    if first_pos > current_indexes[-1][0] and second_pos > current_indexes[-1][1]:
                        current_indexes.append((first_pos, second_pos))
                        if first_pos < len(first):
                            first_pos += 1
                        if second_pos < len(second):
                            second_pos += 1
                    else:
                        is_partition_good = False
            if current_indexes[-1] == (m, n):
                if is_partition_good:
                    good_partitions.add(tuple(current_indexes))
                else:
                    other_partitions.add(tuple(current_indexes))
            else:
                current_indexes = current_indexes[:-1] + [(m, n)]
                other_partitions.add(tuple(current_indexes))
        if len(good_partitions) >= 1:
            answer = list(good_partitions)[0]
        else:
            answer = list(other_partitions)[0]
    return answer

def align_sents(source, correct, return_only_different=False, replace_cost=1.0,
                partition_intermediate=True, groups_in_source=None):
    """
    Возвращает индексы границ групп в оптимальном выравнивании

    :param source, correct: str, исходное и исправленное предложение
    :param return_only_different: следует ли возвращать только индексы нетождественных исправлений
    :param replace_cost: штраф за нетождественную замену
    :return: answer, list of pairs of tuples,
        оптимальное разбиение на группы. Если answer[i] == ((i, j), (k, l)), то
        в одну группу входят source[i:j] и correct[k:l]
    """
    if groups_in_source is None:
        groups_in_source = []
    alignments = extract_levenstein_alignments(source, correct, replace_cost=replace_cost)
    m, n = len(source), len(correct)
    prev = 0, 0
    answer = []
    for i, j in alignments[0]:
        if i > prev[0] + 1 or j > prev[1] + 1:
            if partition_intermediate:
                partition_indexes =\
                    get_partition_indexes(source[prev[0]: i-1], correct[prev[1]: j-1])
                if partition_indexes is not None:
                    for pos, (f, s) in enumerate(partition_indexes[:-1]):
                        answer.append(((prev[0] + f, prev[0] + partition_indexes[pos+1][0]),
                                       (prev[1] + s, prev[1] + partition_indexes[pos+1][1])))
                else:
                    answer.append(((prev[0], i-1), (prev[1], j-1)))
            else:
                answer.append(((prev[0], i-1), (prev[1], j-1)))
        answer.append(((i-1, i), (j-1, j)))
        prev = i, j
    if m > prev[0] or n > prev[1]:
        if partition_intermediate:
            partition_indexes =\
                    get_partition_indexes(source[prev[0]: m], correct[prev[1]: n])
            if partition_indexes is not None:
                for pos, (f, s) in enumerate(partition_indexes[:-1]):
                        answer.append(((prev[0] + f, prev[0] + partition_indexes[pos+1][0]),
                                       (prev[1] + s, prev[1] + partition_indexes[pos+1][1])))
            else:
                answer.append(((prev[0], m), (prev[1], n)))
        else:
            answer.append(((prev[0], m), (prev[1], n)))
    positions_in_answer = []
    indexes_in_source = [elem[0] for elem in answer]
    end_in_answer = -1
    for pos, (i_ref, j_ref) in enumerate(groups_in_source):
        start_in_answer = end_in_answer + 1
        while (start_in_answer < len(indexes_in_source) and
                       indexes_in_source[start_in_answer][0] < i_ref):
            start_in_answer += 1
        if start_in_answer == len(indexes_in_source):
            break
        i, j = indexes_in_source[start_in_answer]
        end_in_answer = start_in_answer
        if i == i_ref:
            while (end_in_answer < len(indexes_in_source) and
                        indexes_in_source[end_in_answer][1] < j_ref):
                end_in_answer += 1
            if end_in_answer == len(indexes_in_source):
                break
            if indexes_in_source[end_in_answer][1] == j_ref:
                positions_in_answer.append((start_in_answer, end_in_answer))
    prev_end = -1
    new_answer = []
    for start_in_answer, end_in_answer in positions_in_answer:
        new_answer.extend(answer[prev_end+1: start_in_answer])
        new_answer.append(((answer[start_in_answer][0][0], answer[end_in_answer][0][1]),
                           (answer[start_in_answer][1][0], answer[end_in_answer][1][1])))
        prev_end = end_in_answer
    new_answer.extend(answer[prev_end+1: ])
    answer = new_answer
    if return_only_different:
        answer = [((i, j), (k, l)) for ((i, j), (k, l)) in answer if source[i:j] != correct[k:l]]
    return answer

def make_corrections_data(source_sents, correct_sents, answer_sents):
    etalon_corrections = dict()
    answer_corrections = dict()
    for num, (source, correct, answer) in\
            enumerate(zip(source_sents, correct_sents, answer_sents)):
        print(num)
        indexes = align_sents(source, correct, return_only_different=True, replace_cost=1.9)
        for ((i, j), (k, l)) in indexes:
            etalon_corrections[(num, i, j)] = tuple(correct[k:l])
        indexes = align_sents(source, answer, return_only_different=True, replace_cost=1.9,
                              groups_in_source=[elem[0] for elem in indexes])
        for ((i, j), (k, l)) in indexes:
            answer_corrections[(num, i, j)] = tuple(answer[k:l])
    return etalon_corrections, answer_corrections

def measure_quality(etalon_corrections, answer_corrections):
    TP = 0
    for triple, answer_correction in answer_corrections.items():
        etalon_correction = etalon_corrections.get(triple)
        if etalon_correction == answer_correction:
            TP += 1
    precision = TP / len(answer_corrections)
    recall = TP / len(etalon_corrections)
    f_measure = 2 * precision * recall / (precision + recall)
    return TP, precision, recall, f_measure


def output_differences(diff_file, source_sents, correct_sents, answer_sents,
                       etalon_corrections, answer_corrections):
    false_positives = defaultdict(list)
    false_negatives = defaultdict(list)
    miscorrections = defaultdict(list)
    for (num, i, j), answer_correction in answer_corrections.items():
        etalon_correction = etalon_corrections.get((num, i, j))
        if etalon_correction is None:
            false_positives[num].append(((i, j), answer_correction))
        elif etalon_correction != answer_correction:
            miscorrections[num].append(((i, j), answer_correction, etalon_correction))
    for (num, i, j), etalon_correction in etalon_corrections.items():
        answer_correction = answer_corrections.get((num, i, j))
        if answer_correction is None:
            false_negatives[num].append(((i, j), etalon_correction))
    with open(diff_file, "w", encoding="utf8") as fout:
        width = 24
        for num, sent in enumerate(source_sents):
            current_false_positives = false_positives[num]
            current_false_negatives = false_negatives[num]
            current_miscorrections = miscorrections[num]
            if (len(current_false_positives) == 0 and len(current_false_negatives) == 0 and
                    len(current_miscorrections) == 0):
                continue
            fout.write("{0}\n{1}\n{2}\n".format(
                " ".join(sent), " ".join(answer_sents[num]), " ".join(correct_sents[num])))
            for (i, j), answer_correction in current_false_positives:
                fout.write("{0:<{width}}{1:<{width}}{2:<{width}}\n".format(" ".join(sent[i:j]),
                    " ".join(answer_correction), " ".join(sent[i:j]), width=width))
            for (i, j), etalon_correction in current_false_negatives:
                fout.write("{0:<{width}}{1:<{width}}{2:<{width}}\n".format(" ".join(sent[i:j]),
                    " ".join(sent[i:j]), " ".join(etalon_correction), width=width))
            for (i, j), answer_correction, etalon_correction in current_miscorrections:
                fout.write("{0:<{width}}{1:<{width}}{2:<{width}}\n".format(" ".join(sent[i:j]),
                    " ".join(answer_correction), " ".join(etalon_correction), width=width))
            fout.write("\n")
    return

def test(task=1):
    if task == 0:
        first_sent = ['фотка', 'классная', 'кстате', 'хоть', 'и', 'не', 'по', 'теме']
        second_sent = ['фотка', 'классная', 'кстати', 'хотя', 'не', 'по', 'теме']
        align_sents(first_sent, second_sent, replace_cost=1.9)
    elif task == 1:
        first, second = 'жж', 'ж'
        align_sents(first, second)


if __name__ == "__main__":
    args = sys.argv[1:]
    to_output_differences = False
    opts, args = getopt.getopt(args, "d:", ["--differences="])
    for opt, val in opts:
        if opt in ["-d", "--differences"]:
            to_output_differences = True
            diff_file = val
        else:
            print(ValueError("Wrong option {0}".format(opt)))
    if len(args) == 0:
        test()
        sys.exit(0)
    if len(args) != 3:
        sys.exit("Использование: evaluate.py source_file correct_file answer_file\n"
                 "source_file: исходный файл\n"
                 "correct_file: файл с эталонными исправлениями\n"
                 "answer_file: файл с ответами системы\n")
    source_file, correct_file, answer_file = args
    with open(source_file, "r", encoding="utf8") as fsource,\
            open(correct_file, "r", encoding="utf8") as fcorr,\
            open(answer_file, "r", encoding="utf8") as fans:
        source_sents = [extract_words(line.strip().strip('\ufeff'))
                        for line in fsource.readlines() if line.strip().strip('\ufeff') != ""]
        correct_sents = [extract_words(line.strip().strip('\ufeff'))
                         for line in fcorr.readlines() if line.strip().strip('\ufeff') != ""]
        answer_sents = [extract_words(line.strip().strip('\ufeff'))
                        for line in fans.readlines() if line.strip().strip('\ufeff') != ""]
    etalon_corrections, answer_corrections =\
        make_corrections_data(source_sents, correct_sents, answer_sents)
    TP, precision, recall, f_measure = measure_quality(etalon_corrections, answer_corrections)
    print("Precision={0:.2f} Recall={1:.2f} FMeasure={2:.2f}".format(
        100 * precision, 100 * recall, 100 * f_measure))
    print(TP, len(answer_corrections), len(etalon_corrections))
    if to_output_differences:
        output_differences(source_sents, correct_sents, answer_sents,
                           etalon_corrections, answer_corrections)




