from collections import defaultdict
import sys

# System call: python earley.py grammar.txt lexicon.txt sentences.txt

class Parser:
    def __init__(self, gram_file, lex_file):
        self.grammar = self.read_grammar(gram_file)
        self.lexicon = self.read_lexicon(lex_file)
        self.chart = defaultdict(set)
        self.predicted = set()
        self.completed = set()

    def read_grammar(self, gram_file):
        """
        Creates a grammar dictionary from the grammar file
        :param gram_file: text file with grammar rules
        :return grammar: defaultdict[set]
        """
        grammar = defaultdict(set)
        with open(gram_file, 'r') as gram:
            for line in gram:
                split_grammar = line.strip().split(' ')
                left, right = split_grammar[0], " ".join(split_grammar[1:])
                grammar[left].add(right)
        return grammar

    def read_lexicon(self, lex_file):
        """
        Creates a lexicon dictionary from the lexicon file
        :param lex_file: text file with lexicon rules
        :return lexicon: defaultdict[set]
        """
        lexicon = defaultdict(set)
        with open(lex_file, 'r') as gram:
            for line in gram:
                split_grammar = line.strip().split(' ')
                left, right = split_grammar[0], split_grammar[1:]
                for terminal in right:
                    lexicon[left].add(terminal)
        return lexicon

    def add(self, rule, startpos, endpos):
        """
        Adds a punkt rule to the chart. Calls corresponding functions afterward
        :param rule: punkt rule to be added
        :return: None
        """
        # TODO: The bug is most likely to be here. Some of the indexes are way out of range
        # rule format: (left, right)
        left, right = rule
        if rule not in self.chart[left, startpos, endpos]:
            # chart format: (left, startpos, endpos) -> set(rules)
            self.chart[left, startpos, endpos].add(right)

            length = endpos - startpos
            right = right.split()
            if length != len(right):
                self.predict(right[length-1], startpos)
            else:
                self.complete(left, startpos, endpos)

    def scan(self, word, pos):
        """
        Reads the next input word and looks up possible word types in the lexicon. Calls add for each found word type
        :param word:
        :return: None
        """
        word_types = self.lexicon[word]
        for type in word_types:
            self.add((type, word), pos, pos)

    def predict(self, X, i):
        """
        Called when the punkt is in front of a nonterminal. Searches for all possible grammar rules for the next nonterminal after the point. Adds every grammar rule of the form (X -> . alpha, i, i) into the chart.
        :param X: nonterminal
        :param i: position of the nonterminal in the sentence
        :return: None
        """
        if (X, i) in self.predicted:
            return
        else:
            self.predicted.add((X, i))
            nonterminal_rules = self.grammar[X]
            for rule in nonterminal_rules:
                self.add((X, rule), i, i)

    def complete(self, Y, m, e):
        """
        Called when the punkt is at the end of a rule. Searches all chart rules of the form (X -> [...] . Y [...], s, m) and combines the two of them into one (with point moved)
        :param Y: nonterminal
        :param m: start position
        :param e: end position
        :return: None
        """
        if (Y, m, e) in self.completed:
            return
        else:
            self.completed.add((Y, m, e))
            completions = {(left, startpos, e): rule for (left, startpos, endpos), rule in self.chart.items() if Y in rule and endpos == m}
            self.chart.update(completions)

    def parse(self, word_list):
        """
        Earley Parser method. Makes the first predict call with the start symbol and then the scan method with every word. Returns True if a complete parse was found and False if it was not.
        :param word_list: List of words in the current sentence to be parsed
        :return: bool
        """
        self.predict("S", 0)
        for idx, word in enumerate(word_list):
            self.scan(word, idx+1)
        print(self.chart.items())
        if self.chart["S", 0, len(word_list)]:
            return True
        return False


if __name__ == '__main__':
    grammar_file, lexicon_file, sentences_file = sys.argv[1], sys.argv[2], sys.argv[3]
    parser = Parser(grammar_file, lexicon_file)
    with open(sys.argv[3], 'r', encoding='utf-8') as sentences_file:
        for sentence in sentences_file:
            print(f"{sentence}: {parser.parse(sentence)}")