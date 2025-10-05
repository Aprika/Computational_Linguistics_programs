# Übung 7: Wortart-Tagger (Training)

from collections import defaultdict, Counter
import pickle

def get_suffix(word, s_len):
    """
    :param word: input word
    :param s_len: suffix length
    :return: word suffix of length s_len
    """
    if len(word) < s_len:
        suffix = " " * (s_len-len(word)) + word
    else:
        suffix = word
    suffix = suffix[:s_len]
    if word.isalpha():
        if word.islower():
            suffix = suffix + "k"
        else:
            suffix = suffix + "g"
    else:
        suffix = suffix + "o"
    return suffix


def read_corpus(filename, suffix_len):
    """
    :param filename: Dateipfadread (str)
    :param: suffix_len: Suffix length (int)
    :return: Tag-Wahrscheinlichkeits-Dict und Wort-Tag-Wahrscheinlichkeits-Dict ((dict, dict))
    """
    word_tag_freq = {}
    words, tags = [], []
    tag_ngram_freq = {}
    suff_tag_freq = {}
    with open(filename, "r", encoding="utf-8") as text:
        for line in text:
            line = line.strip()
            if len(line.split("\t")) == 2:
                word, tag = line.split("\t")
                words.append(word)
                tags.append(tag)
            else:
                for w, t in zip(words, tags):
                    # Get suffix from word
                    suffix = get_suffix(word, suffix_len)

                    # Build word tag frequency dict
                    if not word_tag_freq.get(word):
                        word_tag_freq[word] = defaultdict(int)
                    word_tag_freq[word][tag] += 1

                    # Build suffix tag frequency dict
                    if not suff_tag_freq.get(suffix):
                        suff_tag_freq[suffix] = defaultdict(int)
                    suff_tag_freq[suffix][tag] += 1

                # Build tag trigram frequency dict
                tags = ['<s>', '<s>'] + tags + ['</s>', '</s>']
                for t1, t2, t3 in zip(tags, tags[1:], tags[2:]):
                    if not tag_ngram_freq.get((t1, t2)):
                        tag_ngram_freq[t1, t2] = defaultdict(int)
                    tag_ngram_freq[t1, t2][t3] += 1
                words, tags = [], []


        return word_tag_freq, tag_ngram_freq, suff_tag_freq


def compute_discount(freq_dict):
    """
    Compute discount for a context tag frequency dictionary
    :param freq_dict: Input tag frequency dictionary (word or suffix) (nested dict)
    :return: discount for that dictionary (int)
    """
    # Extraktion von Anzahlen von 1-Mal und 2-Mal aufgetretenen Werten
    once = len([freq for key in freq_dict for freq in freq_dict[key].values() if freq == 1])  # keys werden nicht benötigt
    twice = len([freq for key in freq_dict for freq in freq_dict[key].values() if freq == 2])

    # Berechnung von Discount
    if once > twice > 0:
        discount = once / (once + 2 * twice)
    else:
        discount = 0.5
    return discount


def estimate_probs(freq_dict, smoothing=True):
    """
    Compute relative frequencies p*(tag|context)
    :param freq_dict: context tag frequency dict (nested dict)
    :return:
    """
    discount = compute_discount(freq_dict) if smoothing else 0.0

    # Compute all sum(f(context, t')) in advance
    total_context_freqs = defaultdict(int)
    for context, tag in freq_dict.items():
        for tag, freq in freq_dict[context].items():
            total_context_freqs[context] += freq

    # Calculate p*(tag|context) = (f(context, tag) - discount) / sum(f(context, t'))
    rel_freq = {}
    for context, tag in freq_dict.items():
        for tag, freq in freq_dict[context].items():
            if not rel_freq.get(context):
                rel_freq[context] = defaultdict(float)
            rel_freq[context][tag] = (freq-discount) / total_context_freqs[context]

    return rel_freq


def reduced_context_freqs(context_tag_freq, n):
    """
    Calculate the frequency of smaller contexts. Smoothed with Kneser-Ney-Backoff
    :param context_tag_freq:
    :return: Context-tag dictionary for reduced suffix context
    """
    red_context_tag_freq = {}
    suffix_len = 5

    for context, tag in context_tag_freq.items():
        for tag, _ in context_tag_freq[context].items():
            context = context[n:]
            if not red_context_tag_freq.get(context):
                red_context_tag_freq[context] = defaultdict(int)
            red_context_tag_freq[context][tag] += 1
    check = list(red_context_tag_freq.items())[:20]
    print(f"Reduced context with n = {n}: {check}")
    return red_context_tag_freq


