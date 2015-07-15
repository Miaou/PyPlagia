#
# Tools, DB, and plagiarism...

# DO NOT USE, this is the old lib...

assert False, "PLEASE DO NOT USE THIS OLD LIB"

from sys import platform
import os
import tokenize
import token
import keyword
import builtins
import io
import ctypes
from itertools import permutations

from multiprocessing import Queue, Process, Lock, Value
from threading import Thread
from queue import Empty as QEmpty
import time



sDB = 'plagia.db'
SOURCE_DIR = 'codesEleves/'
# On too much procs, very strange errors using sqlite3 database ("database disk image is malformed" or "file is encrypted or is not a database" (!!!))
#  and race condition using mutiprocessing.Lock (tested ok with 8)
# Hmm, further analysis leads to weirder results: when the threads are replaced by processes (for writing the DB), less race conditions...
#  however, these leads to "disappearing processes": processes that stop without error! (hmm, they may just have finish their unbalanced queue...)
N_PROCESS = 24


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





#-------------------------------------------------------------------------------
# First tests with tokenized code, and pure-Python implementation for SIM
#-------------------------------------------------------------------------------
if False:
    root = ast.parse(open('test.py').read())
    root = ast.parse('dudu = 3+2')
    #PrintName().generic_visit(root)
    nl = NodeLister()
    nl.generic_visit(root)
    lNodes = nl.lNodes

    with open('test.py', 'rb') as f:
        lTok = list(tokenize.tokenize(f.readline))


    import numpy as np
    def strAlign(a,b):
        # Hypothèse que c'est pas une seule lettre qui correspond... (moins de tests)
        scMax = 0
        iM,jM = 0,0
        m = 1
        d = -1
        g = -2
        sc = lambda x,y: m if x==y else d
        D = np.zeros( (len(a), len(b)) )
        for j in range(len(b)):
            D[0,j] = max([sc(a[0],b[j]),0])
        for i in range(1,len(a)):
            D[i,0] = max([sc(a[i],b[0]),0])
            for j in range(1,len(b)):
                D[i,j] = max([D[i-1,j-1] + sc(a[i],b[j]),
                              D[i-1,j]+g,
                              D[i,j-1]+g,
                              0]) # Le zéro m'étonne beaucoup pour la deuxième ligne...
                if D[i,j] > scMax:
                    iM,jM = i,j
                    scMax = D[i,j]
        print(D)
        if iM>jM:
            print(a)
            print(' '*(iM-jM)+b)
        elif iM<jM:
            print(' '*(jM-iM)+a)
            print(b)
        else:
            print(a)
            print(b)
        print('score: {}'.format(scMax))
    def strAlignScore(a,b):
        scMax = 0
        lPrev = [0 for i in b]+[0]
        l = lPrev[:]
        g = -2
        def fSc(x,y):
            if x>DicIncr.NAME_OFFSET and y>DicIncr.NAME_OFFSET:
                return 2 if x==y else 0
            return 1 if x==y else 0 # -2 ?!
        #fSc = lambda x,y: 1 if x==y else -1
        for j,y in enumerate(b):
            lPrev[j] = max( (fSc(a[0],y),0) )
        for i,x in enumerate(a[1:]):
            for j,y in enumerate(b):
                l[j] = max([lPrev[j-1] + fSc(x,y),
                            lPrev[j] + g,
                            l[j-1] + g,
                            0])
            if max(l)>scMax:
                scMax = max(l)
            lPrev = l[:]
        return scMax
    
    def scoreBlocks(lTokin,llTokin):
        return sum(strAlignScore(lTokin,block) for block in llTokin)


    # Score is not permutative
    def score(f1,f2):
        if len(f1) > 30:
            lTokin1 = intifyTokens(tokenizeStr(f1))
        else:
            lTokin1 = intifyTokens(tokenize.tokenize(open(f1, 'rb').readline))
        if len(f2) > 30:
            lTokin2 = intifyTokens(tokenizeStr(f2))
        else:
            lTokin2 = intifyTokens(tokenize.tokenize(open(f2, 'rb').readline))
        
        sc11 = scoreBlocks(lTokin1, detectBlocks(lTokin1))
        sc22 = scoreBlocks(lTokin2, detectBlocks(lTokin2))
        sc12 = scoreBlocks(lTokin1, detectBlocks(lTokin2))
        
        return 2*sc12/(sc11+sc22)


            


