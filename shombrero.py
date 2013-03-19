import os
import re
import cmd
import readline
import pdb
from Automata import SNFA,NFA,DFA

def Sombrero( str ):
    items = []
    stack = []

    ops = "+."

    #Preprocess to add implied concatenators
    nodot = re.compile( "([^(.+])([^).*+])" )
    pre = ""
    while pre != str:
        pre = str
        str = re.sub( nodot, r"\1.\2", str )

    #Transform the infix regex into a postfix regex
    for c in str:
        if c in ops:
            while len(stack) > 0 and ops.find( stack[-1] ) > ops.find( c ):
                item = stack.pop()
                items.append( item )
            stack.append( c )
        elif c == '*':
            items.append( c )
        elif c == '(':
            stack.append( c )
        elif c == ')':
            item = stack.pop()
            while item != '(':
                items.append( item )
                item = stack.pop()
        else:
            items.append( c )

    while len( stack ) > 0:
        items.append( stack.pop() )

    verbose = "".join(items)
    #Use the standard constructions to build an NFA from the postfix regex
    stack = []
    for x in items:
        if x == '*':
            stack.append( stack.pop().sombrero() )
        elif x == ".":
            N = stack.pop()
            stack.append( stack.pop().cat( N ) )
        elif x == "+":
            N = stack.pop()
            stack.append( stack.pop().union( N ) )
        else:
            stack.append( SNFA( 2, [{x:{1}},{}], 0, 1 ) )
    #Problem: At this point we might have a stack of disjoint NFAs.
    #Solution: cat ALL the NFAs
    while len( stack ) > 1:
        N = stack.pop()
        stack.append( stack.pop().cat( N ) )

    return verbose, stack[0].toNFA()

class Shombrero(cmd.Cmd):
    def __init__(self):
        self.var = re.compile("\$(_*[A-Za-z][A-Za-z0-9_]*)")
        self.regexs = {}
        self.varExpand = lambda m: '(' + self.regexs[m.group(1)][0] + ')'
        cmd.Cmd.__init__(self)
        self.prompt = "~^~ "
        self.singing = False

    def do_sing(self,args):
        self.singing = True

    def do_hist(self, args):
        print self._hist

    def do_exit(self, args):
        return -1

    def do_EOF(self, args):
        print
        return self.do_exit(args)

    def do_help(self, args):
        cmd.Cmd.do_help(self, args)

    def do_let(self, args):
        tokens = args.strip().split()
        regex = " ".join( tokens[1:] )
        variables = re.findall( self.var, regex )
        errors = False
        for x in variables:
            if x not in self.regexs:
                print "*** Undefined variable: ", x
                errors = True
        if errors:
            return
        regex = re.sub( self.var, self.varExpand, regex )
        verbose, N = Sombrero( regex )
        #N.condense()
        self.regexs[ tokens[0] ] = ( regex, N )

    def do_eval(self, args):
        tokens = args.strip().split()
        for w in tokens[1:]:
            if tokens[0] in self.regexs:
                print self.regexs[tokens[0]][1].Accepts( w, self.singing ),
        print

    def do_min(self, args):
        tokens = args.strip().split()
        for arg in tokens:
            if arg in self.regexs and isinstance(self.regexs[ arg ][1], DFA):
                self.regexs[ arg ][1].TableFill()

    def do_subset(self, args):
        tokens = args.strip().split()
        for arg in tokens:
            if arg in self.regexs and isinstance(self.regexs[ arg ][1], NFA):
                sigma = self.regexs[ arg ][1].Alphabet( )
                r, R = self.regexs[ arg ]
                self.regexs[ arg ] = (r, R.Subset( sigma ))

    def do_terse(self, args):
        tokens = args.strip().split()
        for arg in tokens:
            if arg in self.regexs and isinstance(self.regexs[ arg ][1], NFA):
                self.regexs[ arg ][1].Condense()

    def do_print(self, args):
        tokens = args.strip().split()
        for arg in tokens:
            if arg in self.regexs:
                print arg,":=",self.regexs[ arg ][0]
                print self.regexs[ arg ][1]

    def preloop(self):
        cmd.Cmd.preloop(self)
        self._hist = []
        self.regexs = {}

    def precmp(self, line):
        self._hist.append(line.strip())
        return line

    def postloop(self):
        cmd.Cmd.postloop(self)

    def emptyline(self):
        pass

if __name__ == '__main__':
    sh = Shombrero()
    sh.cmdloop()
