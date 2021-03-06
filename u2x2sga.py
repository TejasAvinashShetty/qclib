#!/usr/bin/python
#
# qclib - Quantum Computing library for Python
# Copyright (C) 2006   Robert Nowotniak <rnowotniak@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from numpy import *
from qclib import *
from randU2 import randU2, u2
from random import shuffle, choice
import sys

# quantum examples
S = (
        (1.0/sqrt(5) * transpose(matrix([2, 1])), 1.0/sqrt(10) * transpose(matrix([3, 1]))),
        (1.0/sqrt(20) * transpose(matrix([-2, 4])), 1.0/sqrt(40) * transpose(matrix([2, -6]))),
        )
X = matrix([
    [ 2.0 / sqrt(5) , -2.0 / sqrt(20) ],
    [ 1.0 / sqrt(5) , 4.0 / sqrt(20)  ]])
Y = matrix([
    [ 3.0 / sqrt(10) , 2.0 / sqrt(40) ],
    [ 1.0 / sqrt(10) ,-6.0 / sqrt(40) ]])

GOOD = matrix([[s2, s2],
        [s2, -s2]])

def fitness(m):
    t = (m * X - Y)
    return float(abs(0.5 * (t * t.H).trace()))

precision = 9
xmin = -pi
xmax = pi
chromlen = 4 * int(ceil(log((xmax - xmin) * 10**precision + 1)/log(2.0)))
print chromlen
poplen = 40
elitism = 5
Ngen = 50
pc = 0.90
pm = 0.01

def bin2real(s, a = xmin, b = xmax):
    return a + 1.0 * int(s, 2) * (1.0 * (b - a) / (2**len(s) - 1))


def phenotype(s):
    partlen = chromlen / 4
    phi = bin2real(s[:partlen])
    theta = bin2real(s[partlen:2*partlen])
    psi = bin2real(s[2*partlen:3*partlen])
    alpha = bin2real(s[3*partlen:])
    return u2(phi, theta, psi, alpha)

# initial random population
population = []
for i in xrange(poplen):
    chrom = ''.join([str(int(random() > 0.5)) for locus in xrange(chromlen)])
    population.append(chrom)

print 'Initial population:'
for c in population:
    print phenotype(c)

print S

best = None
best_val = None

f = open('log.txt', 'w')

for epoch in xrange(Ngen):

    print 'epoch ' + str(epoch)

    # calculate fitness
    fvalues = []
    for i in xrange(poplen):
        fvalues.append(fitness(phenotype(population[i])))
    # print fvalues, min(fvalues)

    if best == None or min(fvalues) < best_val:
        best_val = min(fvalues)
        best = population[fvalues.index(best_val)]

    f.write('%d %f %f %f %f\n' % (epoch, best_val, min(fvalues), max(fvalues), sum(fvalues) / len(fvalues)))

    if True: # tournament
        newpop = []
        # elitism
        if elitism > 0:
            ranking = fvalues[:]
            ranking.sort()
            for e in xrange(elitism):
                newpop.append(population[fvalues.index(ranking[e])])
        while len(newpop) < poplen:
            i1 = choice(range(len(population)))
            while True:
                i2 = choice(range(len(population)))
                if i1 != i2:
                    break
            while True:
                i3 = choice(range(len(population)))
                if i3 != i2 and i3 != i1:
                    break
            if fvalues[i1] < min(fvalues[i2], fvalues[i3]):
                newpop.append(population[i1])
            elif fvalues[i2] < min(fvalues[i1], fvalues[i3]):
                newpop.append(population[i2])
            else:
                newpop.append(population[i3])
        population = newpop

    if False: # roulette
        sects = [-v for v in fvalues]
        m = min(sects)
        if m < 0:
            sects = [s - m for s in sects]
        sects /= sum(sects)

        # accumulated
        for i in xrange(1, poplen):
            sects[i] = sects[i - 1] + sects[i]

        #print population
        #print sects
        newpop = []
        for i in xrange(poplen):
            r = random()
            for j in xrange(len(sects)):
                if r <= sects[j]:
                    newpop.append(population[j])
                    break

        population = newpop
        print population

    toCrossover = []
    for n in xrange(poplen):
        if random() <= pc:
            toCrossover.append(n)
    if len(toCrossover) % 2 != 0:
        n = int(floor(random() * poplen))
        while toCrossover.count(n) > 0:
            n = int(floor(random() * poplen))
        toCrossover.append(n)

    done = []
    for n in xrange(len(toCrossover)):
        par1 = toCrossover[n]
        if done.count(par1) > 0:
            continue

        while True:
            par2 = choice(toCrossover)
            if done.count(par2) == 0:
                break

        cp = int(floor(random() * (chromlen - 1)))
        # print par1, par2, cp, len(population)
        # print population[par1]
        # print population[par2]
        child1 = population[par1][:cp] + population[par2][cp:]
        child2 = population[par2][:cp] + population[par1][cp:]
        population[par1] = child1
        population[par2] = child2
        done.append(par1)
        done.append(par2)

    # mutation
    for n in xrange(poplen):
        for locus in xrange(chromlen):
            if random() <= pm:
                chrom = list(population[n])
                if chrom[locus] == '1':
                    chrom[locus] = '0'
                else:
                    chrom[locus] = '1'
                population[n] = ''.join(chrom)


print best_val
print phenotype(best)
print GOOD

f.close()