#-------------------------------------------------------------------------------
# Used for custom-tokenization of identifiers
#-------------------------------------------------------------------------------
class DicIncr:
    NAME_OFFSET = 1024
    def __init__(self):
        self.N = 1 # Not 0, reserved but ... by what?
        self.d = {}
    def __getitem__(self,s):
        if s not in self.d:
            self.d[s] = self.N
            self.N += 1
        return self.d[s]
    def __str__(self): return 'PAB'+str(self.d)
    def __repr__(self): return 'PAB'+repr(self.d)
    def setAfterTokens(self):
        self.N = token.NT_OFFSET
    def setCustomNames(self):
        self.N = DicIncr.NAME_OFFSET
        


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
def intifyTokens(lTok):
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
# SIM method
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



#-------------------------------------------------------------------------------
# DAO
#-------------------------------------------------------------------------------

# DAO is unique, uses a string to identify the results which are to be dumped or load
#  so access should be grouped, and lists in argument should a serious length (100, 1000 ?)
class DAO:
    # Sim A: with 0 for any kind of mismatch
    # Sim B: with -2 for mismatch between non-identifiers
    getTableName = lambda sMethod: 'Cmp{}'.format(sMethod)
    
    def __init__(self, sDB, timeout=5):
        self.sDB = sDB
        self.db = sqlite3.connect(self.sDB, timeout)
        with self.db as db:
            db.execute('CREATE TABLE IF NOT EXISTS PickleNameToToken (data BLOB NOT NULL)') # Stores the nameToToken which is the customized token infos taking into account identifiers. Should be unique and project-wide...
            db.execute('CREATE TABLE IF NOT EXISTS Pickles (sFile TEXT PRIMARY KEY, bPick BLOB NOT NULL)')

            for sMeth in LibPlagia.METHODS:
                db.execute('''CREATE TABLE IF NOT EXISTS {} (sFileA TEXT NOT NULL, sFileB TEXT NOT NULL, fScore REAL,
                           PRIMARY KEY (sFileA, sFileB))'''.format(DAO.getTableName(sMeth)))

    def getNameToToken(self):
        '''Name to token is not thread-safe : all tokens should be precomputed in a single thread!'''
        dic = self.db.execute('SELECT * FROM PickleNameToToken').fetchone()
        return pickle.loads(dic[0]) if dic else initNameToToken()
    def setNameToToken(self, nameToToken):
        '''Name to token is not thread-safe : all tokens should be precomputed in a single thread!'''
        with self.db as db:
            db.execute('DELETE FROM PickleNameToToken')
            db.execute('INSERT INTO PickleNameToToken VALUES(?)', (pickle.dumps(nameToToken),))

    # With proper thinking, this one might not be performant:
    #  there are not so many files, they should be returned in a dict form (with too much keys, but not that much)
    #  and when they are to be pickled, the function should not return anything, so...
##    def getTokensFileList(self, lFiles, bPreserveNameToToken=True):
##        '''Name to token is not thread-safe : all tokens should be precomputed in a single thread!'''
##        # Note to self: yes, avoided repeated tokenization is good, but ... is tokenization so much time-consuming?
##        # Note to self: as sqlite&Lock show crazy race conditions, it is finally a rather bad idea to store tokenized info ... because the get() is now the bottleneck... (!!!)
##        with self.db as db: # Locks (hopefully) the DB, so this should avoid race conditions
##            lPickle = []
##            for sFile in lFiles:
##                tPick = self.db.execute('SELECT bPick FROM Pickles WHERE sFile=?', (sFile,)).fetchone()
##                if tPick:
##                    bPick, = tPick
##                    lPickle.append(pickle.loads(bPick))
##                else:
##                    if bPreserveNameToToken:
##                        raise ValueError('File was not pre-tokenized')
##                    with open(sFile, 'rb') as f:
##                        lTok = intifyTokens(list(tokenize.tokenize(f.readline)))
##                    with self.db as db:
##                        db.execute('INSERT INTO Pickles VALUES(?,?)', (sFile, pickle.dumps(lTok)))
##            return lPickle
    def getTokensDict(self):
        dTokens = {}
        with self.db as db:
            for sFile,bPick in db.execute('SELECT * FROM Pickles'):
                dTokens[sFile] = pickle.loads(bPick)
        return dTokens
    def getListOfTokenizedFiles(self):
        return [f for f, in self.db.execute('SELECT sFile FROM Pickles')]
    def genPickleForFiles(self, lFiles, bForce=False):
        with self.db as db:
            lFilesDone = self.getListOfTokenizedFiles()
            for sFile in lFiles:
                if bForce or not sFile in lFilesDone:
                    with open(sFile, 'rb') as f:
                        lTok = intifyTokens(list(tokenize.tokenize(f.readline)))
                    db.execute('INSERT OR REPLACE INTO Pickles VALUES(?,?)', (sFile, pickle.dumps(lTok)))


