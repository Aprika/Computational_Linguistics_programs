import sys

# System call for building tree: python build-tree.py wordlist.txt > tree.txt

def add(word, transition, counter, node=0):
    if len(word) == 1:
        if transition.get(node) is None:
            transition[node] = {}
        if word in transition[node]:
            if transition[node][word][1] is not True:
                end_node, _ = transition[node][word]
                transition[node][word] = (end_node, True)
                return counter
        else:
            counter += 1
            transition[node][word] = (counter, True)
            return counter
    else:
        if transition.get(node) is None:
            transition[node] = {}
        if transition[node].get(word[0]):
            node = transition[node][word[0]][0]
            counter = add(word[1:], transition, counter, node)
            return counter
        else:
            counter += 1
            transition[node][word[0]] = (counter, False)
            node = counter
            counter = add(word[1:], transition, counter, node)
            return counter

def read_into_file(transition, text="" , node=0):
    # Move the resulting Data structure to a file. The given function call moves all printouts into tree.txt
    # Format of the tree: list of edges
    for letter in transition[node]:
        end_node, is_last = transition[node][letter]
        if is_last:
            print(text + str(node) + "\t" + letter + "\t" + str(end_node) + "\n" + str(end_node))
        else:
            read_into_file(transition, text + str(node) + "\t" + letter + "\t" + str(end_node) + "\n", end_node)

transition = {0: {}}

# read Data from the file from cmd
filename = sys.argv[1]
with open(filename, "r", encoding='utf-8') as f:
    count = 0
    for line in f:
        line = line.strip()
        count = add(line, transition, count)

read_into_file(transition)
