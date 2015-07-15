#
# This is similar to batch.py, but we define here single operations.
#  That is to say, single file test against other references.
# This is also a good example of how-to use the libplagia module...

# The goal of this context is to test a single file against all the others,
#  WITHOUT inserting it in the DB.
#  A single test, with no consequences...

# pyplagia, Pierre-Antoine BRAMERET (C) 2014


from . import pickle

from . import DAO
from . import LibPlagia




#-------------------------------------------------------------------------------
# Dealing with singleprocessing
#-------------------------------------------------------------------------------


class SingleContext:
    def __init__(self, sDB):
        self.sDB = sDB
        self.libplagia = LibPlagia() # Tests that lib is build before launching further tests...
        self.dao = DAO(sDB)
    
    def testSingleFileAgainstDB(self, sFile):
        # This functions touches deep API. Maybe it should be wrapped in LibPlagia somewhere,
        #  but it is not that obvious.
        
        # 0) Load Cache
        print('Read Cache')
        self.libplagia.readPickleCache(self.dao)
        
        # 1) Pickle file, and de-picklie it and stores it in the cache
        print('Pickling')
        ddTokenToInt = self.libplagia.getAndInitDictsTokenToInt(self.dao)
        dPickledFile = {}
        for sMethPick in LibPlagia.METHODS_PICKLING:
            try:
                bData = self.libplagia.pickleFile(sMethPick, sFile, ddTokenToInt[sMethPick])
                self.libplagia._ddMethFileInts[sMethPick][sFile] = pickle.loads(bData) # This is an ugly hack. Never do this at home.
            except SyntaxError:
                print('SingleContext.testSingleFileAgainstDB: syntax error in file "{}"'.format(sFile))
        
        # 2) Does the calcScore (similar to build a todo list and then execute, but avoids intermediate steps)
        N = 0
        ddMethFileInts = self.dao.getIntifiedFiles()
        ddResults = {} # {sMeth:{sFileA:fSc}, ...}
        print('Scoring... ({} tests)'.format(len(ddMethFileInts[LibPlagia.METHODStoMETHODS_PICKLING[LibPlagia.METHODS[0]]])*len(LibPlagia.METHODS)))
        for sMeth in LibPlagia.METHODS:
            sMethPick = LibPlagia.METHODStoMETHODS_PICKLING[sMeth]
            dFileInts = ddMethFileInts[sMethPick]
            ddResults[sMeth] = {}
            for sFileA in dFileInts:
                ddResults[sMeth][sFileA] = self.libplagia.calcScore(sMeth, sFileA, sFile)
                N += 1
                if N%10==0:
                    print('.', end='')
        
        # 3) Print results
        print('\n'*2+'-'*70)
        print(sFile)
        for sMeth in LibPlagia.METHODS:
            print('\n'+'-'*70+'\n'+sMeth+'\n')
            iSuf = sFile.find('/20')+1
            for sFileA in sorted(ddResults[sMeth], key=lambda k:-ddResults[sMeth][k]):
                iSufA = sFileA.find('/20')+1
                print('{:.3f} {}'.format(ddResults[sMeth][sFileA], sFileA[iSufA:]))
           
    
    
    
