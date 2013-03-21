#! /usr/bin/python
import pdb
import sys
from Automata import DFA

sigma = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

finDFA = open(sys.argv[1], 'r')
finQuery = open(sys.argv[2], 'r')
foutPart = open(sys.argv[3], 'w')
foutTest = open(sys.argv[4], 'w')

dd = []
N = 0
for line in finDFA:
    words = line.split()
    if words[0] == 'F':
        F = { int(word)-1 for word in words if word != 'F' }
    else:
        N = len( words )
        dd.append( [ int(word)-1 for word in words ] )

D = DFA(sigma[:N], len( dd ), dd, 0, F)
print "DFA D:"
print D

for line in finQuery:
    words = line.split()
    p = int(words[0])-1
    q = int(words[1])-1
    print '\nTesting Pair (%d, %d)\n' % (p,q)
    for x in D.ForwardClosure( p, q ):
        found, part, badPair = x
    pp = []
    mapping = []
    for x in part:
        if x[0] is None:
            mapping.append( len( pp ) )
            pp.append( {x[1]} )
        else:
            mapping.append( None )
    for x in part:
        y = D.find(x[1],part)
        pp[mapping[y[1]]].add( x[1] )
    pstr = '; '.join([' '.join(sorted( [ str( x+1 ) for x in i ] )) for i in pp]) + '\n'
    foutPart.write( pstr )
    if found:
        foutTest.write( 'G\n' )
    else:
        u, v = badPair
        foutTest.write( str( u+1 ) + " " + str( v+1 ) )


