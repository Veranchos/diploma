from random import shuffle
from nltk.probability import FreqDist
from corpus import normalize_corpora
import numpy

PARTS = 11
p = 0


# def randomize_words(corpus1, corpus2):
#     random_corpus1 = []
#     random_corpus2 = []
#     corpora = []
#
#     for i in range(len(corpus1)):
#         corpora.append([corpus1[i], corpus2[i]])
#
#     shuffle(corpora)
#
#     for i in range(len(corpora)):
#         item1, item2 = corpora[i]
#
#         random_corpus1.append(item1)
#         random_corpus2.append(item2)
#
#     return [random_corpus1, random_corpus2]


def create_wordlist(tokens):
    fdist1 = FreqDist(tokens).items()

    return sorted(fdist1, key=lambda item: item[1], reverse=True)

def create_known_similarity_corpora(corpus1, corpus2):
    known_similarity_corpora = []
    pieces = sum([i for i in range(PARTS)])

    start1 = 0
    end1 = 0
    start2 = 0
    end2 = PARTS - 1

    for i in range(1, PARTS+1):
        sub_corpus = corpus1[start1*len(corpus1)//pieces:end1*len(corpus1)//pieces] + \
                     corpus2[start2*len(corpus2)//pieces:end2*len(corpus2)//pieces]

        known_similarity_corpora.append(create_wordlist(sub_corpus))

        start1, end1 = end1, end1 + i
        start2, end2 = end2, end2 + (PARTS - i - 1)

    return known_similarity_corpora  # 11 corpora, including corpus1 and corpus2


def compare_known_similarity_corpora(ks_corpora, compare_corpora):
    CACHE = {}
    corpora_length = len(ks_corpora)
    counter = 0
    right_counter = 0

    for c in range(corpora_length):
        for d in range(corpora_length-1, c+1, -1):
            for a in range(c, d + 1):
                for b in range(d, a, -1):
                    if c == a and b == d:
                        continue

                    if str(c) + str(d) in CACHE:
                        distance1 = CACHE[str(c) + str(d)]
                    else:
                        corpus_c, corpus_d = normalize_corpora(ks_corpora[c], ks_corpora[d])
                        distance1 = compare_corpora(corpus_c, corpus_d)
                        CACHE[str(c) + str(d)] = distance1

                    if str(a) + str(b) in CACHE:
                        distance2 = CACHE[str(a) + str(b)]
                    else:
                        corpus_a, corpus_b = normalize_corpora(ks_corpora[a], ks_corpora[b])
                        distance2 = compare_corpora(corpus_a, corpus_b)
                        CACHE[str(a) + str(b)] = distance2

                    if distance2 < distance1:
                        right_counter += 1
                    counter += 1

    CACHE.clear()
    return right_counter / counter


def compare_measurement(corpus1, corpus2, compare_corpora):
    ks_corpora = create_known_similarity_corpora(corpus1, corpus2)

    return compare_known_similarity_corpora(ks_corpora, compare_corpora)
    # return percent of right signs

def compare_corpora_on_interval(compare_corpora, interval):

    return lambda c1, c2: compare_corpora(c1, c2, interval)

def ksc_in_intervals(corpus1, corpus2, compare_corpora, interval_length, step):

    iterations = (len(corpus1) - interval_length) // step
    percents_list = []

    print(len(corpus1), len(corpus2), interval_length)

    for i in range(400):
        interval = [i * step, interval_length + i * step]
        comparator = compare_corpora_on_interval(compare_corpora, interval)
        percent_on_interval = compare_measurement(corpus1, corpus2, comparator)
        n_corpus1, n_corpus2 = normalize_corpora(create_wordlist(corpus1), create_wordlist(corpus2))
        distance = comparator(n_corpus1, n_corpus2)

        print('ksc-in-intervals', interval, percent_on_interval, distance)

        percents_list.append([interval, percent_on_interval, distance])

    return percents_list

def find_best_interval(corpus1, corpus2, compare_corpora):
    best_interval = 0
    best_kilgarriff = 0

    n_corpus1, n_corpus2 = normalize_corpora(create_wordlist(corpus1), create_wordlist(corpus2))
    print(len(n_corpus1))
    for i in range(1, len(n_corpus1), 10):
        comparator = compare_corpora_on_interval(compare_corpora, [0,i])
        i_kilgarriff = compare_measurement(corpus1, corpus2, comparator)

        print('I try to find the best interval:', i, i_kilgarriff, comparator(n_corpus1, n_corpus2))
        if i_kilgarriff > best_kilgarriff:
            best_kilgarriff = i_kilgarriff
            best_interval = i

            if best_kilgarriff == 1:
                return best_interval

    return best_interval

