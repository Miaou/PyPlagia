#!/usr/bin/python3
# Test de la lib
# Il faudrait des tests plus sérieux, en particulier pour vérifier que je me suis pas planté dans les indices dans les algos...
#  (ce qui est arrivé au moins une fois)
# Et tester la symétrie

import ctypes
from sys import platform
#import random
import time


if platform.startswith('linux'): # win32
    LIB_PATH='./libplagia.so' # Le './' est important
else:
    LIB_PATH='libplagia.dll'



if __name__=='__main__':
    # strAlignScore("dudu dodo toto", "toto")
    libplagia = ctypes.cdll.LoadLibrary(LIB_PATH)
    lToto = (ctypes.c_uint*4)(*list(map(ord,"toto")))
    lBuf = (ctypes.c_uint*5)() # 4+1 pour les méthodes ilar, 4 pour sim.
    lBufP = (ctypes.c_uint*5)()
    lBig = (ctypes.c_uint*14)(*list(map(ord,"dudu dodo toto")))

    print( libplagia.simAGetAlignScore(lBig, 14, lToto, 4, lBuf, lBufP) )
    print( libplagia.simBGetAlignScore(lBig, 14, lToto, 4, lBuf, lBufP) )
    print( libplagia.ilarAGetAlignScore(lBig, 14, lToto, 4, lBuf, lBufP) )
    print( libplagia.ilarBGetAlignScore(lBig, 14, lToto, 4, lBuf, lBufP) )
    







