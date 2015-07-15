// Sign here.

// This one gathers help functions... It should not use LIBPLAGIA_API.

#include "utils.h"

// Used by ilarA too
int simAScoreCouple(int a, int b)
{
    if(a == b)
        return (a>NAME_OFFSET) ? 2:1;
    return (a>NAME_OFFSET && b>NAME_OFFSET) ? 0:-2;
}

// Used by ilarB too
int simBScoreCouple(int a, int b)
{
    if(a == b)
        return (a>NAME_OFFSET) ? 2:1;
    return 0;
}

int _max(int a, int b, int c)
{
    if(a>b)
        return (a>c) ? a:c;
    return (b>c) ? b:c;
}
int _max(int a, int b, int c, int d)
{
    int x = _max(a,b,c);
    return (x>d) ? x:d;
}
