#
# Tools for the SIM method.
# pyplagia, Pierre-Antoine BRAMERET (C) 2014


import tokenize
import token
import keyword
import builtins
import io
from itertools import permutations






            
#-------------------------------------------------------------------------------
# This one is used by sim and ilar.
# Convert token names to int. Let token be recorded to be always in the same order
# Sim uses it to store identifier names too.
#-------------------------------------------------------------------------------
class DicIncr:
    NAME_OFFSET = 1024
    def __init__(self):
        self.N = 1 # Not 0, reserved but ... by what?
        self.d = {}
        self.bReadOnly = False # When True, raises an error if key is not in d (debug assert)
    def __getitem__(self,s):
        if s not in self.d:
            if self.bReadOnly:
                raise KeyError('This DicIncr is now read-only and this key was not registred')
            self.d[s] = self.N
            self.N += 1
        return self.d[s]
    def __str__(self): return 'PAB'+str(self.d)
    def __repr__(self): return 'PAB'+repr(self.d)
    def setAfterTokens(self):
        self.N = token.NT_OFFSET
    def setCustomNames(self):
        self.N = DicIncr.NAME_OFFSET
    def setReadOnly(self):
        self.bReadOnly = True




#-------------------------------------------------------------------------------
# Used for custom-tokenization of identifiers
# By now, used only by sim.
#-------------------------------------------------------------------------------

# This is due to a WEIRD *something*: token.COMMENT does not exists BUT token.tok_name[55] is 'COMMENT', AND tok_name is build in token.py from the constants that are also in token.__all__ (hence exported)
# (and token.N_TOKENS is not in tok_name)
try:
    assert token.tok_name[55]=='COMMENT', 'Non-version-independant constant is not good'
    assert token.tok_name[56]=='NL', 'Non-version-independant constant is not good'
    assert token.tok_name[57]=='ENCODING', 'Non-version-independant constant is not good'
    token.COMMENT = 55
    token.NL = 56
    token.ENCODING = 57
except AssertionError:
    assert token.tok_name[54]=='COMMENT', 'Non-version-independant constant is not good'
    assert token.tok_name[55]=='NL', 'Non-version-independant constant is not good'
    assert token.tok_name[56]=='ENCODING', 'Non-version-independant constant is not good'
    token.COMMENT = 54
    token.NL = 55
    token.ENCODING = 56


        


def initNameToToken():
    nameToToken = DicIncr()
    nameToToken.setAfterTokens()
    # Record operators (optional)
    for s in ['+', '-', '*', '**', '/', '//', '%', '<<', '>>', '&', '|', '^', '~', '<', '>', '<=', '>=', '==', '!=',
              '(', ')', '[', ']', '{', '}', ',', ':', '.', ';', '@', '=', '+=', '-=', '*=', '/=', '//=', '%=', '&=', '|=', '^=', '>>=', '<<=', '**=',]:
        nameToToken[s]
    # Record some keywords, so that it gives average identification...
    for s in keyword.kwlist:
        nameToToken[s]
    for s in dir(builtins):
        nameToToken[s]
    # Now begins custom names
    nameToToken.setCustomNames()
    return nameToToken


# Use Python tokenizer to analyse the source code
def tokenizeStr(s):
    sb = io.BytesIO()
    sb.write( s.encode() )
    sb.seek(0)
    return list(tokenize.tokenize(sb.readline))


# Converts tokens to integers (it's easier to compare, and to customize)
def intifyTokens(lTok, nameToToken):
    l = []
    for tok in lTok:
        # Translates operators to integers (a single token OP is used by Python to reduce the number of tokens)
        if tok.type in (token.OP, token.NAME):
            l.append(nameToToken[tok.string])
        # Ignore newlines, comments (there content should be treated separately, and their position can be changed too easily) and some other tokens
        elif tok.type in (token.COMMENT, token.NL, token.ENCODING):
        #elif tok.type in (token.NL, token.ENCODING):
            continue
        else:
            l.append(tok.type)
    return l



#-------------------------------------------------------------------------------
# SIM-only method (yes, as the others ^^)
# http://lowara.googlecode.com/svn/KPI/diplom/source_code/Sim_%20A%20Utility%20For%20Detecting%20Similarity%20in%20Computer%20Programs.pdf
#-------------------------------------------------------------------------------

# Detects subblocks of code, by their level of indentation
#  Will make subblocks from functions, if-statements, for-loops, ...
#  Will not work well with functions in functions
def simDetectBlocks(lTokin):
    ll = []
    a = 0
    N = 3 # Should separate if statement and for loops in methods of classes
    for i,x in enumerate(lTokin):
        if x in (token.INDENT, token.DEDENT) and N>0:
            ll.append(lTokin[a:i])
            a = i
        if x == token.INDENT:
            N -= 1
        elif x == token.DEDENT:
            N += 1
    ll.append( lTokin[a:] )
    return ll







    






















