import os
import nltk
import pickle

fact_ru_eval_path = "factrueval-2016-tokenized/factrueval-2016-tokenized.txt"
idiom_path = "idioma1-tokenized/idioma1-tokenized.txt"
libru_path = "librusec-tokenized/librusec-tokenized.txt"
wiki_2017_path = "ruwiki-2017-tokenized/ruwiki-2017-tokenized.txt"
without_wiki2017 = [fact_ru_eval_path, idiom_path, libru_path]


def _read_file(path):
    with open(path, 'r', encoding='utf-8') as file:
        return [j for i in file.read().split("\n") for j in i.split()]

list_of_words = []
for path in without_wiki2017:
    list_of_words.extend(_read_file(path))

freq = nltk.FreqDist(list_of_words)
with open('no_wiki_ru_.pickle', 'wb') as f:
    pickle.dump(freq, f)

wiki = _read_file(wiki_2017_path)
freq_wiki = nltk.FreqDist(wiki)
with open('wiki_ru_.pickle', 'wb') as f_w:
    pickle.dump(freq_wiki, f_w)

cfreq = nltk.ConditionalFreqDist(nltk.bigrams(list_of_words))
with open('no_wiki_ru_cfreq.pickle', 'wb') as cf:
    pickle.dump(cfreq, cf)