if __name__ == "__main__":
    """
    Word type tagger training main function
    :param data: Name of the data source
    :param suffix_len: Suffix length
    :return: estimated parameters for trigram HMM
    """
    data = "../Data/tiger.txt"
    suffix_len = 5
    word_tag_freq, tag_ngram_freq, suff_tag_freq = read_corpus(data, suffix_len)
    print(f"Word tag frequencies: {list(word_tag_freq.items())[:20]}")
    print(f"Tag ngram frequencies: {list(tag_ngram_freq.items())[:20]}")
    print(f"Suffix tag frequencies: {list(suff_tag_freq.items())[:20]}")
    word_tag_probs = estimate_probs(word_tag_freq)
    suff_tag_probs = estimate_probs(suff_tag_freq)
    for n in range(1, suffix_len+1):
        if n == suffix_len+1:
            #TODO: Add probs for suffix with only gko, but without smoothing
            suff_red_probs = estimate_probs(reduced_context_freqs(suff_tag_freq, n), smoothing=False)
            suff_red_probs.update(suff_tag_probs)
            suff_tag_probs = suff_red_probs
        else:
            suff_red_probs = estimate_probs(reduced_context_freqs(suff_tag_freq, n))
            suff_red_probs.update(suff_tag_probs)
            suff_tag_probs = suff_red_probs
    print(f"Word tag probabilities: {list(word_tag_probs.items())[:20]}")
    print(f"Suffix tag probabilities: {list(suff_tag_probs.items())[:20]}")

    # Taghäufigkeiten berechnen: freq[tag] += tag_ngram_freq[context][tag]
    tag_freq_dict = defaultdict(int)
    for tags in tag_ngram_freq.values():
        for tag, freq in tags.items():
            tag_freq_dict[tag] += freq

    print(f"Tag frequency dictionary: {list(tag_freq_dict.items())[:20]}")

    total_tag_freq = sum(tag_freq_dict.values())
    print(f"Total tag frequency: {total_tag_freq}")

    # Apriori-Tag-Wahrscheinlichkeiten: p(t) = freq(t) / sum(freq(t))
    apriori_tag_prob = {}
    for tag, freq in tag_freq_dict.items():
        apriori_tag_prob[tag] = freq / total_tag_freq

    print(f"Apriori Tag Probability: {list(apriori_tag_prob.items())[:20]}")

    # TODO: Tag-nGramm-Ws in einer Schleife über alle n-Gramm-Größen berechnen
    tag_ngram_prob = estimate_probs(tag_ngram_freq)
    for context in range(0, 2):
        if n == 0:
            tag_ngram_prob.update(estimate_probs(reduced_context_freqs(tag_ngram_freq, n), smoothing=False))
        else:
            suff_red_probs.update(estimate_probs(reduced_context_freqs(tag_ngram_freq, n)))

    print(f"Tag ngram probabilities: {list(tag_ngram_prob.items())[:20]}")

    # TODO: Daten mit pickle speichern
    with open("../Data/viterbi_params.pickle", "wb") as file:
        model = (5, apriori_tag_prob, word_tag_probs, suff_tag_probs, tag_ngram_prob)
        pickle.dump(model, file)


# TODO: Teil 1: Parameterschätzung
    # Apriori-W: p(t) = f(t) / sum(f(t'))
    # Kneser-Ney geglättete relative Kontext-W (vgl. Übung 3): p*(t|t',t''), p*(t|t''), p*(t)
    # Kneser-Ney Bachoff-geglättete Lexikalische W:
        # f(b(range(1, k+1))g, t): Wörter mit Endung b(range(1, k+1)) und Groß/Kleinschreibung g, die mit t getaggt sind
        # Falls ein Wort kürzer als die maximale Suffixlänge, den Anfang mit Leerzeichen auffüllen
        # g(w) = liefert "k" für kleingeschrieben, "g" für großgeschrieben, 0 sonst
        # p(t|w) = (f(w, t) - delta(6)) / (sum(f(w, t')) + alpha(w) p(t|a(range(n-4, n+1))g(w))
        # p(t|b(range(1, k+1))g, t') = (f(b(range(1, k+1))g, t)) - delta(k)) / (sum(f(b(range(1, k+1)g, t')) + alpha(b(range(1, k+1) p(t|b(range(2, k+1)g)  für 0 < k < 5
        # p(t|g) = (f(g, t)) / (sum(f(g, t'))