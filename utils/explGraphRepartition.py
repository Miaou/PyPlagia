#
# Exemples de graphes qu'on peut obtenir sur la DB
# PAB 2014


import os, sys
os.chdir('..'); sys.path.append(os.path.abspath('.'))

import pyplagia
print('Import pylab...', end='')
import pylab
print(' Ok.')


sDB = 'plagia.db'
N_TRANCHES = 100


# Le DAO a une fonction qui permet de regrouper les résultats des comparaisons par tranches de score,
#  dans le but de tracer une espèce de Gaussiennne et de voir le score moyen de similarité
# (sur tous les tests qui ont été faits dans la DB jusqu'à présent) (en 2014, ce sont les scores de 2014 avec les années précédentes (2014 inclue))
dao = pyplagia.DAO(sDB)
dRepart = {sMeth:dao.getRepartition(sMeth, N_TRANCHES) for sMeth in pyplagia.LibPlagia.METHODS}
lX = pylab.array(range(N_TRANCHES))/N_TRANCHES # Affichage du score entre 0 et 1
for sMeth,lV in dRepart.items():
    pylab.plot(lX, lV, 'x-', label=sMeth)
pylab.title('Répartition des scores en fct de la méthode de calcul')
pylab.xlabel('Score')
pylab.ylabel('Nombre d\'occurences')
pylab.legend()
pylab.gcf().set_size_inches(8.3, 5)
pylab.savefig('Stats2014.svg', facecolor='none',edgecolor='none',dpi=90)
pylab.close()
for sMeth,lV in dRepart.items():
    pylab.plot(lX[int(N_TRANCHES*.75):], lV[int(N_TRANCHES*.75):], 'x-', label=sMeth)
pylab.title('Répartition des scores en fct de la méthode de calcul (highscores)')
pylab.xlabel('Score')
pylab.ylabel('Nombre d\'occurences')
pylab.legend()
pylab.gcf().set_size_inches(8.3, 5)
pylab.savefig('Stats2014_zoom.svg', facecolor='none',edgecolor='none',dpi=90)
pylab.close()




