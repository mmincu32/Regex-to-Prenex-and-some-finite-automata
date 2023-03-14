from __future__ import annotations
from builtins import print
from typing import Type


from BTree import BTreeNode
from DFA import DFA
from NFA import NFA

class Parser:
    # This function should:
    # -> Classify input as either character(or string) or operator
    # -> Convert special inputs like [0-9] to their correct form
    # -> Convert escaped characters
    # You can use Character and Operator defined in Regex.py
    @staticmethod
    def preprocess(regex: str) -> list:
        pass

    # This function should construct a prenex expression out of a normal one.
    @staticmethod
    def toPrenex(s: str) -> str:
        s = s.replace("\'", "")     #to get rid of escapes
        s = s.replace("[0-9]", "(0|1|2|3|4|5|6|7|8|9)")     #transform [0-9]
        s = s.replace("[a-z]", "(a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z)")     #transform [a-z]
        s = s.replace("[A-Z]", "(A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z)")     #transform [A-Z]
        if s == "eps" or s == "void" :
            return s
        s = '(' + s + ')'
        tree = BTreeNode.buildExpTree(s)
        res = BTreeNode.preorder(tree)
        return res[:-1]
