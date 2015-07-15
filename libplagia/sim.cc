// Sign here.

// Sim: A Utility For Detecting Similarity in Computer Programs; David Gitchell and Nicholas Tran, 1999


#include "utils.h"


// lbSc and lbScP are buffers and should be of size at least nSmall
LIBPLAGIA_API int simAGetAlignScore(int *lBig, int nBig, int *lSmall, int nSmall, int *lbSc, int *lbScP)
{
    int i,j;
    int scMax = 0;
    
    if(!lBig || !lSmall || !lbSc || !lbScP)
        return -1;
    
    for(j=0; j<nSmall; ++j)
    {
        lbScP[j] = simAScoreCouple(lBig[0], lSmall[j]);
        if(lbScP[j] < 0)
            lbScP[j] = 0;
    }
    
    for(i=1; i<nBig; ++i)
    {
        for(j=0; j<nSmall; ++j)
        {
            if(j>0)
                lbSc[j] = _max(lbScP[j-1]+simAScoreCouple(lBig[i],lSmall[j]),
                                 lbScP[j]-2,
                                 lbSc[j-1]-2,
                                 0);
            else
                lbSc[j] = _max(simAScoreCouple(lBig[i],lSmall[j]),
                                 lbScP[j]-2,
                                 0);
            if(lbSc[j]>scMax)
                scMax = lbSc[j];
        }
        for(j=0; j<nSmall; ++j)
            lbScP[j] = lbSc[j]; // I should have exchanged pointers instead of that full copy. Maybe when comparing performances, it should be done...
    }
    
    return scMax;
}

// lbSc and lbScP are buffers and should be of size at least nSmall
LIBPLAGIA_API int simBGetAlignScore(int *lBig, int nBig, int *lSmall, int nSmall, int *lbSc, int *lbScP)
{
    int i,j;
    int scMax = 0;
    
    if(!lBig || !lSmall || !lbSc || !lbScP)
        return -1;
    
    for(j=0; j<nSmall; ++j)
    {
        lbScP[j] = simBScoreCouple(lBig[0], lSmall[j]);
        if(lbScP[j] < 0)
            lbScP[j] = 0;
    }
    
    for(i=1; i<nBig; ++i)
    {
        for(j=0; j<nSmall; ++j)
        {
            if(j>0)
                lbSc[j] = _max(lbScP[j-1]+simBScoreCouple(lBig[i],lSmall[j]),
                               lbScP[j]-2,
                               lbSc[j-1]-2,
                               0); // useless: simBScore >= 0 ans lbScP too
            else
                lbSc[j] = _max(simBScoreCouple(lBig[i],lSmall[j]),
                               lbScP[j]-2,
                               0); // useless: simBScore >= 0
            if(lbSc[j]>scMax)
                scMax = lbSc[j];
        }
        for(j=0; j<nSmall; ++j)
            lbScP[j] = lbSc[j];
    }
    
    return scMax;
}






