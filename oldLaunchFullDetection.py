#
# Launches the N //-processes to do the job (before that, it prepares the DB (pickling where necessary)).

# Old Lib Version
# PLEASE DO NOT USE THIS FILE

assert False, "PLEASE, DO NOT USE THIS OLD FILE, it works with an older version of the lib"

from pyplagia.batch import workerCompare
from pyplagia import DAO



FORCE_RECALC = False
sDB = 'plagia.db'
SOURCE_DIR = 'codesEleves/'
# On too much procs, very strange errors using sqlite3 database ("database disk image is malformed" or "file is encrypted or is not a database" (!!!))
#  and race condition using mutiprocessing.Lock (tested ok with 8)
# Hmm, further analysis leads to weirder results: when the threads are replaced by processes (for writing the DB), less race conditions...
#  however, these leads to "disappearing processes": processes that stop without error! (hmm, they may just have finish their unbalanced queue...)
N_PROCESS = 24



# TO BE TRANSFERED TO batch.py


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
