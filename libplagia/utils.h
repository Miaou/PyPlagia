// Sign here.


#ifndef LIBPLAGIA_UTILS_H
#define LIBPLAGIA_UTILS_H


//#include <algorithm>
//#include <array>
//using namespace std;


#ifdef _WIN32
#ifdef LIBPLAGIA_EXPORTS
#define LIBPLAGIA_API extern "C" __declspec(dllexport)
#else
#define LIBPLAGIA_API extern "C" __declspec(dllimport)
#endif
#else // _WIN32
#define LIBPLAGIA_API extern "C"
#endif


// Used by ilarA too
int simAScoreCouple(int a, int b);
// Used by ilarB too
int simBScoreCouple(int a, int b);

int _max(int a, int b, int c);
int _max(int a, int b, int c, int d);



#endif //! LIBPLAGIA_UTILS_H
