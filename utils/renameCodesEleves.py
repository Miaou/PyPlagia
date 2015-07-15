#
# Pour pré-fixer les noms de fichier par l'année
# PAB 2014


import os
import unicodedata
os.chdir('codesEleves')


for sAn in os.listdir('.'):
    if os.path.isdir(sAn):
        for f in os.listdir(sAn):
            fNew = unicodedata.normalize('NFD', f).encode('ASCII', 'ignore').decode().replace('.py.py','.py').replace(' ', '_')
            os.rename(sAn+'/'+f,sAn+'_'+fNew)
        if not os.listdir(sAn):
            os.removedirs(sAn)



