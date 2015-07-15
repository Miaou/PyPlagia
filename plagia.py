#
# "Faiseur" des calculs
# pyplagia, Pierre-Antoine BRAMERET (C) 2014
#  (mail to pa.brameret at gmail if you need support)



FORCE_RECALC = False
sDB = 'plagia.db'
SOURCE_DIR = 'codesEleves/'
N_WORKERS = 24


import os
import pyplagia
import argparse
import time # Year







if __name__=='__main__':
    # Command-line
    # If the folder argument is specified, the selected subfolder is used to calculate all the missing similarity data.
    # Otherwise, the IDLE-like interactive mode is assumed.
    parser = argparse.ArgumentParser(description='Calculate the scores of similarity for all files in the selected folder (prepend current year to filename if necessary).\n'+
                                     'If folder is not specified, nothing is done through the command line (so that the script is interactive, as usual)\n'+
                                     'By default, all files are compared to all other files. To compare works from this year to all others, use -y or -Y',
                                     epilog='Typical usage: python3 plagia.py -n 24 -y plagia.db codesEleves/')
    parser.add_argument('-f', '--force-recalc', dest='bForceRetoken', action='store_true',
                        help='Forces the re-tokenization of all files present in folder for every available method AND re-does the scoring for these files (you should delete the database instead of specifying -f...)')
    parser.add_argument('-n', '--n-workers', dest='nWorkers', default=4, type=int,
                        help='Number of parallel workers used')
    parser.add_argument('-N', '--N-buffer-size', dest='nBuffSize', default=100, type=int,
                        help='Buffer size when writting the database (1 is too low, and concurrent database access may crash the workers, 1000000 might saturate the memory, 100 is good)')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-y', '--this-year', dest='bThisYear', action='store_true',
                        help='Compare only the codes from this year (we are in {}) between them and to older codes. See -Y to specify a another year'.format(time.localtime().tm_year))
    group.add_argument('-Y', '--year', dest='iYear', default=0, type=int,
                        help='Same as -y, as if we were in year IYEAR (-Y {} is the same as -y)'.format(time.localtime().tm_year))
    parser.add_argument('database', nargs='?', help='The database filename') # Can't rename positional args
    parser.add_argument('folder', nargs='?', help='Path to folder containing python sources')
    # La visualisation des résultats reste un problème... Il faut spécifier un threshold par méthode, c'est donc pas trop adapté à la ligne de commande...
    # D'autant que ça risque d'être volumineux...
    # Ou alors dans un autre script...
    args = parser.parse_args()
    args.sDB = args.database
    args.sSrcPath = args.folder

    if args.sSrcPath:
        # Non-interactive mode, "calculator"-mode
        # 0) Preps
        dao = pyplagia.DAO(args.sDB)
        libplagia = pyplagia.LibPlagia()
        # 1) Explores folder and tokenize/intify files as needed (this should be provided by pyplagia...)
        print('Pickling new files...')
        libplagia.pickleFolderToDAO(args.sSrcPath, dao, args.bForceRetoken)
        # 2) Creates the "to-do" list (should be provided by pylapgia too)
        print('Building ToDo list...')
        if not args.bThisYear and not args.iYear:
            lToDo = dao.prepareToDoList(args.bForceRetoken)
        else:
            if args.bThisYear:
                args.iYear = time.localtime().tm_year
                print('\n--> Doing year {} against them and below <--'.format(args.iYear))
            lToDo = dao.prepareToDoList_yearBelow(args.bForceRetoken, args.iYear)
        # 3) Creates the multiprocessing context
        ctx = pyplagia.MultiContext(args.nWorkers, args.sDB, args.nBuffSize)
        # 4) Gives it the todo list
        print('Dispatching ToDo list and starting processi...')
        lBadlyDone = ctx.dispatchScoreRequest(lToDo)
        if lBadlyDone:
            print('Something went wrong: pickling may have not be recorded correctly')
        # 5) And starts
        assert ctx.start()
        # 6) Waits until it is done.
        print('Waiting until completion...')
        try:
            ctx.waitCompletion()
        except KeyboardInterrupt:
            print('Things are still running in the background')
    else:
        # "IDLE"-mode
        print('Use python plagia.py -h to obtain help on the command line mode.\n')
        print('# 0) Preps\ndao = pyplagia.DAO(sDB)\nlibplagia = pyplagia.LibPlagia()')
        print('# 1) Explores folder and tokenize/intify files as needed\n#  (this prepend filenames with {}_ when necessary)\nlibplagia.pickleFolderToDAO(SOURCE_DIR, dao, FORCE_RECALC)'.format(time.localtime().tm_year))
        print('# 2) Creates the "to-do" list\nlToDo = dao.prepareToDoList(args.bForceRetoken)')
        print('# 3) Creates the multiprocessing context\nctx = pyplagia.MultiContext(N_WORKERS, sDB, 100)')
        print('# 4) Gives it the todo list and starts\nlBadlyDone = ctx.dispatchScoreRequest(lToDo)\nassert ctx.start()')
        print('# 5) Waits until it is done.\nctx.waitCompletion()')
        print('# 6) Get Results')
        print('dTop = dao.getTopPlagia(nTop=10)')
        print('dao.displayTopPlagia(nTop=10)')
        print('\n# 7) Test a single file against the others.\nctx = pyplagia.SingleContext(sDB)\nctx.testSingleFileAgainstDB(sFile)')



# Changes:
# - changer la détection de l'année dans un nom de fichier. Ce devrait être une fonction plus clean que ça, et unifromiser (3 occurences dans DAO)
# - voir pourquoi on a du négatif sur les Ilar








