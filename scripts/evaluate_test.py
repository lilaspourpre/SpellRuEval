import sys
import getopt

from evaluate import make_corrections_data, measure_quality, output_differences, extract_words


if __name__ == "__main__":
    args = sys.argv[1:]
    to_output_differences, lines_number = False, 100000
    opts, args = getopt.getopt(args, "l:d:", ["--lines_number", "--differences="])
    for opt, val in opts:
        if opt in ["-d", "--differences"]:
            to_output_differences = True
            diff_file = val
        elif opt in ["-l", "--lines_number"]:
            lines_number = int(val)
        else:
            print(ValueError("Wrong option {0}".format(opt)))
    if len(args) != 4:
        sys.exit("Использование: evaluate.py source_file correct_file answer_file index_file\n"
                 "source_file: исходный файл\n"
                 "correct_file: файл с эталонными исправлениями\n"
                 "answer_file: файл с ответами системы\n"
                 "index_file: файл с индексами предложений, по которым проводится тестирование")
    source_file, correct_file, answer_file, index_file = args
    print("Reading input...")
    with open(source_file, "r", encoding="utf8") as fsource,\
            open(correct_file, "r", encoding="utf8") as fcorr,\
            open(answer_file, "r", encoding="utf8") as fans:
        source_sents = [extract_words(line.strip().strip('\ufeff'))
                        for line in fsource.readlines() if line.strip().strip('\ufeff') != ""]
        correct_sents = [extract_words(line.strip().strip('\ufeff'))
                         for line in fcorr.readlines() if line.strip().strip('\ufeff') != ""]
        answer_sents = [extract_words(line.strip().strip('\ufeff')) for line in fans.readlines()][:100000]
    with open(index_file, "r") as find:
        indexes = [int(x.strip()) for x in find if x.strip() != ""]
    print("Extracting test sents...")
    source_sents = [source_sents[i] for i in indexes if i < lines_number]
    correct_sents = [correct_sents[i] for i in indexes if i < lines_number]
    answer_sents = [answer_sents[i] for i in indexes if i < lines_number]
    print("Making corrections data...")
    etalon_corrections, answer_corrections =\
        make_corrections_data(source_sents, correct_sents, answer_sents)
    TP, precision, recall, f_measure =\
        measure_quality(etalon_corrections, answer_corrections)
    equal_sents_number = sum(int(corr_sent == answer_sent)
                             for corr_sent, answer_sent in zip(correct_sents, answer_sents))
    accuracy = equal_sents_number / len(correct_sents)
    print("Precision={0:.2f} Recall={1:.2f} FMeasure={2:.2f} Accuracy={3:.2f}".format(
        100 * precision, 100 * recall, 100 * f_measure, 100 * accuracy))
    print(TP, len(answer_corrections), len(etalon_corrections))
    if to_output_differences:
        output_differences(diff_file, source_sents, correct_sents, answer_sents,
                           etalon_corrections, answer_corrections)
