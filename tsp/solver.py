#!/usr/bin/python
# -*- coding: utf-8 -*-
import math
from collections import namedtuple
import numpy as np
from exact_mip import *
from two_opt_heuristic import *
Point = namedtuple("Point", ['x', 'y'])

def length(point1, point2):
    return np.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')
    nodeCount = int(lines[0])
    points = []
    for i in range(1, nodeCount+1):
        line = lines[i]
        parts = line.split()
        points.append(Point(float(parts[0]), float(parts[1])))
    method = "optimal" if nodeCount<1000 else "heuristic"
    timelimit = 2*60*60 # two hours to explore
    if method == "optimal":
        solution, obj, opti = mip_tsp(nodeCount, points,timelimit)
        if opti == 0:
            solution, obj = two_opt(nodeCount, points, timelimit/4) # it mip deos not yield exact solution, try heuristic

    if method == "heuristic":
        opti = 0
        solution, obj = two_opt(nodeCount, points, timelimit)

    # prepare the solution in the specified output format
    output_data = '%.2f' % obj + ' ' + str(opti) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data


import sys

if __name__ == '__main__':
    import sys
    sys.argv = ['C:/Users/JI YIHONG/Dropbox/Coursera/Discrete Optimization/tsp/solver.py', 'data/tsp_1889_1']
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/tsp_51_1)')

