from typing import Callable, Generic, TypeVar

S = TypeVar("S")
T = TypeVar("T")

class NFA(Generic[S]):

	def __init__(self, states, alphabet, delta, initState, finalStates) :
		self.states = states
		self.alphabet = alphabet
		self.delta = delta
		self.initState = initState
		self.finalStates = finalStates
	
	@staticmethod
	def deltaUnion(delta1, delta2) :
		dUnion = delta1.copy()
		for key in delta2 :
			if key in dUnion :
				dUnion[key] = dUnion[key] | delta2[key]
			else: 
				dUnion.update({key: delta2[key]})
		return dUnion
	
	@staticmethod
	def NFAunion(N1: 'NFA[S]', N2: 'NFA[S]') -> 'NFA[S]' :
		return NFA[S](N1.states | N2.states, N1.alphabet | N2.alphabet, NFA.deltaUnion(N1.delta, N2.delta), 
                N1.initState, N2.finalStates)
	
	def map(self, f: Callable[[S], T]) -> 'NFA[T]':
		#pass
		deltaaux = self.delta.copy()
		finaldelta = {}
		for (s, c) in self.delta :
			sd = deltaaux[(s, c)]
			del deltaaux[(s, c)]
			finaldelta[(f(s), c)] = {f(x) for x in sd}
		return NFA[T]({f(s) for s in self.states}, self.alphabet, finaldelta,
                f(self.initState), {f(s) for s in self.finalStates})

	def next(self, from_state: S, on_chr: str) -> 'set[S]':
		for key in self.delta :
			if key == (from_state, on_chr) :
				return self.delta[key]
		return set()
      

	def getStates(self) -> 'set[S]':
		#pass
		return self.states

	def acceptsFromState(self, str: str, state: S, steps: int) -> bool:
		if steps == 100 :	#to avoid loops we put a limit for recursion steps
			return False
		if str == "" and self.isFinal(state):
			return True 
		res = False
		if len(str) > 0:
			for s in self.next(state, str[0]) :
				res = res or self.acceptsFromState(str[1:], s, steps + 1)
		for s in self.next(state, "eps") :
			res = res or self.acceptsFromState(str, s, steps + 1)
		return res

	def accepts(self, str: str) -> bool:
		return self.acceptsFromState(str, self.initState, 0)

	def isFinal(self, state: S) -> bool:
		return state in self.finalStates

	@staticmethod
	def parse(str: str) -> '[str, str]' :
		if (str.startswith("UNION")) == False and (str.startswith("CONCAT")) == False :
			return ["", ""]
		stack = []
		popped = False
		e1 = ""
		e2 = ""
		strpop = ""
		s = ""
		while True :

			if str.startswith("UNION") and popped == False :
				stack.append(["UNION", "", ""])
				str = str[6:]

			elif str.startswith("CONCAT") and popped == False :
				stack.append(["CONCAT", "", ""])
				str = str[7:]

			elif str.startswith("STAR") and popped == False :
				stack.append(["STAR", ""])
				str = str[5:]

			elif str.startswith("PLUS") and popped == False :
				stack.append(["PLUS", ""])
				str = str[5:]

			elif str.startswith("MAYBE") and popped == False :
				stack.append(["MAYBE", ""])
				str = str[6:]

			else :
				aux = str[0:1]
				top = stack[len(stack) - 1]

				if str.startswith("void") and popped == False:
					s = "void"
					str = str[5:]
				elif str.startswith("eps") and popped == False:
					s = "eps"
					str = str[4:]
				elif str.startswith("' '") and popped == False:
					s = "' '"
					str = str[4:]
				elif popped == False:
					s = aux
					str = str[2:]
				else :
					s = strpop
					strpop = ""
					popped = False

				if top[len(top) - 2] == "" :
					top[len(top) - 2] = s
					if len(stack) == 1 :
						e1 = s
					stack[len(stack) - 1] = top

				elif top[len(top) - 1] == "" :
					top[len(top) - 1] = s
					if len(stack) == 1 :
						e2 = s
					stack[len(stack) - 1] = top

				if (top[len(top) - 1] != "") :
					elpop = stack.pop()
					for i in range(len(elpop)) :
						strpop = strpop + elpop[i] + " "
					strpop = strpop[:len(strpop) - 1]
					popped = True

			if (len(stack) == 0) :
				break
		return [e1, e2]	

	def getEpsClosure(self, state: S, steps: int) -> 'set[S]' :
		e = {state}
		if steps == 100 :
			return set()
		for s in self.next(state, "eps") :
			e = e | self.getEpsClosure(s, steps + 1)
		return e

	@staticmethod
	def fromPrenex(str: str) -> 'NFA[int]':

		#void
		if str == "void" :
			return NFA[int]({0, 1}, set(), {}, 0, {1})

		#epsilon
		elif str == "eps" :
			return NFA[int]({0}, {""}, {(0, "eps"): {0}}, 0, {0})
		
		#character
		elif len(str) == 1 :
			return NFA[int]({0, 1}, {str}, {(0, str): {1}}, 0, {1})

		# e1e2
		elif str.startswith("CONCAT") :
			N1 = NFA.fromPrenex(NFA.parse(str)[0])
			fstate = N1.finalStates.pop()
			N1.finalStates.add(fstate)
			count = len(N1.getStates())
			Neps = NFA[int]({0, 1}, {""}, {(0, "eps"): {1}}, 0, {1})
			N2 = NFA.fromPrenex(NFA.parse(str)[1])
			return NFA.NFAunion(NFA.NFAunion(N1, Neps.map(lambda x : (count - fstate) * x + fstate)), 
                       N2.map(lambda x : x + count))

		# e1 U e2
		elif str.startswith("UNION") :
			N1 = NFA.fromPrenex(NFA.parse(str)[0])
			Neps = NFA[int]({0, 1}, {""}, {(0, "eps"): {1}}, 0, {1})
			N2 = NFA.fromPrenex(NFA.parse(str)[1])
			epsN1 = NFA.NFAunion(Neps, N1.map(lambda x : x + 1))
			fstate = epsN1.finalStates.pop()
			epsN1.finalStates.add(fstate)
			count = len(epsN1.getStates())
			#print(count)
			epsN1eps = NFA.NFAunion(epsN1, Neps.map(lambda x : (count - fstate) * x + fstate))
			epsN2 = NFA.NFAunion(Neps.map(lambda x : x * (count + 1)), N2.map(lambda x : x + count + 1))
			fstate2 = epsN2.finalStates.pop()
			#print(fstate2)
			epsN2.finalStates.add(fstate2)
			count2 = len(N2.getStates())
			#print(count2)
			epsN2eps = NFA.NFAunion(epsN2, Neps.map(lambda x : (count - fstate2) * x + fstate2))
			return NFA.NFAunion(epsN1eps, epsN2eps)

		# e*
		elif str.startswith("STAR") :
			N = NFA.fromPrenex(str[5:])
			fstate = N.finalStates.pop()
			N.finalStates.add(fstate)
			count = len(N.getStates())
			Neps = NFA[int]({0, 1}, {""}, {(0, "eps"): {1}}, 0, {1})
			NFA1 = NFA.NFAunion(NFA.NFAunion(Neps, N.map(lambda x : x + 1)), Neps.map(lambda x : (count - fstate) * x + fstate + 1))
			return NFA.NFAunion(NFA.NFAunion(NFA1, Neps.map(lambda x : -fstate * x + fstate + 1)), 
                       Neps.map(lambda x : x * (count + 1)))

		# ' '
		elif str.startswith("' '") :
			return NFA[int]({0, 1}, {' '}, {(0, ' '): {1}}, 0, {1})

		# +
		elif str.startswith("PLUS") :
			return NFA.fromPrenex("CONCAT " + str[5:] + " STAR " + str[5:])

		# ?
		elif str.startswith("MAYBE") :
			return NFA.fromPrenex("UNION " + str[6:] + " eps")
