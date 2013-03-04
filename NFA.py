__author__ = 'liam'

import copy
import random

class GNFA:
    def __init__(self, Q, delta, s, t):
        self.Q = Q          #Number of states in NFA
        self.delta = delta  #list of dicts of sets representing transitions. list has Q elements
        self.s = s          #Start state
        self.t = t          #Accepting states
        self.F = {t}

    def __repr__(self):
        rep = []
        for i in xrange( len( self.delta ) ):
            item = []
            if i == self.s:
                item.append( " ->" )
            else:
                item.append( "   " )
            item.append( self.delta[i].__repr__() )
            if i in self.F:
                item.append( "*" )
            rep.append( " ".join( item ) )
        return "\n".join(rep)

    def cat(self, nfa):
        """
        "'WRREEEEARH!' ... That was the cat." - Jean Gallier
        """
        gnfa = copy.deepcopy(nfa)
        Q = self.Q
        self.Q += gnfa.Q
        for delta in gnfa.delta:
            for k in delta.keys():
                dk = set()
                for v in delta[ k ]:
                    dk.add( v + Q )
                delta[ k ] = dk
            self.delta.append( delta )
        self.delta[self.t][''] = {gnfa.s + Q}
        self.t = gnfa.t+Q
        self.F = {self.t}
        return self

    def union(self,nfa):
        gnfa = copy.deepcopy(nfa)
        Q = self.Q
        self.Q += gnfa.Q + 2
        for delta in gnfa.delta:
            for k in delta.keys():
                dk = set()
                for v in delta[ k ]:
                    dk.add( v + Q )
                delta[ k ] = dk
            self.delta.append( delta )
        self.delta[self.t][''] = {Q + gnfa.Q + 1}
        self.delta[gnfa.t+Q][''] = {Q + gnfa.Q + 1}
        self.delta.append( { '' : {self.s, gnfa.s+Q} } )
        self.delta.append( {} )
        self.s = Q + gnfa.Q
        self.t = Q + gnfa.Q + 1
        self.F = {self.t}
        return self

    def sombrero(self):
        Q = self.Q
        self.Q += 2
        self.delta[self.t][''] = {self.s, Q+1}
        self.delta.append( { '':{self.s, Q+1} } )
        self.delta.append( {} )
        self.s = Q
        self.t = Q + 1
        self.F = {self.t}
        return self

    def eClosure(self, state, ignore):
        if state >= self.Q:
            return set()
        eStates = { state }
        if '' in self.delta[state]:
            for x in self.delta[state]['']:
                if x not in ignore:
                    eStates |= self.eClosure( x, eStates )
        return eStates

    def epsilonlessify(self):
        #get rid of epsilon transitions
        for state in range( self.Q ):
            eps = self.eClosure(state, set())
            if len( self.F.intersection( eps ) ) > 0:
                self.F.add( state )
            delta = {}
            for es in eps:
                for k in self.delta[es].keys():
                    if k == '':
                        continue
                    if k in delta:
                        delta[k] |= self.delta[es][k]
                    else:
                        delta[k] = self.delta[es][k]
            self.delta[state] = delta

    def trim(self, state, ignore):
        if state in ignore:
            return set()
        Q = {state}
        ignore.add( state )
        for k in self.delta[state].keys():
            for s in self.delta[state][k]:
                Q |= self.trim( s, ignore )
        return Q

    def Condense(self):
        self.epsilonlessify()
        Q = self.trim(self.s,set())
        mapper = {self.s:0}
        idx = 1
        fromStates = [self.s]
        for x in Q:
            for k in self.delta[x].keys():
                newTrans = set()
                for q in self.delta[x][k]:
                    if q not in mapper:
                        mapper[q] = idx
                        fromStates.append( q )
                        idx += 1
                    newTrans.add(mapper[q])
                self.delta[x][k] = newTrans
        self.s = 0
        self.delta = [self.delta[x] for x in fromStates]
        self.F = { mapper[x] for x in self.F if x in Q }
        self.Q = len( Q )
        return self

    def Subset(self, Sigma):
        K = [self.eClosure(self.s,set())]
        total = 0
        marked = -1
        Delta = []
        while marked < total:
            marked += 1
            S = K[marked]
            Del = {}
            for a in Sigma:
                U = set.union( * [ self.delta[q][a] if a in self.delta[q].keys() else set() for q in S ] ) if len( S ) > 0 else set()
                T = set.union( * [ self.eClosure( q, set() ) for q in U ] ) if len( U ) > 0 else set()
                if T not in K:
                    total += 1
                    K.append( T )
                Del[a] = {K.index(T)}
            Delta.append( Del )
        F = { K.index(S) for S in K if len( S.intersection( self.F ) ) > 0 }
        self.Q = total + 1
        self.s = 0
        self.delta = Delta
        self.F = F
        return self

    def Alphabet(self):
        return ''.join( set.union( * [ set( d.keys() ) for d in self.delta ] ) )

    def Minimize(self):
        return self

    def Accepts(self, w, sing):
        Q = self.eClosure( self.s, set() )
        for a in w:
            if sing:
                print random.choice( ( "do", "de", "da" ) ),
            Q = set.union( * [ self.delta[p][a] if a in self.delta[p] else set() for p in Q ] )
            if len( Q ) == 0:
                return False
            Q = set.union( * [ self.eClosure( q, set() ) for q in Q ] )
        return len( Q & self.F ) > 0

    def tableFill(self):
        pass

    def drawing(self):
        """
        Write a Dot representation of this DFA to stdout.
        (Stolen from Mr. M. Moeller)
        """
        print "digraph g {"
        print "    rankdir=LR"
        print "    qnull[color=white,fontcolor=white]"
        # Create nodes
        for state in range(self.Q):
            accepting = ''
            if state in self.F:
                accepting = ',peripheries=2'
            print '    q' + str(state) + '[shape=circle,label="' + str(state) + '"' + accepting + '];'
        # Create the "start" transition
        print '\n    qnull -> q'+str(self.s)
        # Create the real transitions
        for state in range(self.Q):
            inverted = {}
            for letter in self.delta[state].keys():
                for destination in self.delta[state][letter]:
                    if letter == '':
                        name = "epsilon"
                    else:
                        name = letter
                    if destination in inverted:
                        inverted[destination] += ","+letter
                    else:
                        inverted[destination] = name
            for destination in inverted:
                print '    q' + str(state) +\
                      ' -> q' + str(destination) +\
                      '[label="' + inverted[destination] + '"];'
        print "}"
