# Cryptographic Crosswords Solver

The program solves the cryptogram problem.

The same letter corresponds to the same number (substitution cipher).

Input is read as :

n //number of columns

m // number of rows

//grid of sybols, _ if empty

1,2,3_

_1,2,3

//hints

1,a

2,b

3,c

For reference see *input.txt* or *test-input.txt*.

It is also necessary to specify the dictionary file.

To solve a cryptogram, create a Solver instance specifying a dictionary and a file for problem definition.

Look at lw_test for inspiration on the usage,

After creating the solver, run its *solve()* method.