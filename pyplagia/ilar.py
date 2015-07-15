#
# Tests with flattening asts
# Implementation of what is needed for the ilar method.

# pyplagia, Pierre-Antoine BRAMERET (C) 2014


# !! DAO.genPickleForFiles doit mettre à jour nameToToken, revoir ça dans intifyTokens() (l'ajouter en paramètre)
# Le DAO doit stoquer les pickles de sim et de ilar
#  ... qui du coup ne sont pas du tout pareils... donc il faut tout rechanger :P


import ast
import inspect
from .sim import DicIncr



# It is not necessary to store nodeToToken in DB, as it is a "constant" for a given CPython implementation.
# .. but it will be, because of genericity
def initNodeToToken():
    nodeToToken = DicIncr()
    for n in dir(ast):
        if n == 'AST':
            continue
        o = getattr(ast, n)
        if inspect.isclass(o) and issubclass(o, ast.AST): # In practise, all classes in ast are subclassed from ast.AST
            nodeToToken[n]
    nodeToToken.setReadOnly()
    return nodeToToken




if False:
    for n in dir(ast):
        o = getattr(ast, n)
        if not inspect.isclass(o):
            print('#',n)
        elif issubclass(o, ast.AST):
            print('+',n)
        else:
            print('-',n)


if __name__=='__main__':
    testCode = '''
    nom = 'Dudu'
    a = 3
    def uneFonction():
        a = 42
        g = 76*a
    class Zob:
        def uneAutre(self):
            method = True
    def autreFct():
        b = 89
        def c():
            x = 42
        return c()
    print( autreFct() )
    '''
    #t = ast.parse(testCode)
    t = ast.parse(open('codesEleves/2011_BlondelAdhemar.py', 'rb').read())


#-------------------------------------------------------------------------------
# Tests with Abstract Syntax Trees
#
# It is not very clear on how to use the NodeVisitor...
# If you want to use the visit and generic_visit:
#  visit visits the current node and ast.NodeVisitor.visit dispatches the call
#   to the visit_classname() methods
#   OR calls generic_visit(node) if no visit_classname is ok
#  generic_visit calls visit on children of current node.
# "Note that child nodes of nodes that have a custom visitor method won’t be visited
#  unless the visitor calls generic_visit() or visits them itself."
#-------------------------------------------------------------------------------
if False:
    class PrintName(ast.NodeVisitor):
        def visit(self, node):
            if isinstance(node, ast.AST):
                if 'name' in node._fields:
                    print(node.lineno, node.name)
                elif isinstance(node, (ast.expr, ast.stmt)):
                    print(node.lineno, '###')
                else:
                    print('X not expr nor stmt', type(node))
                #for child in ast.iter_child_nodes(node):
                #    self.generic_visit(child)
                self.generic_visit(node)
            else:
                print('node not a node')

    class NodeLister(ast.NodeVisitor):
        def __init__(self):
            self.lNodes = []
        def visit(self, node):
            self.lNodes.append(node)
            self.generic_visit(node)
            #for child in ast.iter_child_nodes(node):
            #    self.generic_visit(child)


    class PrintToken(ast.NodeVisitor):
        def visit(self, node):
            cName = node.__class__.__name__
            print(nodeToToken[cName], cName)
            self.generic_visit(node)


    class DepthPrinter(ast.NodeVisitor):
        def __init__(self):
            self.iLevel = 0
        def visit(self, node):
            print(self.iLevel, node.__class__.__name__)
            self.iLevel += 1
            super().visit(node) # Calls generic_visit because there are no specific visit_classname()
            self.iLevel -= 1



#-------------------------------------------------------------------------------
# Ilar flattener.
# (AST flattener and function separator)
#-------------------------------------------------------------------------------
# Flattens a code (recursive) in the following way:
# - adds nodes to a "main" list
# - adds functions to sublists in llFcts
#  - if subfunctions are defined, they are kept in definition of the function
# - ignores classes
# Usage: flat = Flattener(nodeToToken) to make a "__main__ flattener"; then flat.visit()
class Flattener(ast.NodeVisitor):
    def __init__(self, nodeToToken, bKeepSubfunction=False):
        self.lMain = []
        self.llFcts = []
        self.bKeepSubfunction = bKeepSubfunction
        self.nodeToToken = nodeToToken
    def getToken(self, node):
        # Debug : return type(node).__name__
        return self.nodeToToken[type(node).__name__]
    def getTokenBlocks(self):
        return [self.lMain]+self.llFcts

    def visit(self, node):
        if not isinstance(node, (ast.ClassDef, ast.FunctionDef)):# and (self.bKeepFunction or not isinstance(node, ast.FunctionDef)):
            self.lMain.append(self.getToken(node))
        return super().visit(node)
    def visit_FunctionDef(self, node):
        subflat = Flattener(self.nodeToToken, bKeepSubfunction=True)
        subflat.lMain.append(self.getToken(node))
        subflat.generic_visit(node) # So, we don't do it for self.
        if self.bKeepSubfunction:
            self.lMain.extend(subflat.lMain)
        self.llFcts.append(subflat.lMain)
        self.llFcts.extend(subflat.llFcts)
        

# This one is used only
def intifyAndCutAST(sFileName, nodeToToken):
    #pass # Pas trop compatbile avec l'API existant...
    rootNode = ast.parse(open(sFileName, 'rb').read())
    flater = Flattener(nodeToToken)
    flater.visit(rootNode)
    return [flater.lMain]+flater.llFcts


if __name__=='__main__':
    intifyAndCutAST(t)





