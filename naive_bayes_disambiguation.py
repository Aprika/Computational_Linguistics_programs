# Übung 5: Wortbedeutungsdesambiguierung

from collections import defaultdict, Counter
from math import prod
import json
import re

# Teil 1: Training eines Wortbedeutungsdesambiguierers
    # Schritt 1: Alle Vorkommen der Wörter "Staat" und "Kind" extrahieren
        # Dazu alle max. 50 Positionen entfernte Inhaltswörter
        # Inhaltswort hat Tag: ADJA, ADJD, ADV, NE, NN, VVFIN, VVINF, VVPP oder VVIZU
        # Ergebnis: Tabelle mit Häufigkeiten von Wortpaaren (s, w), wobei s entweder "Staat" oder "Kind" und w Kontextwort
def extract_pair_freq(file):
    with open(file, mode="r", encoding="utf-8") as data:
        clean_data = []
        for line in data.readlines():
            line = line.strip()
            line = re.sub('(?<=\\d) (?=\\d)','', line)
            line = re.sub('(?<=\\d) - (?=\\d)', '-', line)
            line = re.sub('(?<=\\d) / (?=\\d)', '/', line)
            line = re.sub(r'\s+', ' ', line)
            line = line.split(" ")
            clean_data.append(line)

        pair_freq_dict = defaultdict(int)
        for idx, (_, tag, lemma) in enumerate(clean_data):
            if lemma == "Kind" or lemma == "Staat":
                # Kontext = 50 Lemmas vor und nach "Staat" oder "Kind"
                startpos = max(0, idx - 50)
                endpos = min(idx+51, len(clean_data))
                for context_idx in range(startpos, endpos):
                    # Mit Set ist es effizienter
                    if (context_idx != idx
                        and clean_data[context_idx][1] in {"ADJA", "ADJD", "ADV", "NE", "NN", "VVFIN", "VVINF", "VVPP", "VVIZU"}):
                        pair_freq_dict[lemma, clean_data[context_idx][2]] += 1
    return pair_freq_dict


# Schritt 2: geglättete (Witten-Bell) bedingte Wahrscheinlichkeiten der Kontextwörter w schätzen
def save_params(pair_freq_dict, params_file):
    # a(s) = Zahl der unterschiedlichen Inhaltswörter, die in Nachbarschaft von s auftauchen
    a_sets = {"Staat": set(), "Kind": set()}

    # Iteriere über alle extrahierten Wortpaare und berechne f_1(s) und f_2(w) als Summe von Worthäufigkeiten
    f_1 = defaultdict(int)
    f_2 = defaultdict(int)
    for (s, w), freq in pair_freq_dict.items():
        # f_1(s) = Summe für alle w: f(s, w)
        f_1[s] += freq
        # allgemeine Worthäufigkeit: f_2(w) = f(Staat, w) + f(Kind, w)
        f_2[w] += freq
        a_sets[s].add(w)
    a = {s: len(w_list) for s, w_list in a_sets.items()}
    # Gesamthäufigkeit: N = f_1(Staat) + f_1(Kind)
    N = sum(f_1.values())
    # W. von Inhaltswörtern: p(w) = f_2(w) / N
    p = {w: f_2[w] / N for _, w in list(set(pair_freq_dict.keys()))}
    p_cond = {"Staat": {}, "Kind": {}}
    # Iteriere noch einmal über extrahierten Wortpaare und berechne p(w|s)
    for (s, w), freq in pair_freq_dict.items():
        # geglättete bedingte W: p(w|s) = (f(s,w) + a(s)*p(w)) / (f_1(s) + a(s))
        p_cond[s][w] = (freq + a[s] * p[w]) / (f_1[s] + a[s])
    # Schritt 3: Parameter in einer Datei speichern
    with open(params_file, "w") as output:
        json.dump(p_cond, output)

# Teil 2: Testung des Desambiguierers, der Daten klassifiziert
def pseudoword_test(p_cond_file, file):
    # Eingabe: zwei Dateinamen. 1 = Modellparameter; 2 = zu desambiguierender Text
    with open(p_cond_file, mode="r", encoding="utf-8") as training:
        p_cond = json.load(training)
    with open(file, mode="r", encoding="utf-8") as test:
        clean_data = []
        tag = []
        lemma = []
        for line in test.readlines():
            line = line.strip()
            line = re.sub('(?<=\\d) (?=\\d)', '', line)
            line = re.sub('(?<=\\d) - (?=\\d)', '-', line)
            line = re.sub('(?<=\\d) / (?=\\d)', '/', line)
            line = re.sub(r'\s+', ' ', line)
            line = line.split(" ")
            # Für Testdaten werden "Kind" und "Staat" durch Pseudowort "Kind:Staat" ersetzt
            if line[2] == "Staat" or line[2] == "Kind":
                line[2] = "Staat:Kind"
            tag.append(line[1])
            lemma.append(line[2])
            clean_data.append(line)

    # Ausgabe: Produkt von bed. W. für alle Wörter in Kontextwortliste unter Voraussetzung der Klasse
    disambiguation_dict = {}
    for idx, word in enumerate(lemma):
        if word == "Staat:Kind":
            disambiguation_dict[idx] = {"Staat": [], "Kind": []}
            startpos = max(0, idx - 50)
            endpos = min(idx + 51, len(clean_data))
            for context_idx in range(startpos, endpos):
                if tag[context_idx] in ["ADJA", "ADJD", "ADV", "NE", "NN", "VVFIN", "VVINF", "VVPP", "VVIZU"]:
                    disambiguation_dict[idx]["Staat"].append(p_cond["Staat"].get(lemma[context_idx], 1))
                    disambiguation_dict[idx]["Kind"].append(p_cond["Kind"].get(lemma[context_idx], 1))
            disambiguation_dict[idx]["Staat"] = prod(disambiguation_dict[idx]["Staat"])
            disambiguation_dict[idx]["Kind"] = prod(disambiguation_dict[idx]["Kind"])
            # Extra Parameter dient dazu, dass die Funktion wie argmax wirkt: Extrahiert Schlüssel mit maximalem Wert
            disambiguation_dict[idx]["best_sense"] = max(disambiguation_dict[idx], key = disambiguation_dict[idx].get)
    return disambiguation_dict



# Aufgabe 1
# pair_freq_dict = extract_pair_freq("../Data/zeit-10M-tagged")
# save_params(pair_freq_dict, "../Data/zeit-params.json")

# Aufgabe 2
disambiguation = pseudoword_test("../Data/zeit-params.json", "../Data/zeit-10M-tagged")
print(list(disambiguation.items())[:20])