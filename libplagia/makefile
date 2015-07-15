# :)
# Changer MODE en debug pour voir les warnings du code
# pyplagia, Pierre-Antoine BRAMERET (C) 2014


CC=g++
MODE=release
USE_ARRAY=
#USE_ARRAY=-std=c++11

ifeq ($(MODE),release)
    MODE_CFLAGS=-O3 -g0 -Wall
    MODE_LDFLAGS=-s
else
    MODE_CFLAGS=-Wall
    MODE_LDFLAGS=
endif
UNAME_S:=$(shell uname -s)
ifeq ($(UNAME_S),Linux)
    CFLAGS=$(MODE_CFLAGS) -DLIBPLAGIA_EXPORTS -DNAME_OFFSET=1024 $(USE_ARRAY) -fPIC
    LDFLAGS=$(MODE_LDFLAGS) -shared
    OLIB=libplagia.so
else
    CFLAGS=$(MODE_CFLAGS) -DLIBPLAGIA_EXPORTS -DNAME_OFFSET=1024 $(USE_ARRAY)
#    LDFLAGS=$(MODE_LDFLAGS) -shared -Wl,--subsystem,windows,--out-implib,./libtestlib.a
    LDFLAGS=$(MODE_LDFLAGS) -shared -Wl,--subsystem,windows
    OLIB=libplagia.dll
endif
#LIB=-leay32 -lpython32


SRC=sim.cc utils.cc ilar.cc
OBJ=$(SRC:%.cc=%.o)


.PHONY: all cleanObj clean
all: $(OBJ) $(OLIB)
cleanObj:
	rm -f $(OBJ)
	rm -f $(OBJT)
clean: cleanObj
	rm -f $(OLIB)
	rm -f $(OLIBT)


$(OLIB): $(OBJ)
	$(CC) $(LDFLAGS) $(OBJ) -o $@
%.o: %.cc
	$(CC) $(CFLAGS) -c $< -o $@

    

