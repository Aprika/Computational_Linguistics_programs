# Übung 8: Wortart-Tagger (Anwendung)

from collections import defaultdict
from math import log
from Uebung_7 import get_suffix
import pickle

class HMMTagger:
    def __init__(self, filename):
        with (open(filename, "rb") as file):
            suffix_len, apriori_tag_prob, word_tag_probs, suffix_tag_probs, tag_ngram_prob = pickle.load(file)
        self.suffix_len = suffix_len
        self.apriori_tag_prob = apriori_tag_prob
        self.word_tag_probs = word_tag_probs
        self.suff_tag_probs = suffix_tag_probs
        self.tag_ngram_prob = tag_ngram_prob
        self.word_tag_backoff = self.backoff_factors(self.word_tag_probs)
        print(f"Word Tag Alphas: {list(self.word_tag_backoff.items())[:20]}")
        self.suff_tag_backoff = self.backoff_factors(self.suff_tag_probs)
        print(f"Suffix Tag Alphas: {list(self.suff_tag_backoff.items())[:20]}")
        self.tag_ngram_backoff = self.backoff_factors(self.tag_ngram_prob)
        print(f"Tag Ngram Alphas: {list(self.tag_ngram_backoff.items())[:20]}")

    @staticmethod
    def backoff_factors(prob_dict):
        """
        backoff[context] = 1 - sum(prob[context][t])
        :param prob_dict: Dictionary of Dictionaries mit Wahrscheinlichkeiten
        :return backoff_dict: Dictionary mit Backoff-Faktoren
        """
        backoff_dict = {}
        for context, tags in prob_dict.items():
            backoff_dict[context] = 1 - sum([prob for prob in tags.values()])
        return backoff_dict

    def compute_suffix_prob(self, suff, tag):
        """
        Rekursive Berechnung der Suffixwahrscheinlichkeit:
        p(tag|a1, ..., ak, g) = p*(tag|a1, ..., ak) + alpha(a1, ..., ak, g) * p(tag|a2, ..., ak, g)
        p(tag|g) = p*(tag|g)
        :param suff: Suffix a1, ..., ak, g
        :param tag: Tag
        :return suffix_prob: Wahrscheinlichkeit von Tag gegeben Suffix
        """
        if len(suff) == 1:
            return self.suff_tag_probs[suff].get(tag, 0.0)
        p = self.compute_suffix_prob(suff[1:], tag)

        try:
            return self.suff_tag_probs[suff].get(tag, 0.0) + self.suff_tag_backoff[suff] * p
        except KeyError:
            return p



    def compute_word_prob(self, word, tag):
        """
        Berechnet mit Hilfe der Funktionen get_suffix und compute_suffix_prob
        für ein Wort und ein Tag die bedingte Wahrscheinlichkeit p(tag|word)
        p(tag|word) = p*(tag|word) + alpha(word) * p(tag|get_suffix(word))
        :param word:
        :param tag:
        :return word_prob: Wahrscheinlichkeit von Tag gegeben Wort
        """
        p = self.compute_suffix_prob(get_suffix(word, self.suffix_len), tag)
        try:
            return self.word_tag_probs[word].get(tag, 0.0) + self.word_tag_backoff[word] * p
        except KeyError:
            return p

    def lex_probs(self, word):
        """
        Berechnet für ein Wort die Menge der Tags mit einer W > 0.001.
        Gibt diese als Dictionary (key = Tag, val = W) zurück
        :param word: Eingabewort
        :return lex_prob_dict: Dictionary von Tagwahrscheinlichkeiten für ein Wort
        """
        if word == "":
            return {'</s>': 1.0}
        tag_prob = {tags: self.compute_word_prob(word, tags) for tags in self.apriori_tag_prob.keys()}
        return {tag: log(p) for tag, p in tag_prob.items() if p > 0.001}


    def context_prob(self, context, tag):
        """
        Gibt für ein Tag-Trigramm seine geglättete Kontextwahrscheinlichkeit zurück
        :param context: erste zwei Tags im Trigramm
        :param tag: drittes Tag im Trigramm
        :return context_prob: geglättete Kontext-W
        """
        if len(context) == 1:
            return self.tag_ngram_prob[context][tag]
        p = self.context_prob(context[1:], tag)
        try:
            return self.tag_ngram_prob[context].get(tag, 0.0) + self.tag_ngram_backoff[context] * p
        except KeyError:
            return p

    def viterbi(self, sentence):
        """
        Gibt für einen Satz die wahrscheinlichste Tagfolge zurück.
        :param sentence: Satz (Token-Liste)
        :return max_tag_seq: Wahrscheinlichste Tagfolge
        """
        words = [''] + sentence + ['', '']
        logvitprob = [{} for _ in words]  # Logarithmus der besten Viterbi-W (Delta)
        bestprev = [{} for _ in words]  # bester Vorgängertag (Psi)
        for i, word in enumerate(words):
            if i == 0:
                logvitprob[i]['<s>', '<s>'] = 0.0
            else:
                for tag, lprob in self.lex_probs(word):  # Iterieren über alle wahrscheinlichsten Tags für i: lex_probs
                    for (tag1, tag2), prev_logp in logvitprob[i-1].items():
                        logp = prev_logp + log(lprob * self.context_prob((tag1, tag2), tag)) / self.apriori_tag_prob[tag]

                        if logvitprob[i][tag2, tag] < logp:
                            logvitprob[i][tag2, tag] = logp
                            bestprev[i][tag2, tag] = (tag1, tag2)
        best_tags = []
        tagpair = '</s>', '</s>'
        for i in range(len(words)-1, 2, -1):
            tagpair = bestprev[i][tagpair]
            best_tags.append(tagpair[0])

        return best_tags[::-1]






if __name__ == "__main__":
    # Hauptfunktion
    with open("../Data/viterbi_test.txt", "r", encoding="utf-8") as file:
        texts = file.readlines()

    test_sents = []
    for sent in texts:
        test_sents.append(sent.strip().split(" "))
    print(test_sents)

    tagger = HMMTagger("../Data/viterbi_params.pickle")

    for sent in test_sents:
        best_tags = tagger.viterbi(sent)
        print(best_tags)


    # logvitprob = {}
    # logvitprob[0][('<s>', '<s>')] = log(1)

    # TODO: Über alle Wortpositionen i = 1, ..., n+1 iterieren
    # TODO: Für alle Tags t im Tagset W p(t|wi) berechnen (Übung 6)

