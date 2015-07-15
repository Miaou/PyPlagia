// Sign here.

// Ilar: A Source Code Plagiarism Detecting Method Using Alignment with Abstract Syntax Tree Elements; Hiroshi Kikuchi, Takaaki Goto, Mitsuo Wakatsuki, Tetsuro Nishino, 2014

#include "utils.h"



// lbSc and lbScP are buffers and should be of size at least (nSmall+1)
// (nSmall can be bigger than nBig, but it is memory inefficient...)
LIBPLAGIA_API int ilarAGetAlignScore(int *lBig, int nBig, int *lSmall, int nSmall, int *lbSc, int *lbScP)
{
    int i,j;
    int *lbTmp;
    
    if(!lBig || !lSmall || !lbSc || !lbScP)
        return -1;
    
    // This is j==0
    for(i=0; i<nSmall+1; ++i)
        lbScP[i] = (-2)*i;
    
    for(j=1; j<nBig+1; ++j)
    {
        lbSc[0] = (-2)*j;
        for(i=1; i<nSmall+1; ++i)
            lbSc[i] = _max(lbScP[i-1]+simAScoreCouple(lBig[j-1], lSmall[i-1]),
                           lbScP[i]-2,
                           lbSc[i-1]-2);
        lbTmp = lbSc;
        lbSc = lbScP;
        lbScP = lbTmp;
    }
    
    return lbScP[nSmall];
}


// lbSc and lbScP are buffers and should be of size at least (nSmall+1)
// (nSmall can be bigger than nBig, but it is memory inefficient...)
LIBPLAGIA_API int ilarBGetAlignScore(int *lBig, int nBig, int *lSmall, int nSmall, int *lbSc, int *lbScP)
{
    int i,j;
    int *lbTmp;
    
    if(!lBig || !lSmall || !lbSc || !lbScP)
        return -1;
    
    // This is j==0
    for(i=0; i<nSmall+1; ++i)
        lbScP[i] = (-2)*i;
    
    for(j=1; j<nBig+1; ++j)
    {
        lbSc[0] = (-2)*j;
        for(i=1; i<nSmall+1; ++i)
            lbSc[i] = _max(lbScP[i-1]+simBScoreCouple(lBig[j-1], lSmall[i-1]),
                           lbScP[i]-2,
                           lbSc[i-1]-2);
        lbTmp = lbSc;
        lbSc = lbScP;
        lbScP = lbTmp;
    }
    
    return lbScP[nSmall];
}