##    def setCmpSimA(self, sFileA, sFileB, fScore):
##        with self.db as db:
##            db.execute('INSERT INTO CmpSimA VALUES(?,?,?)', (sFileA, sFileB, fScore))
##    def getCmpSimAList(self):
##        return self.db.execute('SELECT * FROM CmpSimA').fetchall()
##    def getCmpSimA(self, sFileA, sFileB):
##        r = self.db.execute('SELECT fScore FROM CmpSimA WHERE sFileA=? AND sFileB=?', (sFileA, sFileB)).fetchone()
##        return r[0] if r else None
##    def setCmpSimB(self, sFileA, sFileB, fScore):
##        with self.db as db:
##            db.execute('INSERT INTO CmpSimB VALUES(?,?,?)', (sFileA, sFileB, fScore))
##    def getCmpSimBList(self):
##        return self.db.execute('SELECT * FROM CmpSimB').fetchall()
##    def getCmpSimB(self, sFileA, sFileB):
##        r = self.db.execute('SELECT fScore FROM CmpSimB WHERE sFileA=? AND sFileB=?', (sFileA, sFileB)).fetchone()
##        return r[0] if r else None

    def getCmpList(self, sMeth):
        assert sMeth in LibPlagia.METHODS
        return list(self.db.execute('SELECT * FROM {}'.format(DAO.getTableName(sMeth))))
    def getCmp(self, sMeth, sFileA, sFileB):
        assert sMeth in LibPlagia.METHODS
        r = self.db.execute('SELECT * FROM {} WHERE sFileA=? AND sFileB=?'.format(DAO.getTableName(sMeth)), (sFileA, sFileB)).fetchone()
        return r[0] if r else None
    def setCmpList(self, sMeth, lTriples):
        """lTriples: [(sFileA, sFileB, fScore), ...]"""
        assert sMeth in LibPlagia.METHODS
        for tup in lTriples:
            assert len(tup) == 3 # Might be superfluous, but might help when debugging
        sCmd = 'INSERT OR REPLACE INTO {} VALUES(?,?,?)'.format(DAO.getTableName(sMeth))
        with self.db as db:
            db.executemany(sCmd, lTriples)





#-------------------------------------------------------------------------------
# LibPlagia: its role is not really bounded for now.
#  It should handle all wrappings and for now, it handles scoring too.
#-------------------------------------------------------------------------------
class LibPlagia:
    METHODS = ('SimA', 'SimB', 'IlarA', 'IlarB') # Methods are not case sensitive!
    def __init__(self):
        if platform.startswith('linux'): # win32
            LIB_PATH='./libplagia/libplagia.so' # Le './' est important
        else:
            LIB_PATH='libplagia/libplagia.dll'
        self.lib = ctypes.cdll.LoadLibrary(LIB_PATH)

    def calcScore(self, sMeth, lTokA, lTokB):
        assert sMeth in LibPlagia.METHODS
        if sMeth in ('SimA','SimB'):
            #return self._wrapSimGetAlignScore(sMeth[3:], lTokA, lTokB)
            scoreBlocksSim = lambda lTokin,llTokin: sum(self._wrapSimGetAlignScore(sMeth[3:], lTokin, block) for block in llTokin)
            llTokB = simDetectBlocks(lTokB)
            sc11 = scoreBlocksSim(lTokA, simDetectBlocks(lTokA))
            sc22 = scoreBlocksSim(lTokB, llTokB)
            sc12 = scoreBlocksSim(lTokA, llTokB)
            return 2*sc12/(sc11+sc22)
        raise ValueError # Should never be raised, but will remind me if I forgot to implement an authorised methods...
