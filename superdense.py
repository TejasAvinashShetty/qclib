#!/usr/bin/python

from qclib import *

qregiter = epr()

b1 = 1
b2 = 0

# Perform coding operations on Alice qubit
if b1:
    print (PhaseShift(pi) ** I)
    qregiter = (PhaseShift(pi) ** I)(qregiter)

if b2:
    qregiter = (Not() ** I)(qregiter)

B = Arbitrary([
    [s2,   0,  0,  s2],
    [ 0,  s2, s2,   0],
    [s2,   0,  0, -s2],
    [ 0, -s2, s2 ,  0],
    ])

print B(qregiter).dirac()



