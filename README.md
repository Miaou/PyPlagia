PyPlagia is a plagiarism detection tool for Python 3 codes, written in Python 3 and C.
Its goal is to detect students who tried to avoid their Python assignment by submitting the work of someone else. No less, no more.

Students would put more effort into covering their fault than they would into doing the project by themselves.


# A note to Saphire students

Salut ! En arrivant ici, vous espérez peut-être voir comment est faite la détection du plagiat, et c'est cool ! Je vous souhaite bon courage. Vous verrez, c'est un sujet vaste et très intéressant...


# Overview

The codes of the students are compared to the works of past students, all stored in a database (which is not disclosed because students are copyright holders of their work).
Simple algorithms taken from the literature are used to detect plagiarism. References are given (hoping I am not violating any license by doing so)...

False positives (works detected as very similar but actually done by two different people) are always possible, so the results of the software are always checked again by hand.
The files Stats*.png show that plagiarism detection discriminates correctly the students, even though they all have to implement the same algorithm.

Please feel free to provide your feedback!


# Implementation notes

The tool is provided as a Python package. It takes advantage of the multiprocessing capabilities of Python, and the most computing intensive operations are coded in the C part of the project (so-called libplagia).
Results of the detection are simply stored in a SQLite database.

The package can be launched on Linux or Windows, provided that libplagia is compiled against the same architecture as the Python interpreter of the machine (x64 Python -> x64 compilation of libplagia).
Analysis of the results can be done without compilation of libplagia...


# How to use the tool

1. Compile libplagia with the given makefile
  - cd libplagia
  - make all cleanObj
2. See pyplagia.py, which explains the command line interface as well as the pyplagia API.


# Documentation

None. In fact, no. A lot. Meaningful to me. Maybe not to you. See the code. Contact me if you want more!


# Licensing

This work is provided **as-is**, and licensed under the GPL license. Please read ./LICENSE for more details.
Copyright (C) 2014  Pierre-Antoine BRAMERET

Contact me for more details...