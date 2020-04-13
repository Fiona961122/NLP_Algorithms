"""
    this module builds the default grammar rules
"""
from collections import defaultdict

def get_grammar(file):
    grammar = defaultdict(dict)
    with open(file, "r") as f:
        line = f.readline().strip()
        while line:
            tag, result, p = line.split(",")
            grammar[tag.strip()][tuple(result.strip().split())] = float(p)
            line = f.readline()
    return grammar

if __name__ == "__main__":
    print(get_grammar("rules.txt"))