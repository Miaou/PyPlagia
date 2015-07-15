#
# This is where batch-work is defined: workers for multiprocessing and so on
# This is a good example of how-to use the libplagia module...
# pyplagia, Pierre-Antoine BRAMERET (C) 2014




import os
from multiprocessing import Queue, Process, Lock, Value
from threading import Thread
from queue import Empty as QEmpty

from . import time
from . import DAO
from . import LibPlagia



#-------------------------------------------------------------------------------
# Workers functions.
# A worker is the basis of the multiprocesing: one is called for each subprocess.
# A worker should be assigned a queue, from which it extracts the comparison method
#  which is to be used and files to be compared.
#-------------------------------------------------------------------------------


# The worker bufferize calls to the DB, in order to avoid weird behaviors.
#  Seems conclusive.
def workerCompare(sDB, bEnd, qTriples, nBuffered):
    lTriples = []
    dao = DAO(sDB, timeout=30)
    libplagia = LibPlagia()
    libplagia.readPickleCache(dao) # Loads up the pickled files
    dResults = {} # {sMeth:[(sFileA,sFileB,fSc)], ...}
    while not bEnd.value:
        if not qTriples.empty():
            N = min(qTriples.qsize(), nBuffered)
            for i in range(N):
                # From my experience, you should except a QEmpty here, because of a race condition when a queue is being filled but not yet. Hopefully, waiting up to .5 second should do the trick...
                lTriples.append( qTriples.get(timeout=.5) )
            while lTriples:
                sMeth, sFileA, sFileB = lTriples.pop()
                fScore = libplagia.calcScore(sMeth, sFileA, sFileB)
                if sMeth not in dResults:
                    dResults[sMeth] = []
                dResults[sMeth].append( (sFileA,sFileB,fScore) )
            for sMeth,lScore in dResults.items():
                dao.setCmpList(sMeth,lScore)
        time.sleep(.1) # Do not overhead CPU when there is nothing to do...




#-------------------------------------------------------------------------------
# Dealing with multiprocessing
#-------------------------------------------------------------------------------


# Multiprocessing requires a "context", which stores the end(), start(), the queues, and so on...
class MultiContext:
    def __init__(self, nWorkers, sDB, nBufferedScoring=100):
        self.nWorkers = nWorkers
        self.sDB = sDB
        #self.dao = DAO(sDB)
        self.nBuffered = nBufferedScoring
        libplagia = LibPlagia() # Tests that lib is build before launching N_PROCESS without target...

        # Assert tokentization ???

        self.lQueues = [Queue() for i in range(self.nWorkers)]
        self.bEnd = Value('b')
        self.bEnd.value = False
        self.lP = [Process(target=workerCompare, args=(self.sDB, self.bEnd, q, self.nBuffered))
                   for q in self.lQueues]

    def dispatchScoreRequest(self, lTrip):
        '''Where lTripl = [(sMeth, sFileA, sFileB), ...]
           Returns the list of yet to intify files (for which tests are ignored)'''
        # This "checking" behavior should prevent processi from crashing,
        #  for the LibPlagia is not yet tolerant to non-prepared files. (see LibPlagia.calcScore)
        ddMethFileInts = DAO(self.sDB).getIntifiedFiles()
        lTripOk = []
        lToDo = []
        for trip in lTrip:
            sMeth, sFileA, sFileB = trip
            assert sMeth in LibPlagia.METHODS
            sMethPick = LibPlagia.METHODStoMETHODS_PICKLING[sMeth]
            bAdd = True
            if not sFileA in ddMethFileInts[sMethPick]:
                lToDo.append(sFileA)
                bAdd = False
            if not sFileB in ddMethFileInts[sMethPick]:
                lToDo.append(sFileB)
                bAdd = False
            if bAdd:
                lTripOk.append( trip )
        print('MultiContext.dispatchScoreRequest: Dispatching {} ok-requests out of {} requests'.format(len(lTripOk), len(lTrip)))
        i = 0
        for trip in lTrip:
            # Does not filter, as one may want to re-do some tests.
            self.lQueues[i%self.nWorkers].put(trip)
            i += 1
        return lToDo
        

    def start(self):
        if self.bEnd.value:
            print('Processi are not meant to be restarted once ended...')
            return False
        for p in self.lP:
            p.start()
        return True

    def checkProgress(self):
        nInQ = sum(map(lambda q:q.qsize(), self.lQueues))
        print('Remaining {} to {} tests.{}'.format(nInQ+self.nBuffered*len(self.lQueues), nInQ,
              (not all(p.is_alive() for p in self.lP) and ' (but {}/{} processi are dead)'.format(
                  sum( 1 if p.is_alive() else 0 for p in self.lP ), self.nWorkers))
              or '') )
        
    def end(self):
        'Ends current session, waiting for at most nBuffered scores'
        self.bEnd.value = True
        print('Waiting for processi to finish their batch')
        for p in self.lP:
            p.join()
        return True

    def waitCompletion(self):
        'Ends current session after it is finished'
        while sum(map(lambda q:q.qsize(), self.lQueues)):
            if all(not p.is_alive() for p in self.lP):
                print('MultiContext.waitCompletion: All the processes died but the queues are not empty\n (somthing went (partially)-wrong)')
                break
            self.checkProgress()
            time.sleep(10)
        return self.end()









