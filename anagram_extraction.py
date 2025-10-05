import regex as re
from collections import defaultdict, Counter

def read_data(filename):
    """
    Extracts all the words in the first column
    :param filename: filename of space-separated file with three columns
    :return: list of words (list[string])
    """
    with open(filename, 'r', encoding="utf-8") as f:
        lines = f.readlines()
    first_column = [line.split()[0] for line in lines if line.split()[0].isalpha()]
    return first_column

def anagram(words):
    """
    First creates a nested dictionary to store all the anagrams in lower-and uppercase forms together with their counts. Each line has its word sorted by occurrence in its most common form. Outputs in required format.
    :param words: list of words (list[string])
    :return: None
    """
    ana_freq = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    for word in words:
        word_type = word.lower()
        sorted_letters = "".join(sorted(word_type))
        ana_freq[sorted_letters][word_type][word] += 1
    ana_collection = [[max(ana_freq[sorted_word][word_type].items()) for word_type in ana_freq[sorted_word]
                   if sum(ana_freq[sorted_word][word_type].values()) > 10]
                  for sorted_word in ana_freq]
    ana_sorted = [" ".join([word for _, word in sorted([(count, word) for word, count in tuple_list], reverse=True)])
                   for tuple_list in ana_collection if len(tuple_list) >= 2]
    for word_list in ana_sorted:
        print(word_list)
    return ana_sorted



read_lines = read_data("../Data/zeit-10M-tagged")
anagram(read_lines)

