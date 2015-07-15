#
# "Main" part of the libplagia !
# LibPlagia provides a generic API
#  while being responsible for calls to the C-libplagia, caching, and pickling.
# Does not touch data.

# pyplagia, Pierre-Antoine BRAMERET (C) 2014



import os
from sys import platform
from . import pickle
import ctypes
import tokenize
import unicodedata
from . import time


from . import sim #simDetectBlocks, scoreBlocksSim
from . import ilar



#-------------------------------------------------------------------------------
# LibPlagia: its role is not really bounded for now.
#  It should handle all wrappings and for now, it handles scoring too.
# LibPlagia should be renamed to something like PlagiaCalc or PlagiaWrap
#-------------------------------------------------------------------------------
class LibPlagia:
    METHODS = ('SimA', 'SimB', 'IlarA', 'IlarB') # Methods are not case sensitive in the DB! But everywhere else!
    METHODS_PICKLING = ('Sim', 'Ilar')
    METHODStoMETHODS_PICKLING = {'SimA':'Sim', 'SimB':'Sim',
                                'IlarA':'Ilar', 'IlarB':'Ilar'}
    #METHODS_PICKLINGtoNAME_DICT_TOKEN = {'Sim': 'nameToToken',
    #                                     'Ilar': 'nodeToToken'}
    def __init__(self):
        if platform.startswith('linux'): # win32
            LIB_PATH='./libplagia/libplagia.so' # Le './' est important
        else:
            LIB_PATH='libplagia/libplagia.dll'
        if not os.path.isfile(LIB_PATH):
            print('LibPlagia.__init__: The libplagia.dll/.so was not found, trying to compile it...')
            os.system('make -Clibplagia all')
        self._lib = ctypes.cdll.LoadLibrary(LIB_PATH)
        self._ddMethFileInts = {}
        self.bCacheWarned = False # ~ useful, stores if the user has been warned about a incomplete/missing cache


    
    #----------------------------------
    # Inits
    #----------------------------------
    def getAndInitDictsTokenToInt(self, dao):
        ddTokenToInt = dao.getDictsTokenToInt()
        if 'Sim' not in ddTokenToInt:
            ddTokenToInt['Sim'] = sim.initNameToToken()
        if 'Ilar' not in ddTokenToInt:
            ddTokenToInt['Ilar'] = ilar.initNodeToToken()
        return ddTokenToInt


    
    #----------------------------------
    # Pickling
    #----------------------------------
    def pickleFile(self, sMethPick, sFile, dTokenToInt):
        '''Where dTokenToInt is either sim.nameToToken or ilar.nodeToToken
           (which may be modified (LibPlagia is not responsible for updating dTokenToInt in dao))'''
        # Does not stores results in DB: it is not good to insert only one file at a time...
        assert sMethPick in LibPlagia.METHODS_PICKLING # Yes, we check the method but don't check the dTokenToInt
        if sMethPick == 'Sim':
            with open(sFile, 'rb') as f:
                return pickle.dumps( sim.intifyTokens(list(tokenize.tokenize(f.readline)),dTokenToInt) )
        elif sMethPick == 'Ilar':
            return pickle.dumps( ilar.intifyAndCutAST(sFile,dTokenToInt) )

    # Helper
    def pickleFolderToDAO(self, sPath, dao, bForceRepickle):
        if not sPath[-1] in ('\\','/'):
            sPath += '/'
        ddMethFileInts = dao.getIntifiedFiles()
        ddTokenToInt = self.getAndInitDictsTokenToInt(dao)
        dlPickledFiles = {sMethPick:[] for sMethPick in LibPlagia.METHODS_PICKLING}
        lFiles = []
        for f in os.listdir(sPath):
            if not (f[:4].isdecimal() and f[4] == '_'):
                fNew = '{}_'.format(time.localtime().tm_year) + unicodedata.normalize('NFD', f).encode('ASCII', 'ignore').decode().replace('.py.py','.py').replace(' ', '_')
                os.rename(sPath+f, sPath+fNew)
                f = fNew
            sFile = sPath + f
            lFiles.append(sFile)
            for sMethPick in LibPlagia.METHODS_PICKLING:
                if bForceRepickle or not sFile in ddMethFileInts[sMethPick]:
                    try:
                        bFile = self.pickleFile(sMethPick, sFile, ddTokenToInt[sMethPick])
                        dlPickledFiles[sMethPick].append( (sFile,bFile) )
                    except SyntaxError:
                        print('LibPlagia.picckleFolderToDAO: syntax error in file "{}"'.format(sFile))
        for sMethPick in dlPickledFiles:
            dao.setPickleForFiles(sMethPick, dlPickledFiles[sMethPick])
        dao.setDictsTokenToInt(ddTokenToInt)
        for dTokenInt in ddTokenToInt.values():
            dTokenInt.setReadOnly()
        


    #----------------------------------
    # Caching
    #----------------------------------
    def readPickleCache(self, dao):
        'Reads the ddMethFileInts from the dao (which should be a dao.DAO (not asserted))'
        self._ddMethFileInts = dao.getIntifiedFiles()
    

    #----------------------------------
    # Scoring/wrapping
    #----------------------------------
