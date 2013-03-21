__author__ = 'liam'

import pdb
import copy
import random

class DFA:
    def __init__(self, sigma, Q, delta, s, F):
        self.sigma = sigma
        self.Q = Q
        self.delta = delta
        self.s = s
        self.F = F

    def __repr__(self):
        rep = ["      | "+" | ".join(self.sigma)]
        rep.append("    --+-"+"-+-".join(["-"]*len(self.sigma)))
        for i in xrange(len(self.delta)):
            d = self.delta[i]
            pre = " -> " if self.s == i else "    "
            post = " *" if i in self.F else "" 
            rep.append(pre+str(i)+" | "+" | ".join([str(x) for x in d])+post)
        return "\n".join(rep)

    def Accepts(self, w, sing):
        Q = self.s
        for a in w:
            if sing:
                print random.choice( ( "do", "de", "da" ) ),
            if a not in self.sigma:
                return False
            Q = self.delta[Q][self.sigma.index(a)]
        return Q in self.F

    def Alphabet(self):
        return self.sigma

    def TableFill(self):
        bad = lambda p,q: ( p not in self.F and q in self.F ) \
                or ( p in self.F and q not in self.F )
        table = [[bad(i,j) for i in range( j+1 )] \
                for j in range( self.Q )]
        idx = [(i,j) for i in range( 1, self.Q ) \
                for j in range( i ) if not table[i][j]]
        updated = True
        while updated:
            updated = False
            for (p,q) in idx:
                if not table[p][q]:
                    for a in self.sigma:
                        i = self.delta[p][self.sigma.index(a)]
                        j = self.delta[q][self.sigma.index(a)]
                        if i < j:
                            i = i^j
                            j = i^j
                            i = i^j
                        if table[i][j]:
                            table[p][q] = True
                            updated = True
                            break
        partition = [ {i,j} for i,j in idx if not table[i][j] ]
        P = [ {i} for i in range( self.Q ) ]
        for p in P:
            for g in partition:
                if len( p & g ) > 0:
                    p |= g
        checked = []
        for x in P:
            if x not in checked:
                checked.append(x)
        P = checked
        rename = { i:j for j in range( len( P ) ) for i in P[j] }
        delta = []
        for S in P:
            i = iter(S).next()
            d = []
            for a in self.sigma:
                j = self.delta[i][self.sigma.index(a)]
                d.append( rename[j] )
            delta.append( d )
        self.s = rename[self.s]
        self.Q = len( P )
        self.delta = delta
        self.F = {rename[f] for f in self.F}

    def printPartition(self,part):
        pp = []
        mapping = []
        for x in part:
            if x[0] is None:
                mapping.append( len( pp ) )
                pp.append( {x[1]} )
            else:
                mapping.append( None )
        for x in part:
            y = self.find(x[1],part) 
            pp[mapping[y[1]]].add( x[1] )
        pstr = '; '.join([' '.join(sorted( [ str( x ) for x in i ] )) for i in pp])
        return pstr

    def ForwardClosure(self,p,q,gen=None):
        part = [ [None,s,1] for s in xrange(self.Q) ]
        stack = [(p,q)]
        while len( stack ) > 0:
            pstr = self.printPartition( part )
            if gen:
                yield pstr
            else:
                print pstr
            uu, vv = stack.pop()
            if self.bad(uu,vv):
                print "Bad pair: (", uu,  ",", vv, ")"
                yield (False, part, (uu,vv))
                return
            u = self.find( uu, part )
            v = self.find( vv, part )
            if u[1] != v[1]:
                self.union( u[1], v[1], part )
                for i in xrange( len( self.sigma ) ):
                    u1 = self.delta[uu][i]
                    v1 = self.delta[vv][i]
                    stack.append( (u1,v1)  )
        yield (True, part, None)

    def bad(self,p,q):
        if p in self.F and q not in self.F:
            return True
        if p not in self.F and q in self.F:
            return True
        return False

    def union(self,p,q,part):
        P = self.find( p, part )
        Q = self.find( q, part )
        if P[1] == Q[1]:
            return
        if P[2] < Q[2]:
            part[P[1]][0] = Q[1]
            part[Q[1]][2] += P[2]
        else:
            part[Q[1]][0] = P[1]
            part[P[1]][2] += Q[2]

    def find(self,p,part):
        path = []
        q = part[p]
        while q[0] is not None:
            path.append(q[1])
            q = part[q[0]]
        for s in path:
            part[s][0] = q[1]
        return q

    def Reverse(self):
        Q = self.Q + 1
        S = self.F
        F = { self.s }
        delta = []
        for i in xrange( self.Q ):
            delta.append( {} )
        delta.append( {'':self.F} )
        for q in xrange( self.Q ):
            for i in xrange( len(self.sigma) ):
                a = self.sigma[i]
                p = self.delta[q][i]
                if a in delta[p]:
                    delta[p][a] |= { q }
                else:
                    delta[p][a] = { q }
        return NFA( Q, delta, S, F ).Condense()