##    def wrapSimAGetAlignScore(lTokA, lTokB):
##        A = len(lTokA)
##        B = len(lTokB)
##        lA = (ctypes.c_uint*A)()
##        for i,k in enumerate(lTokA):
##            lA[i] = k
##        lB = (ctypes.c_uint*B)()
##        for i,k in enumerate(lTokB):
##            lB[i] = k
##        lBuf  = (ctypes.c_uint*B)()
##        lBufP = (ctypes.c_uint*B)()
##        return libplagia.simAGetAlignScore(lA, A, lB, B, lBuf, lBufP)
##    def wrapSimBGetAlignScore(lTokA, lTokB):
##        A = len(lTokA)
##        B = len(lTokB)
##        lA = (ctypes.c_uint*A)()
##        for i,k in enumerate(lTokA):
##            lA[i] = k
##        lB = (ctypes.c_uint*B)()
##        for i,k in enumerate(lTokB):
##            lB[i] = k
##        lBuf  = (ctypes.c_uint*B)()
##        lBufP = (ctypes.c_uint*B)()
##        return libplagia.simBGetAlignScore(lA, A, lB, B, lBuf, lBufP)
    def _wrapSimGetAlignScore(self, sVar, lTokA, lTokB):
        assert sVar in ('A','B')
        A = len(lTokA)
        B = len(lTokB)
        lA = (ctypes.c_uint*A)()
        for i,k in enumerate(lTokA):
            lA[i] = k
        lB = (ctypes.c_uint*B)()
        for i,k in enumerate(lTokB):
            lB[i] = k
        lBuf  = (ctypes.c_uint*B)()
        lBufP = (ctypes.c_uint*B)()
        return getattr(self.lib,'sim{}GetAlignScore'.format(sVar))(lA, A, lB, B, lBuf, lBufP)
    def _wrapIlarGetAlignScore(self, sVar, lTokA, lTokB):
        assert sVar in ('A','B')
        A = len(lTokA)
        B = len(lTokB)
        lA = (ctypes.c_uint*A)()
        for i,k in enumerate(lTokA):
            lA[i] = k
        lB = (ctypes.c_uint*B)()
        for i,k in enumerate(lTokB):
            lB[i] = k
        lBuf  = (ctypes.c_uint*(B+1))() # Bufs are +1 !
        lBufP = (ctypes.c_uint*(B+1))()
        return getattr(self.lib,'ilar{}GetAlignScore'.format(sVar))(lA, A, lB, B, lBuf, lBufP)
    




### Score is not permutative
##def scoreSimA(lTokA, lTokB):
##    sc11 = scoreBlocksSimA(lTokA, detectBlocks(lTokA))
##    sc22 = scoreBlocksSimA(lTokB, detectBlocks(lTokB))
##    sc12 = scoreBlocksSimA(lTokA, detectBlocks(lTokB))
##    return 2*sc12/(sc11+sc22)
##def scoreBlocksSimA(lTokin,llTokin):
##    return sum(wrapSimAGetAlignScore(lTokin,block) for block in llTokin)
##
##
### Score is not permutative
##def scoreSimB(lTokA, lTokB):
##    sc11 = scoreBlocksSimB(lTokA, detectBlocks(lTokA))
##    sc22 = scoreBlocksSimB(lTokB, detectBlocks(lTokB))
##    sc12 = scoreBlocksSimB(lTokA, detectBlocks(lTokB))
##    return 2*sc12/(sc11+sc22)
##def scoreBlocksSimB(lTokin,llTokin):
##    return sum(wrapSimBGetAlignScore(lTokin,block) for block in llTokin)






#-------------------------------------------------------------------------------
# Workers functions.
# A worker should be assigned a queue, from which it extracts method
#  which is to be used and files to be compared.
#-------------------------------------------------------------------------------


