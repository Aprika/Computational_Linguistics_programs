from math import log
from collections import defaultdict

class Parser:
    def __init__(self, grammar, lexicon):
        self.gramrules = self.read_file(grammar)
        self.lexrules = self.read_file(lexicon)
        self.logvitprob = [dict()]

    def read_file(self, input_file):
        """
        Reads the grammar or lexicon file. Saves grammar in a dictionary of lists.
        :param input_file:
        :return rules: List of logarithmic probabilities of rules with key as the first right side symbol.
        """
        # Example appending
        # rules['DT'].append(('NP', ('DT', 'N1'), log(0,2)))
        rules = defaultdict(list)
        with open(input_file, 'r') as file:
            for line in file:
                prob, lhs, *rhs = line.split()  #lhs = left hand side, rhs = right hand side
                rules[rhs[0]].append((lhs, rhs, log(float(prob))))

        return rules

    def add(self, item, child = None, logprob):  # Hier kann man add auch nach den 3 Operationen einfügen, da es Teil derselben Klasse ist
        """
        Adds a punkt rule to the Chart. If the rule already exists, add only if the prob is larger.
        If a newly added rule has the point at the end, the function calls the functions predict and complete
        :param item: The new Chart entry (punkt rule).
        :param child: Complete Chart entry on which predict of complete was called to create item. If the operation is scan, child = None (punkt rule).
        :param logprob:
        :return:
        """
        # logvitprob[endpos][item] = logprob
        # childitem[endpos][item] = child
        lhs, rhs, dotpos, startpos, endpos = item
        if self.logvitprob[endpos].get(item, -float('inf')) < logprob: # wenn dieses Item nicht existiert, ist das per Default wahr
            self.logvitprob[endpos][item] = logprob
            self.childitem[endpos][item] = child
            if dotpos == len(rhs):    # Wenn Punkt am Ende steht, müssen diese Funktionen neu aufgerufen werden (Rekursion)
                self.predict(item, logprob)
                self.complete(item, logprob)

    def scan(self, i, word):
        """
        Looks up fitting lexical rules for the word. Uses the add function to add the rules into the Chart
        :param i: Position of word 1 in text
        :param word: Given word
        :return:
        """
        # Example: if word "man" is the second word of the sentence
        # self.add(('N', ('man'), 1, 1, 2), log(0.1)
        for lhs, rhs, logprob in self.lexrules[word]:  # Wenn keine Regel gefunden, wird eine leere Liste in defaultdict eingetragen
            # ((left rule side, right rule side, point position (always first here), start position, end position), log prob)
            self.add((lhs, rhs, 1, i, i+1), logprob, None)


    def predict(self, child, logprob):
        """
        Adds all rules into the Chart, where the right side starts with child.
        :param child: The POS to look for on the right side of the rule
        :param logprob:
        :return:
        """
        # Example: if NP from position 0 to 2 is given and a rule S -> NP VP exists
        # You get the new probability p by adding the log-prob of the rule to the log-viterbi-prob of NP
        # self.add(('S', ('NP', 'VP'), 1, 0, 2), p)

        cat, _, _, startpos, endpos = child
        for lhs, rhs, lp in self.gramrules[cat]:  # Wenn keine Regel gefunden, wird eine leere Liste in defaultdict eingetragen
            # ((left rule side, right rule side, point position (always first here), start position, end position), log prob)
            self.add((lhs, rhs, 1, startpos, endpos), logprob+lp, child)

    def complete(self, child, logprob):
        """
        Completes partially recognised consituents that expect the category of the child constituent next
        :param child: The POS that has to be expected next in other rules
        :param logprob:
        :return:
        """
        # Example: adds a completely recognized S-constituent after combining these partials:
        # 0 to 1 = ('S', ('NP', 'VP'), 1, 0, 2)
        # 2 to 8 starts with VP on the left side (in position 2)
        # Probability p = sum of log-probs of both of the combined chart entries
        # self.add(('S', ('NP', 'VP'), 2, 0, 8), p)

        cat, _, _, startpos, endpos = child
        for (lhs, rhs, dotpos, spos, _), lp, in self.logvitprob[startpos].items()  # Endposition identisch zur Startposition
            # Prüfen, ob Regel passt
            if dotpos < len(rhs) and rhs[dotpos] == cat:
                self.add((lhs, rhs, dotpos, spos, endpos), logprob+lp, child)

    def parse(self, words):
        """
        Initialises the Chart. Calls the scan-function for each input word one by one.
        Once the last scan is finished, the sentence is completely parsed.
        Then the graph in logvitprob is scanned top-down to search for the most probable item in logvitprob[-1] with lhs = 'S' and startpos = 0
        :param words: Input sentence
        :return:
        """
        self.logvitprob = [dict() for _ in range(len(words) + 1)]
        self.childitem = [dict() for _ in range(len(words) + 1)]
        for i, word in enumerate(words):
            self.scan(i, word)
        best_item = None
        best_logprob = -float('inf')
        for (lhs, rhs, dotpos, startpos, endpos), logprob in self.logvitprob[
            -1].items():  # iterate over all rules in last column
            if lhs == "S" and startpos == 0 and dotpos == len(rhs):
                if best_logprob < logprob:
                    best_logprob = logprob
                    best_item = (lhs, rhs, dotpos, startpos, endpos)
        tree = self.buld_tree(best_item)
        print(tree)


    def build_tree(self, item):
        """
        Recursive function that returns the partial tree for the punkt rule item.
        Gets a partial tree for every recursive call and combines them in the end to output.
        Output is in bracket form.
        :param words: Punkt rule
        :return partial_tree: Corresponding partial tree to the punkt rule
        """
        # Example output:
        # (S (NP (DT the)(N1 (N man)))(VP (V slept)))

        lhs, rhs, dotpos, startpos, endpos = item
        child = self.childitem[endpos][item]
        if child is None:
            return f'({lhs} {rhs[0]})'
        subtree = self.build_tree(child)
        if dotpos > 1:
            subtree2 = self.build_tree((lhs, rhs, dotpos-1, startpos, child[-1]))
            subtree = subtree2 + subtree
        if dotpos == len(rhs):
            subtree = f'({lhs} {subtree})'
        return subtree


if __name__ == '__main__':
    grammar, lexicon, testfile = sys.argv[:-1]
    parser = Parser(grammar, lexicon)
    with open(testfile) as file:
        for line in file:
            words = line.split()
            print(*words)
            print(parser.parse(words))



