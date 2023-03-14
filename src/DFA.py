import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from typing import Callable, Generic, TypeVar
from NFA import NFA

S = TypeVar("S")
T = TypeVar("T")


class DFA(Generic[S]):

    def __init__(self, states, alphabet, delta, initState, finalStates):
        self.states = states
        self.alphabet = alphabet
        self.delta = delta
        self.initState = initState
        self.finalStates = finalStates

    def map(self, f: Callable[[S], T]) -> 'DFA[T]':
        # pass
        deltaaux = self.delta.copy()
        finaldelta = {}
        for (s, c) in self.delta:
            sd = deltaaux[(s, c)]
            del deltaaux[(s, c)]
            finaldelta[(f(s), c)] = f(sd)
        return DFA[T]({f(s) for s in self.states}, self.alphabet, finaldelta,
                      f(self.initState), {f(s) for s in self.finalStates})

    def next(self, from_state: S, on_chr: str) -> S:
        for key in self.delta:
            if key == (from_state, on_chr):
                return self.delta[key]
        return -1

    def getStates(self) -> 'set[S]':
        return self.states

    def acceptsFromState(self, str: str, state: S, steps: int) -> bool:
        if steps == 100:  # to avoid loops we put a limit for recursion steps
            return False
        if str == "" and self.isFinal(state):
            return True
        res = False
        if len(str) > 0:
            res = res or self.acceptsFromState(str[1:], self.next(state, str[0]), steps + 1)
        return res

    def accepts(self, str: str) -> bool:
        return self.acceptsFromState(str, self.initState, 0)

    def isFinal(self, state: S) -> bool:
        return state in self.finalStates

    @staticmethod
    def fromPrenex(str: str) -> 'DFA[int]':
        N = NFA.fromPrenex(str)
        # N=NFA({0,1,2,3},{"A","B"},{(0,"A"):{1}, (0,"B"):{1,2}, (1,"B"): {0}, (1,"A"): {3},
        # (1,"eps"): {2}, (2,"B"):{3}, (3,"A"):{2,3},(3,"eps"):{0}},0,{3})
        E = []
        for state in N.states:
            E.append(N.getEpsClosure(state, 0))
        # print(E)
        Dstates = []
        Ddelta = {}
        k = 0
        count = 0
        Dfinal = []
        lst = [E[N.initState]]
        ok = True
        # print(N.alphabet)
        while count < len(lst):
            e = lst[count]
            # print("e = ")
            # print(e)
            # value = set()
            if tuple(e) not in Dstates:
                Dstates.append(tuple(e))
            # k = k + 1
            count = count + 1
            for s in e:
                for c in N.alphabet:
                    # print(s)
                    # print(c)
                    value = set()
                    for t in N.next(s, c):
                        # print(E[t])
                        value = value | E[t]
                    # print(value)
                    if (tuple(e), c) in Ddelta:
                        Ddelta[(tuple(e), c)] = Ddelta[(tuple(e), c)] | value
                    elif value != set():
                        Ddelta.update({(tuple(e), c): value})
                # print(Ddelta)

                for c in N.alphabet:
                    if (tuple(e), c) in Ddelta and Ddelta[(tuple(e), c)] not in lst:
                        # print(Ddelta[(tuple(e), c)])
                        lst.append(Ddelta[(tuple(e), c)])
                # print(lst)
            # print(lst)
        for key in Ddelta:
            Ddelta[key] = tuple(Ddelta[key])
            if Ddelta[key] not in Dstates:
                Dstates.append(Ddelta[key])
        fstate = N.finalStates.pop()
        N.finalStates.add(fstate)
        for v in Dstates:
            for s in v:
                if s == fstate and tuple(v) not in Dfinal:
                    Dfinal.append(tuple(v))
        return DFA(Dstates, N.alphabet, Ddelta, tuple(E[N.initState]), Dfinal).map(lambda x: Dstates.index(x))
