# -*- coding: utf-8 -*-
from nltk.tokenize import word_tokenize
#! python3


import re
numbers = ("1","2","3","4","5","6","7","8","9","0")
punctuation = (',', '.', '?', '!', ':', '-', '—', ";", '«', '»', "...", "(", ")", "``", "--")
alphabet = 'abcdefghijklmnopqrstuvwxyz'


def _read_file_lines(path):
    with open(path, 'r', encoding='utf-8') as file:
        data = file.read().split("\n")
        return data

def _split_lines(lines, separator=" "):
    return dict([(line.split(separator)[0], int(line.split(separator)[1])) for line in lines])

def get_words(text):
    return re.findall('\w+', text.lower())

def get_edits1(word):
    splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes    = [a + b[1:] for a, b in splits if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
    replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
    inserts    = [a + c + b     for a, b in splits for c in alphabet]
    return set(deletes + transposes + replaces + inserts)

def get_most_likely(word, d):
    candidates = []
    if word not in d:
        for w in get_edits1(word):
            if w in d:
                candidates.append(w)
        if not candidates:
            splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
            for split in splits:
                try:
                    return (split[0] +" "+ split[1], d[split[0]]+d[split[1]])
                except:
                    pass
            return word, 0
        cand = max(candidates, key=d.get)
        return cand, d[cand]
    else:
        return word, d[word]

def _check_words_forms(word, dict_vocabs):
    if word not in punctuation:

            new_word, count = get_most_likely(word.lower(), dict_vocabs)
            if count == 0:

                print(word)




def main():
    vocab = _read_file_lines("spellcorrection/vocabs/cut_vocab_wiki.txt")
    dict_vocabs = _split_lines(vocab, ' ')
    train_input = _read_file_lines("spellcorrection/data/source_sents_train.txt")
    with open("my_frist_res.txt", 'w') as f:
        for line in train_input:
            words = word_tokenize(line)
            for word in words:
                new_word, count = _check_words_forms(word, dict_vocabs)
                if count == 0:
                    new_word, count = _check_exceptions(word, dict_vocabs)
                    if count == 0:
                        new_word, count = _check_phonetics(word, dict_vocabs)
                        if count == 0:
                            new_word = word
                print(word, "=>", new_word)
                line = line.replace(word, new_word)
                f.write(line+"\n")





if __name__ == '__main__':
    main()