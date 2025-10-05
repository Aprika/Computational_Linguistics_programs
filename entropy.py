# Übung 2: Entropie

from collections import defaultdict
from math import log2

def read_corpus(filename):
    """
    :param filename: Dateipfadread (str)
    :return: Tag-Wahrscheinlichkeits-Dict und Wort-Tag-Wahrscheinlichkeits-Dict ((dict, dict))
    """
    tags = defaultdict(int)
    word_tags = defaultdict(int)
    with open(filename, "r", encoding="utf-8") as text:
        corpus = text.readlines()
    for line in corpus:
        units = line.replace("\n", "").split("\t")
        if len(units) > 1:
            word, tag = units
            tags[tag] += 1
            word_tags[(word, tag)] += 1
    return (tags, word_tags)

"""
# Practice solution
def read_corpus(filename):
    tag_freq = defaultdict(int)
    word_tag_freq = defaultdict(int)
    with open(filename, encoding="utf-8") as text:
        for line in line:
            line = line.strip()
            if line:
                word, tag = line.split("\t")
                word_tag_freq[word, tag] += 1
                tag_freq[tag] += 1
    return word_tag_freq, tag_freq
"""


def estimate_probs(freq):
    """
    :param freq: Dictionary mit Häufigkeiten
    :return: Dictionary mit Wahrscheinlichkeiten
    """
    tag_probs = defaultdict(float)
    n = sum(freq.values())
    for tag, fx in freq.items():
        tag_probs[tag] = fx/n
    return tag_probs

"""
# Practice solution
def estimate_probs(freq):
    n = sum(freq.values())  # Effizienter so, weil man sonst die Summe in der Comprehension immer neu berechnen muss
    prob = {tag: fx/n for tag, fx in freq.items()}
"""


def estimate_cond_probs(freq):
    """
    :param freq: Dictionary mit Häufigkeiten von Word-Tag-Paaren
    :return: Dictionary mit Bedingten Wahrscheinlichkeiten von Tags gegeben Wortpaar
    """
    total_word_freq = defaultdict(int)
    for word, tag in freq:
        total_word_freq[word] += freq[(word,tag)]
    word_tag_probs = defaultdict(float)
    for word_tag, a_b in freq.items():
        word, tag = word_tag
        word_tag_probs[word_tag] = a_b/total_word_freq[word]
    return word_tag_probs

"""
# Practice solution
def estimate_cond_probs(freq):
    # p(tag|wort) = f[word, tag] / f[wort]
    word_freq = defaultdict(int)
    for (word, _), f in freq.items():
        word_freq[word] += f
    word_tag_prob = {(word,tag): a_b/word_freq[word] for (word,tag), a_b in freq.items()}
    return word_tag_prob
"""


def entropy(prob):
    """
    :param prob: Dictionary (keys = Tags, vals = Wahrscheinlichkeiten)
    :return: Entropie der Wahrscheinlichkeitsverteilung
    """
    return -sum([p*log2(p) for p in prob.values()])

"""
# Practice solution is equal to mine
"""


tag_freq, word_tag_freq = read_corpus("../Data/tiger.txt")
tag_prob = estimate_probs(tag_freq)
word_tag_prob = estimate_cond_probs(word_tag_freq)
total_entropy = entropy(tag_prob)