class NFA:
    def __init__(self, Q, delta, S, F):
        self.Q = Q          #Number of states in NFA
        self.delta = delta  #list of dicts of sets, list has Q elements
        self.S = S          #Set of start states
        self.F = F          #Set of accepting states

    def __repr__(self):
        rep = []
        for i in xrange( len( self.delta ) ):
            item = []
            if i in self.S:
                item.append( " ->" )
            else:
                item.append( "   " )
            P={}
            for a in self.delta[i].keys():
                P[a]="{"+", ".join([str(s) for s in self.delta[i][a]])+"}"
           
            item.append("("+" ".join([repr(a)+":"+P[a] for a in P.keys()])+")")
            if i in self.F:
                item.append( "*" )
            rep.append( " ".join( item ) )
        return "\n".join(rep)

    def toSNFA(self):
        delta = self.delta
        Q = self.Q
        validStart = len( self.S ) == 1
        for d in delta:
            for a in d.keys():
                if len(self.S & d[a]) > 0:
                    validStart = False
                    break
        if validStart: # No inbound transitions, only one start
            #This is an oddity of python sets where there are no 'good'
            #methods to extract the element from a set of one
            #so we cast it to a tuple and then unpack it... gross
            s, = self.S
        else:
            s = self.Q
            Q += 1
            delta.append({'':self.S})
        if len( self.F ) == 1:  # Singular accepting state
            f = iter(self.F).next()
            if len(delta[f].keys()) == 0:
                t = f # No outbound transitions, f is a sink
            else:
                if '' in delta[f]:
                    delat[f][''] |= {Q}
                else:
                    delta[f][''] = {Q}
                delta.append({})
                t = Q
                Q += 1
        else:
            for f in self.F:
                if '' in delta[f]:
                    delta[f][''] |= {Q}
                else:
                    delta[f][''] = {Q}
                delta.append({})
                t = Q
                Q += 1
        return SNFA( Q, delta, s, t )

    def eClosure(self, state, ignore):
        if state >= self.Q:
            return set()
        eStates = { state }
        if '' in self.delta[state]:
            for x in self.delta[state]['']:
                if x not in ignore:
                    eStates |= self.eClosure( x, eStates )
        return eStates

    def epsilonlessify(self): # get rid of epsilon transitions
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
        Q = set()
        for s in self.S:
            Q |= self.trim(s,set())
        last = len( Q ) - 1
        mapping = {}
        for x, e in reversed( list( enumerate( self.delta ) ) ):
            if x in Q:
                mapping[x] = last
                last -= 1
            else:
                self.delta.pop( x )
        for d in self.delta:
            for a in d.keys():
                d[a] = { mapping[x] for x in d[a] }
        self.S = { mapping[x] for x in self.S if x in mapping }
        self.F = { mapping[x] for x in self.F if x in mapping }
        self.Q = len( Q )
        return self

    def Subset(self, Sigma):
        K = [set()]
        for s in self.S:
            K[0] |= self.eClosure(s,set())
        total = 0
        marked = -1
        Delta = []
        while marked < total:
            marked += 1
            S = K[marked]
            Del = []
            for a in Sigma:
                U = set.union( * [ self.delta[q][a] if a in self.delta[q].keys() else set() for q in S ] ) if len( S ) > 0 else set()
                T = set.union( * [ self.eClosure( q, set() ) for q in U ] ) if len( U ) > 0 else set()
                if T not in K:
                    total += 1
                    K.append( T )
                Del.append(K.index(T))
            Delta.append( Del )
        F = {K.index(S) for S in K if len(S.intersection(self.F)) > 0}
        return DFA(Sigma,total+1,Delta,0,F)

    def Alphabet(self):
        return ''.join( set.union( * [ set( d.keys() ) for d in self.delta ] ) )

    def Minimize(self):
        pass

    def Accepts(self, w, sing):
        Q = set()
        for s in self.S:
            Q |= self.eClosure(s,set())
        for a in w:
            if sing:
                print random.choice( ( "do", "de", "da" ) ),
            Q = set.union( * [ self.delta[p][a] if a in self.delta[p] else set() for p in Q ] )
            if len( Q ) == 0:
                return False
            Q = set.union( * [ self.eClosure( q, set() ) for q in Q ] )
        return len( Q & self.F ) > 0

    def drawing(self):
        """
        Write a Dot representation of this DFA to stdout.
        (Stolen from Mr. M. Moeller)
        """
        print "digraph g {"
        print "    rankdir=LR"
        for s in self.S:
            print "    qnull" + s + "[color=white,fontcolor=white]"
        # Create nodes
        for state in range(self.Q):
            accepting = ''
            if state in self.F:
                accepting = ',peripheries=2'
            print '    q' + str(state) + '[shape=circle,label="' + str(state) + '"' + accepting + '];'
        # Create the "start" transitions
        for s in self.S:
            print '\n    qnull' + str(s) + ' -> q'+str(s)
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

class SNFA:
    def __init__(self, Q, delta, s, t):
        self.Q = Q          #Number of states in NFA
        self.delta = delta  #list of dicts of sets, list has Q elements
        self.s = s          #Start state
        self.t = t          #Accepting states
        self.F = {t}

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

    def union(self, nfa):
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

    def toNFA(self):
        return NFA(self.Q, self.delta, {self.s}, {self.t})