# The worker bufferize calls to the DB, in order to avoid weird behaviors.
#  To Be Tested...
def workerCompare(sDB, bEnd, qTriples):
    lTriples = []
    dao = DAO(sDB, timeout=30)
    dlTokens = dao.getTokensDict()
    libplagia = LibPlagia()
    dResults = {} # {sMeth:[(sFileA,sFileB,fSc)], ...}
    while not bEnd.value:
        if not qTriples.empty():
            N = min(qTriples.qsize(), 100)
            for i in range(N):
                # From my experience, you should except a QEmpty here, because of a race condition when a queue is being filled but not yet. Hopefully, waiting up to .5 second should do the trick...
                lTriples.append( qTriples.get(timeout=.5) )
            while lTriples:
                sMeth, sFileA, sFileB = lTriples.pop()
                fScore = libplagia.calcScore(sMeth, dlTokens[sFileA], dlTokens[sFileB])
                if sMeth not in dResults:
                    dResults[sMeth] = []
                dResults[sMeth].append( (sFileA,sFileB,fScore) )
            for sMeth,lScore in dResults.items():
                dao.setCmpList(sMeth,lScore)
        time.sleep(.1) # Do not overhead CPU when there is nothing to do...


# For once, I do a simple process function: it finishes when Queue is empty.
# However, because of the wait() mecanism in sqlite3 implementation, I use a qResults to keep a certain level of efficiency........
# However, because of strange behavior of the sqlite DB, I use a lock. Now I'm sad............
##def workerScoreSimA(qCouples, sDB, qResults, lockDB):
##    while not qCouples.empty():
##        sFileA, sFileB = qCouples.get(False)
##        lockDB.acquire()
##        lTokA, lTokB = dao.getTokens(sFileA), dao.getTokens(sFileB)
##        lockDB.release()
##        qResults.put( (sFileA, sFileB, scoreSimA(lTokA, lTokB) ) )
    # Maybe it would be better to pass a string for which method is to be used.
    # Then, a dao.getTokens(listOfFiles) should be used, to reduce the number of with entry
    # Finally, the write could be done here, but as before, through a list containing a 1000 statements...
##def workerScoreSimB(qCouples, sDB, qResults, lockDB):
##    while not qCouples.empty():
##        sFileA, sFileB = qCouples.get(False)
##        lockDB.acquire()
##        lTokA, lTokB = dao.getTokens(sFileA), dao.getTokens(sFileB)
##        lockDB.release()
##        qResults.put( (sFileA, sFileB, scoreSimB(lTokA, lTokB) ) )


# Thread or Process
##def workerCollectResultsSimA(sDB, qResults, lockDB, bEnd):
##    dao = DAO(sDB)
##    while not bEnd.value:
##        lockDB.acquire()
##        try:
##            while not qResults.empty():
##                t = qResults.get(False)
##                dao.setCmpSimA( *t )
##        except QEmpty:
##            pass
##        finally:
##            lockDB.release()
##        time.sleep(.1)
##def workerCollectResultsSimB(sDB, qResults, lockDB, bEnd):
##    dao = DAO(sDB)
##    while not bEnd.value:
##        lockDB.acquire()
##        try:
##            while not qResults.empty():
##                t = qResults.get(False)
##                dao.setCmpSimB( *t )
##        except QEmpty:
##            pass
##        finally:
##            lockDB.release()
##        time.sleep(.1)



if __name__=='__main__':
    print('Init, DB',sDB)
    dao = DAO(sDB)
    nameToToken = dao.getNameToToken()
if platform.startswith('linux'):
    libplagia = LibPlagia() # Test that lib is compiled
    del libplagia
    print('Check Tokenization...')
##    for f in os.listdir(SOURCE_DIR):
##        try:
##            dao.getTokens(SOURCE_DIR+f, False)
##        except BaseException as e:
##            print('Error with file', f)
##            raise e
    sRecFiles = set(dao.getListOfTokenizedFiles())
    # Tokenize
    dao.genPickleForFiles([SOURCE_DIR+f for f in os.listdir(SOURCE_DIR) if not f in sRecFiles])
    # Updates nameToToken
    dao.setNameToToken(nameToToken)
