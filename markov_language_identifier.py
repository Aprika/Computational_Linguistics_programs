# Übung 4: Sprachidentifizierung

import json
import os
import re
import sys
from collections import defaultdict, Counter
from math import log

def extract_freq(data, n):
    # Aufgabe 2: Häufigkeiten aller Buchstaben-n-Gramme
    freq_dict = defaultdict(int)
    with open(data, mode="r", encoding="utf-8") as file:
        text = file.read().strip()
        text = " "*n + text + " "  # Hier werden die Placeholder-Spaces eingefügt
    freq_dict = Counter(text[n_gram:n_gram+n] for n_gram in range(len(text)-n))
    """
    for n_gram in range(len(text) - n + 1):
        freq_dict[text[n_gram:n_gram + n]] += 1
    """
    return freq_dict

def extract_relative_freq(n, n_gram_freq):
    # TODO: Debug this part of code. It does not return values for all possible n-grams
    # Aufgabe 8: Rekursive Berechnung von allen (2-n)-Grammen
    relative_freqs = {}
    for n in range(n, 0, -1):  # Absteigende Iteration von n bis 1
        """
        if n == 1:
            corpus_len = sum(n_gram_freq.values())
            relative_freqs.update({str((n_gram[-1])+"|"): freq/corpus_len
                              for n_gram, freq in n_gram_freq.items()})
            n -= 1
        else:
        """
        # Aufgabe 3: 1-malige und 2-malige n-Gramme
        once = len([freq for freq in n_gram_freq.values() if freq == 1])  # keys werden nicht benötigt
        twice = len([freq for freq in n_gram_freq.values() if freq == 2])

        # Aufgabe 4: Discount
        if once > twice > 0:
            discount = once / (once + 2 * twice)
        else:
            discount = 0.5

        # Aufgabe 5 und 7: Kontext-Häufigkeiten und n-1-Gramm-Häufigkeiten
        context_freqs = defaultdict(int)
        n_1_freqs = defaultdict(int)
        for n_gram, freq in n_gram_freq.items():  # Hier braucht man die Häufigkeiten zur Berechnung
            context_freqs[n_gram[:-1]] += freq
            n_1_freqs[n_gram[1:]] += freq

        # Aufgabe 6: relative Häufigkeiten
        # bedingte Wahrscheinlichkeiten als p("string") statt p("g"|"strin") berechnet
        relative_freqs.update({n_gram: (freq - discount) / context_freqs[n_gram[:-1]]
                              for n_gram, freq in n_gram_freq.items()})
        n_gram_freq = n_1_freqs
    return relative_freqs

def backoff(loaded):
    # Berechnet Backoff für eine JSON-Datei mit relativen Häufigkeiten
    relative_freq = {cond: freq for cond, freq in loaded.items()}
    alpha = defaultdict(lambda:1.0)
    for ngram, p in relative_freq.items():  # von Repetitorium übernommen
        alpha[ngram[:-1]] -= p
    return relative_freq, alpha

def recursive_prob(n, n_gram, relative_freq, alpha):
    if n_gram == "":
        return 0.001
    # Bei nicht existierenden relativen Häufigkeit wird ihr der Wert 0.0 gegeben
    return relative_freq.get(n_gram, 0.0) + alpha.get(n_gram[:-1], 1.0) * recursive_prob(n-1, n_gram[1:], relative_freq, alpha)

def predict_language(test, model_dir, alpha_dir):
    # TODO: Calculate the log probability of the input text being in each language
    # TODO: Return the most likely language
    language_probs = {}
    for language in os.listdir(model_dir):
        with open(model_dir+"/"+language, "r", encoding="utf-8") as json_file:
            n, loaded = json.load(json_file)
        relative_freq = {cond: freq for cond, freq in loaded.items()}
        with open("../Data/Language_Parameters/"+language, "r", encoding="utf-8") as alpha_file:
            alpha = json.load(alpha_file)
        # TODO: implement recursive log-likelihood function
        prob_list = []
        for idx in range(len(test)-n):
            n_gram = test[idx:idx+n]
            prob = recursive_prob(n, n_gram, relative_freq, alpha)
            prob_list.append(log(prob))
        language_probs[language.replace(".txt", "")] = sum(prob_list)
    max_probability = tuple(max(language_probs.items(), key=lambda x:x[1]))
    return max_probability


# Aufgabenteil 1
def start_training(n, training_data):
    # Aufgabe 1: Kommandozeileninput
    n_gram_freq = extract_freq(training_data, n)
    relative_freq = extract_relative_freq(n, n_gram_freq)

    # Aufgabe 9: Speicherung der Parameter in output
    with open("../Data/Language_Models/" + language.replace(".txt", ".json"), "w") as file:
        json.dump((n, relative_freq), file)

prefix = "../Data/Language-Samples/"

for language in os.listdir(prefix):
    # Input n-gram length and input file. Output file is created automatically
    start_training(5, training_data=prefix+language)



# Aufgabenteil 2
# Bemerkung: n hier soll n <= n von Trainingsdaten sein
def language_guesser(model_dir, test_file):
    # Aufgabe 1: Backoff-Faktoren berechnen und speichern
    for language in os.listdir(model_dir):
        with open(model_dir+"/"+language, "r") as json_file:
            n, loaded = json.load(json_file)
        relative_freq, alpha = backoff(loaded)
        with open("../Data/Language_Parameters/"+language.replace(".txt", ".json"), "w") as alpha_file:
            json.dump(alpha, alpha_file)

    # Aufgabe 2: Datei mit zu klassifizierenden Text einlesen, Tokens extrahieren
    with open(test_file, mode="r", encoding="utf-8") as test:
        test_cleaned = test.read().strip().replace("\n", " ")
        test_cleaned = re.sub(r'\s+', ' ', test_cleaned)
        # Hinzufügen von Leerzeichen für akkuratere Berechnung später
        test_cleaned = " "*n + test_cleaned + " "

    language_prediction = predict_language(test_cleaned, model_dir, "../Data/Language_Parameters/")
    return language_prediction

test_data = "../Data/Test_Data/"
for text in os.listdir(test_data):
    # Meine gewählte Testdateien und Gold Label:
    # zauberlehrling.txt ("Der Zauberlehrling"): Deutsch (hier benutzt als Development Data)
    # greek_anthem.txt ("Ymnos is tin Eleftherian"): Griechisch

    # anspruchsvollere Dateien:
    # jabberwockey.txt ("The Jabberwocky"): Englisch (aber ausgedachte Wörter)
    # onegin.txt (Tatianas Brief aus "Eugen Onegin"): Russisch (Sprache nicht in Trainingsdaten)
    result = language_guesser("../Data/Language_Models", test_data+text)
    print(f"{text}: {result[0].replace('.json', '')} | score: {result[1]}")
