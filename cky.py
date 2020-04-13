"""
    This module implements the CKY algorithm
"""

import numpy as np
from collections import defaultdict

from NLP_Algorithms.grammar import get_grammar


class CKY:
    GRAMMAR = 'rules.txt'  # defalut path of grammar rules
    def __init__(self):
        """
        initialize the CKY object with grammar rules
        :param grammarfile: path of the grammar rules file
        """
        self.grammar = get_grammar(self.GRAMMAR)
        self.tag_dict = defaultdict(int)
        self.tag_dict_r = dict()
        self.table = None
        self.back = None
        self.get_tag_dict()


    def build(self, words):
        """

        :param words: list of words
        :return:
            table: np matrix with three dimension
            back: list of list (three dimensions) with element of (k, tag1, tag2)
        """
        table = np.zeros((len(words) + 1, len(words) + 1, len(self.grammar)))
        back = table.tolist()
        for x in range(len(words)):
            word = "'{}'".format(words[x])
            i = x + 1
            # get the initial prob from tag to word
            for j in range(len(self.grammar)):
                table[i - 1, i, j] = self.grammar[self.tag_dict_r[j]].get((word, ), 0)
                # get the unary transition
                if table[i - 1, i, j] != 0:
                    for tag, next_dict in self.grammar.items():
                        inx = self.tag_dict[tag]
                        for next_tag, p in next_dict.items():
                            if len(next_tag) == 1 and self.tag_dict.get(next_tag[0], -1) == j:
                                table[i - 1, i, inx] = p * table[i - 1, i, j]
                                back[i - 1][i][inx] = (0, j, )

            for j in range(i-2, -1, -1):
                for k in range(j+1, i):
                    for tag, next_dict in self.grammar.items():
                        inx = self.tag_dict[tag]
                        for next_tag, p in next_dict.items():
                            if len(next_tag) == 2:
                                inx1, inx2 = self.tag_dict[next_tag[0]], self.tag_dict[next_tag[1]]
                                if table[j, k, inx1] > 0 and table[k, i, inx2] > 0 and table[j, i, inx] < p * table[j, k, inx1] * table[k, i, inx2]:
                                    table[j, i, inx] = p * table[j, k, inx1] * table[k, i, inx2]
                                    back[j][i][inx] = (k, inx1, inx2)

        self.table = table
        self.back = back

    def get_tag_dict(self):
        """
        build the tag dict mapping from tag to index and the reversed tag dict
        """
        for index, tag in enumerate(self.grammar):
            self.tag_dict[tag] = index
            self.tag_dict_r[index] = tag

    def build_tree(self, row, col, inx):
        """
        build tree compatible for latex qtree
        :param row: index of row
        :param col: index of column
        :param inx: index of tag
        :return:
        """
        pointer = self.back[row][col][inx]
        if pointer == 0.0:
            return " [." + self.tag_dict_r[inx] + " " + words[col - 1] + " ]"
        if len(pointer) == 2:
            return " [." + self.tag_dict_r[inx] + self.build_tree(row, col, pointer[1]) + "]"
        return "[." + self.tag_dict_r[inx] + self.build_tree(row, pointer[0], pointer[1]) + "\n" + self.build_tree(pointer[0], col, pointer[2]) + "]"

    def generate_table(self, words):
        """
        generate back table in latex form
        :param words: list of words
        :return: the table
        """
        head = "\\begin{{tabular}}{{|{}}}\n\n".format("c|"*len(words))
        head += " & ".join(["\multicolumn{{1}}{{c}}{{{}}}".format(words[i]) for i in range(len(words))])
        head += "\\\\\n"

        for i in range(len(words)):
            if i == 0:
                line = "\hline\n{} \\\\\n" + "\hline\n"
            else:
                line = "\multicolumn{{{{{}}}}}{{{{c|}}}}{{{{}}}} & ".format(i) + "{}" + " \\\\\n\\cline{{{{{}-{}}}}}\n".format(i+1, len(words))
            args = []
            pointers = self.back[i]
            for j in range(i + 1, len(words) + 1):
                ans = []
                for k in range(len(self.tag_dict)):
                    pointer = pointers[j][k]
                    if pointer != 0:
                        if len(pointer) == 2:
                            ans.append("{0}: {1}".format(self.tag_dict_r[k], self.tag_dict_r[pointer[1]]))
                        else:
                            ans.append("{0}: {1},{2},{3}".format(self.tag_dict_r[k], pointer[0] - 1,
                                                                                self.tag_dict_r[pointer[1]],
                                                                                self.tag_dict_r[pointer[2]]))
                if len(ans) == 0:
                    output = "•"
                elif len(ans) == 1:
                    output = ans[0]
                else:
                    output = "\\begin{tabular}[c]{@{}l@{}}" + "\\\\ ".join(ans) + "\end{tabular}"
                args.append(output)
            head += line.format(" & ".join(args))
        head += "\end{tabular}\\\\\\\\\\"

        return head



if __name__ == "__main__":
    cky = CKY()
    words = "time flies like an arrow".split()
    cky.build(words)
    print(cky.build_tree(0, len(words), cky.tag_dict["S"]))
    print(cky.generate_table(words))
