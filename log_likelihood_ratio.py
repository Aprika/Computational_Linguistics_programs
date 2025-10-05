# Übung 3: Log Likelihood Ratio

from collections import defaultdict
from math import log2


def observed_expected_values(word1, word2, word_pair_count, adj_count, noun_count, num_word_pairs):
    O__ = num_word_pairs
    O1_ = adj_count
    O2_ = O__ - O1_
    O_1 = noun_count
    O_2 = O__ - O_1
    O11 = word_pair_count
    O12 = adj_count - O11
    O21 = O_1 - O11
    O22 = O_2 - O12

    E11 = (O1_ * O_1) / O__
    E12 = (O1_ * O_2) / O__
    E21 = (O2_ * O_1) / O__
    E22 = (O2_ * O_2) / O__

    return [O11, O12, O21, O22], [E11, E12, E21, E22]

def calculate_llr(filename):
    word1_freq = defaultdict(int)
    word2_freq = defaultdict(int)
    wordpair_freq = defaultdict(int)
    with open(filename, encoding="utf-8") as text:
        for line in text:
            line = line.strip()
            if line:
                count, word1, word2 = line.split("\t")
                word1_freq[word1] += int(count)
                word2_freq[word2] += int(count)
                wordpair_freq[word1, word2] += int(count)
    total_wordpairs = sum(wordpair_freq.values())

    # TODO: Fix function to calculate the correct llr!
    # Wenn ein Wort nicht in dem tatsächlichen Wortpaar-Dict vorkommt (Oij = 0), ist LLR nicht anwendbar
    # In einem solchen Fall ist LLR = None
    llr = {}
    for (word1, word2), pair_freq in wordpair_freq.items():
        observed, expected = observed_expected_values(word1=word1, word2=word2, word_pair_count=pair_freq,
                                                      adj_count=word1_freq[word1], noun_count=word2_freq[word2],
                                                      num_word_pairs=total_wordpairs)
        llr.update({(word1, word2): 2 * sum(o * log2(o/e) for o, e in zip(observed, expected) if o > 0)})
    return llr

final_result = calculate_llr("../Data/word-pairs.txt")
print(list(final_result.items())[:20])
sorted_results = sorted(final_result.items(), key=lambda x:x[1], reverse=True)
print(sorted_results[:20])


"""
# Ergebnis der Vorlesung
import sys
from collections import defaultdict
from math import log2

def read_data(filename):
    word_pair_count = {}
    adj_count = defaultdict(int)
    noun_count = defaultdict(int)
    with open(filename) as file:
        for line in file:
            count, word1, word2 = line.strip().split("\t")
            word_pair_count[word1, word2] = int(count)
            adj_count[word1] += int(count)
            noun_count[word2] += int(count)
        num_word_pairs = sum(word_pair_count.values())
    return word_pair_count, adj_count, noun_count, num_word_pairs


def observed_expected_values(word1, word2, word_pair_count, adj_count, noun_count, num_word_pairs):
    O__ = num_word_pairs
    O1_ = adj_count[word1]
    O2_ = O__ - O1_
    O_1 = noun_count[word2]
    O_2 = O__ - O_1
    O11 = word_pair_count[word1, word2]
    O12 = adj_count[word1] - O11
    O21 = O_1 - 011
    O22 = O_2 - 012
    
    E11 = (O1_ * O_1) / O__
    E12 = (O1_ * O_2) / O__
    E21 = (O2_ * O_1) / O__
    E22 = (O2_ * O_2) / O__
      
    return [O11, O12, O21, O22], [E11, E12, E21, E22]
    

def llr(word1, word2, word_pair_count, adj_count, noun_count, num_word_pairs):
    O, E = obeserved_expected_values(word1, word2, word_pair_count, adj_count, noun_count, num_word_pairs)
    # Berechnen die Summe der Werte für alle 4 Kombinationen (2 Varianten per Wort: taucht auf oder taucht nicht auf)
    return 2 * sum(o * log2(o/e) for o, e in zip(O, E) if o > 0)  # Rausfiltern von 0-Werten (e kann nicht 0 sein)
                                                            # Sonst gibt es log-Null-Fehler (undefiniert, aber gegen 0)


LLR = {(word1, word2): llr(word1, word2,
                            word_pair_count, adj_count, noun_count, num_word_pairs):
        for (word1, word2), count in word_pair_count.items()}

for (word1, word2), llr in sorted(LLR.item(), key=lambda x:-x[1]):
    print(word1, word2, llr, sep="\t"

sorted(LLR)

# Idee mit Pandas: Nützlich zum Einlesen von Daten
# Bei read_data:
    # Dataframe erstellen
    df = pd.read_csv(filename, sep='\t', header=None, names["count", "word1", "word2"]) # also eliminates strip() and split("\t")
    # Statt while open as und for loop in Originalcode (über Dataframe iterieren)
    for, index, row in df.iterrows():
        word_pair_count[row["word1"], row["word2"]] == int(row["count"])  # usw.
# In der Prüfung nur Standard-Python nützlich (merken, welche Pakete Teil von Standard-Python sind!)
"""
