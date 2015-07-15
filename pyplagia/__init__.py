#
# py-libplagia package! See ../README for more details.
# Does the imports in the right order.
# pyplagia, Pierre-Antoine BRAMERET (C) 2014


'''
This is a complex but generic way to calculate (efficiently) and gather results
 about plagiarism in SAPHIRE.
This was designed around algorithms found in literrature:
 -
 -

The generic principle (and API) is twofold:
 - each homework is lexic-ized/parsed/... to obtain tokens/graphs
   (stored (pickled) into a DB for better performance)
 - homeworks are compared one another (through there tokens and special algorithms
   (which are implemented in C because of performance issues))
Results of the comparions are store into the DB, for each comparison method, normalized between 0 and 1
Finally, threshold are applied to find "most similar" works.

Behind that, the lib is split into several modules and classes
 - LibPlagia: user frontend and wrapper of the C-functions
 - DAO: Data Access Object: database interface. Use *only* this to access the database.
 - sim.py: Python methods used by sim (tokenization)
 - ilar.py: Python methods used by ilar (tokenization)
 - batch: shows a worker (good example of how the lib works) and help with multiprocessing
'''




import time
import pickle
#from sim import DicIncr, intifyTokens, simDetectBlocks, scoreBlocksSim
#from ilar import intifyAndCutAST
from . import sim
from . import ilar
from .libplagia import LibPlagia
from .dao import DAO
from .batch import MultiContext
from .single import SingleContext

#del DicIncr, intifyTokens, intifyAndCutAST
del sim, ilar, libplagia, dao, batch, single, time, pickle









