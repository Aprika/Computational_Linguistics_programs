import sys
# TODO: Add comments and descriptions

# System call: python hopcroft.py automaton.txt

class Automaton:
    def __init__(self, file):
        """
            Converts a trie into a finite state automaton. Each symbol in the alphabet has a transition to each symbol in the alphabet.
            :param file: Trie text file
            :return (transition, alphabet): finite state automaton (dictionary of dictionaries (like in exercise 3)) and alphabet.
            """
        # TODO: shorten the code + maybe make it more efficient?
        self.reduced_transition = {}
        self.new_final_states = []

        # Build alphabet = set of all existing symbols
        self.alphabet = set()
        with open(file, 'r', encoding="utf-8") as f:
            f_lines = f.readlines()
            for f_line in f_lines:
                line = f_line.strip().split("\t")
                if len(line) == 3:
                    self.alphabet.add(line[1])

            # Reconstruct edge dictionary
            self.transition = {0: {}, "?": {}}
            self.final_states = set()
            for f_line in f_lines:
                line = f_line.strip().split("\t")
                if len(line) == 3:
                    if not self.transition.get(int(line[0])):
                        self.transition[int(line[0])] = {line[1]: int(line[2])}
                    else:
                        self.transition[int(line[0])][line[1]] = int(line[2])
                else:
                    self.final_states.add(int(line[0]))

            # Add "Error" edges to complete the transtion dictionary
            self.max_id = max(int(f_line.strip().split("\t")[0]) for f_line in f_lines) + 1
            for letter in self.alphabet:
                self.transition["?"][letter] = "?"
                for index in range(self.max_id):
                    if not self.transition.get(index):
                        self.transition[index] = {}
                    if not self.transition[index].get(letter):
                        self.transition[index][letter] = "?"

    def split(self, left, letter, right):
        x_1 = set()
        for x in left:
            for y in right:
                if self.transition[x][letter] == y:
                    x_1.add(x)
        x_2 = left.difference(x_1)
        return x_1, x_2

    def minimize(self):
        """
            Uses the Hopcroft algorithm to reduce the automaton
            :return: Reduced automaton (with error state "?" removed in advance)
            """
        # Initialize the required Data structures
        w = set()
        p = set()
        f = self.final_states
        f_cap = set([x for x in range(self.max_id) if x not in self.final_states])
        p.add(frozenset(f))
        p.add(frozenset(f_cap))
        w.add(min(p, key=lambda x: len(x)))
        while not len(w) == 0:
            y = w.pop()
            for letter in self.alphabet:
                for x in list(p):
                    x_1, x_2 = self.split(x, letter, y)
                    if len(x_1) != 0 and len(x_2) != 0:
                        p = p.difference({frozenset(x)}).union({frozenset(x_1), frozenset(x_2)})
                        if x in w:
                            w = w.difference({frozenset(w)}).union({frozenset(x_1), frozenset(x_2)})
                        else:
                            w = w.union({min(frozenset(x_1), frozenset(x_2), key=lambda x: len(x))})

        orig_to_reduce_map = {}
        next_node = 1

        for gen_set in p:
            # New item inherits every transition from previous items
            if 0 in gen_set:
                # If 0 in item, then index is automatically 0
                new_idx = 0
            else:
                # If not, assign one of the available indices
                new_idx = next_node
                next_node += 1
            # If one of the items is in "finals", then its Boolean state is True
            if gen_set.intersection(self.final_states):
                self.new_final_states.append(str(new_idx))
            for item in gen_set:
                orig_to_reduce_map[item] = str(new_idx)

        for node in self.transition:
            for letter in self.transition[node]:
                end_node = self.transition[node][letter]
                if not end_node == "?":
                    start_idx = orig_to_reduce_map[node]
                    end_idx = orig_to_reduce_map[end_node]
                    if not self.reduced_transition.get(start_idx):
                        self.reduced_transition[start_idx] = {letter: (end_idx, (end_idx in self.new_final_states))}
                    else:
                        self.reduced_transition[start_idx][letter] = (end_idx, (end_idx in self.new_final_states))


    def print(self, filename):
        with open(filename, "w", encoding="utf-8") as f:
            for start_node, edges in self.reduced_transition.items():
                for char, (end_node, is_terminal) in edges.items():
                    f.write(f"{start_node}\t{char}\t{end_node}\n")
            for state in self.new_final_states:
                f.write(f"{state}\n")


# Command: python hopcroft.py automaton.txt
# Biggest end node with index under 100 = 98
file_name = sys.argv[1]
automat = Automaton("trie.txt")
automat.minimize()
automat.print(file_name)





