from NFA import GNFA

def Sombrero( str ):
    items = []
    stack = []

    ops = "+."

    #Preprocess to add concatenators between consecutive letters
    pre = []
    lastWasChar = False
    for c in str:
        if c not in ops+"()*":
            if lastWasChar:
                pre.append( '.' )
            lastWasChar = True
        else:
            lastWasChar = False
        pre.append( c )

    str = "".join( pre )

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
            stack.append( GNFA( 2, [{x:{1}},{}], 0, 1 ) )

    while len( stack ) > 1:
        N = stack.pop()
        stack.append( stack.pop().cat( N ) )

    return stack[0]

print "(a+b)*abb"
print

N = Sombrero( "(a+b)*abb" )

N.condense()
print N
print
N.drawing()