##    lQueuesA = [Queue() for i in range(N_PROCESS//2)]
##    lQueuesB = [Queue() for i in range(N_PROCESS//2)]
##    lFiles = dao.getTokenizedFiles()
##    print('Dispatching up to {} tests on {} processes...'.format(len(lFiles)*(len(lFiles)-1)*2, N_PROCESS))
##    N = 0
##    for cpl in permutations(lFiles, 2):
##        if not dao.getCmpSimA(*cpl):
##            lQueuesA[N%(N_PROCESS//2)].put(cpl)
##            N += 1
##        if not dao.getCmpSimB(*cpl):
##            lQueuesB[N%(N_PROCESS//2)].put(cpl)
##            N += 1
##    print('Dispatched {} tests, starting processes...'.format(N))
    # Prepares multi-processing
    lQueues = [Queue() for i in range(N_PROCESS)]
    lFiles = dao.getListOfTokenizedFiles()
    print('Dispatching up to {} tests on {} processes...'.format(len(lFiles)*(len(lFiles)-1)*len(LibPlagia.METHODS), N_PROCESS))
    N = 0
    for sMeth in LibPlagia.METHODS:
        for cpl in permutations(lFiles, 2):
            tTrip = (sMeth,)+cpl
            if not dao.getCmp(*tTrip):
                lQueues[N%N_PROCESS].put(tTrip)
                N += 1
    print('Dispatched {} tests, starting processes...'.format(N))
##    qResA = Queue()
##    qResB = Queue()
##    lockDB = Lock()
##    bEnd = Value('b')
##    thA = Process(target=workerCollectResultsSimA, args=(sDB, qResA, lockDB, bEnd)) # Less race conditions when Process
##    thB = Process(target=workerCollectResultsSimB, args=(sDB, qResB, lockDB, bEnd))
##    thA.start()
##    thB.start()
##    lP  = [Process(target=workerScoreSimA, args=(q, sDB, qResA, lockDB)) for q in lQueuesA]
##    lP += [Process(target=workerScoreSimB, args=(q, sDB, qResB, lockDB)) for q in lQueuesB]
##    for p in lP: p.start()
##    def checkProgress():
##        print('Remaining {}+{} tests'.format(sum(map(lambda q:q.qsize(), lQueuesA)), sum(map(lambda q:q.qsize(), lQueuesB))))
##    def waitEnd():
##        for p in lP: p.join()
##        bEnd.value = True
##        thA.join()
##        thB.join()
    bEnd = Value('b')
    lP = [Process(target=workerCompare, args=(sDB, bEnd, q)) for q in lQueues]
    for p in lP: p.start()
    def checkProgress():
        print('Remaining {} tests'.format(sum(map(lambda q:q.qsize(), lQueues))))
    def waitEnd():
        bEnd.value = True
        for p in lP: p.join()
    print('\ncheckProgress()')
    print('waitEnd()')
elif False:
##    for a,b,c in sorted(dao.getCmpSimAList(), key=lambda t:t[2]):
##        if c>.4:
##            if b[15] != a[15]:
##                print('{:.3f} # {} ## copie ## {}'.format(c, b[17:], a[17:]))
##            else:
##                print('{:.3f}   {} ## copie ## {}'.format(c, b[17:], a[17:]))
##    print('------------------------------------------------------------------------------------')
##    for a,b,c in sorted(dao.getCmpSimBList(), key=lambda t:t[2]):
##        if c>.4:
##            if b[15] != a[15]:
##                print('{:.3f} # {} ## copie ## {}'.format(c, b[17:], a[17:]))
##            else:
##                print('{:.3f}   {} ## copie ## {}'.format(c, b[17:], a[17:]))
    N = 0
    for a,b,c in sorted(dao.getCmpList('SimA'), key=lambda t:t[2]):
        if c>.4:
            if b[15] != a[15]:
                print('{:.3f} # {} ## copie ## {}'.format(c, b[17:], a[17:]))
            else:
                print('{:.3f}   {} ## copie ## {}'.format(c, b[17:], a[17:]))
            N += 1
    print('------------------------------------------------------------------------------------')
    print(N, 'above threshold')
    print('------------------------------------------------------------------------------------')
    N = 0
    for a,b,c in sorted(dao.getCmpList('SimB'), key=lambda t:t[2]):
        if c>.4:
            if b[15] != a[15]:
                print('{:.3f} # {} ## copie ## {}'.format(c, b[17:], a[17:]))
            else:
                print('{:.3f}   {} ## copie ## {}'.format(c, b[17:], a[17:]))
            N += 1
    print('------------------------------------------------------------------------------------')
    print(N, 'above threshold')
    print('------------------------------------------------------------------------------------')

    