##    def calcScore(self, sMeth, lTokA, lTokB):
##        assert sMeth in LibPlagia.METHODS
##        if sMeth in ('SimA','SimB'):
##            #return self._wrapSimGetAlignScore(sMeth[3:], lTokA, lTokB)
##            sim.scoreBlocksSim = lambda lTokin,llTokin: sum(self._wrapSimGetAlignScore(sMeth[3:], lTokin, block) for block in llTokin)
##            llTokB = sim.simDetectBlocks(lTokB)
##            sc11 = sim.scoreBlocksSim(lTokA, sim.simDetectBlocks(lTokA))
##            sc22 = sim.scoreBlocksSim(lTokB, llTokB)
##            sc12 = sim.scoreBlocksSim(lTokA, llTokB)
##            return 2*sc12/(sc11+sc22)
##        raise ValueError # Should never be raised, but will remind me if I forgot to implement an authorised methods...
    def calcScore(self, sMeth, sFileA, sFileB):
        assert sMeth in LibPlagia.METHODS
        if not self._ddMethFileInts and not self.bCacheWarned:
            print('LibPlagia.calcScore: performance issue: no cache found')
            self.bCacheWarned = True # Useless for now: a KeyError will be raised soon.
        if sMeth in ('SimA','SimB'):
            #sMethPick, sVar = sMeth[:3], sMeth[3:]
            sMethPick = LibPlagia.METHODStoMETHODS_PICKLING[sMeth]
            sVar = sMeth[3:]
            # Incompletion of the cache will raise a KeyError for now.
            lTokA = self._ddMethFileInts[sMethPick][sFileA]
            lTokB = self._ddMethFileInts[sMethPick][sFileB]
            scoreBlocksSim = lambda lTokin,llTokin: sum(self._wrapSimGetAlignScore(sVar, lTokin, block) for block in llTokin)
            llTokB = sim.simDetectBlocks(lTokB)
            sc11 = scoreBlocksSim(lTokA, sim.simDetectBlocks(lTokA))
            sc22 = scoreBlocksSim(lTokB, llTokB)
            sc12 = scoreBlocksSim(lTokA, llTokB)
            return 2*sc12/(sc11+sc22)
        elif sMeth in ('IlarA', 'IlarB'):
            sMethPick = LibPlagia.METHODStoMETHODS_PICKLING[sMeth]
            sVar = sMeth[4:]
            llTokA = self._ddMethFileInts[sMethPick][sFileA]
            llTokB = self._ddMethFileInts[sMethPick][sFileB]
            meanList = lambda l: sum(l)/len(l)
            scoreBlocksIlar = lambda llTokA, llTokB: meanList( [max([self._wrapIlarGetAlignScore(sVar, lTokA, lTokB) for lTokB in llTokB]) for lTokA in llTokA] )
            sc11 = scoreBlocksIlar(llTokA, llTokA)
            sc22 = scoreBlocksIlar(llTokB, llTokB)
            sc12 = scoreBlocksIlar(llTokA, llTokB)
            return .5 + sc12/(sc11+sc22)
        raise ValueError # Should never be raised, but will remind me if I forgot to implement an authorised methods...
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
        return getattr(self._lib,'sim{}GetAlignScore'.format(sVar))(lA, A, lB, B, lBuf, lBufP)
    def _wrapIlarGetAlignScore(self, sVar, lTokA, lTokB): # Should be done for llA, llB directly, while choosing the largest buffer. It would avoid to create them so much time...
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
        return getattr(self._lib,'ilar{}GetAlignScore'.format(sVar))(lA, A, lB, B, lBuf, lBufP)












    








