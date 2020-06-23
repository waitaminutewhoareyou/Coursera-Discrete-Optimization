#!/usr/bin/python
# -*- coding: utf-8 -*-
# from mip import *
import random
from csp import *
import gurobipy as gp
from gurobipy import GRB

# def mip_solver(node_count, edge_count, edges):
#     m = Model(solver_name=GRB)
#     M = node_count * 2
#     x = [m.add_var(var_type=INTEGER, lb=0, ub=node_count) for _ in range(node_count)]
#     y = [m.add_var(var_type=BINARY) for _ in range(edge_count)] # decision var for big-M method
#     C = m.add_var(var_type=INTEGER, lb=0, ub=node_count)
#     for ix, (i, j) in enumerate(edges):
#         m += x[j] + 1 - x[i] - M * y[ix] <= 0
#         m += x[i] - x[j] + 1 - M * (1 - y[ix]) <= 0
#     for i in range(node_count):
#         m += x[i] - C <= 0
#     m.objective = minimize(C)
#     status = m.optimize(max_seconds=3000)
#     if status == OptimizationStatus.OPTIMAL:
#         opti = 1
#     else:
#         opti = 0
#     solution = [int(assignment.x) for assignment in x]
#     return solution, opti

def mip_solver(node_count, edge_count, edges):
    m = gp.Model()
    M = node_count*2
    x = m.addVars(node_count, vtype=GRB.INTEGER, lb=0, ub=node_count, name="x")
    y = m.addVars(edge_count, vtype=GRB.BINARY)
    C = m.addVar(vtype=GRB.INTEGER, lb=0, ub=node_count)
    for ix, (i, j) in enumerate(edges):
        m.addConstr(x[j] + 1 - x[i] - M * y[ix] <= 0)
        m.addConstr(x[i] - x[j] + 1 - M * (1 - y[ix]) <= 0)
    for i in range(node_count):
        m.addConstr(x[i] - C <= 0)
    m.setObjective(C, GRB.MINIMIZE)

    timeLimit = 1.5*60*60 #3 hours to check
    m.setParam("TimeLimit", timeLimit)
    m.optimize()
    # provide an inital solution if there is none
    if m.solCount == 0:
        for ix,var in enumerate(x):
            x[var].start = ix
        m.Params.MIPFocus = 1
        timeLimit = 0.5 * 60 * 60  # 4.5 hours to check
        m.setParam("TimeLimit", timeLimit)
        m.optimize()
    opti = 1 if m.status == GRB.OPTIMAL else 0
    solution = [int(v.x) for v in m.getVars()[:node_count]]

    return solution, opti


def solve_semi_magic(num_color, node_count, edge_count, edges,algorithm=backtracking_search, **args):
    """ From CSP class in csp.py
        vars        A list of variables; each is atomic (e.g. int or string).
        domains     A dict of {var:[possible_value, ...]} entries.
        neighbors   A dict of {var:[var,...]} that for each variable lists
                    the other variables that participate in constraints.
        constraints A function f(A, a, B, b) that returns true if neighbors
                    A, B satisfy the constraint when they have values A=a, B=b
                    """

    # Use the variable names in the figure
    def shu(x):
        random.shuffle(x)
        return x

    csp_vars = shu([d for d in range(node_count)])
    #########################################
    # Fill in these definitions

    csp_domains = {var: shu(list(range(num_color))) for var in csp_vars}
    csp_neighbor = {var: [] for var in csp_vars}
    for node_i, node_j in edges:
        csp_neighbor[node_i].append(node_j)
        csp_neighbor[node_j].append(node_i)
    csp_neighbors = {key: shu(val) for key, val in csp_neighbor.items()}

    def csp_constraints(A, a, B, b):
        return a != b

    #########################################

    # define the CSP instance
    csp = CSP(csp_vars, csp_domains, csp_neighbors,
              csp_constraints)

    # run the specified algorithm to get an answer (or None)
    ans = algorithm(csp, **args)

    # print('number of assignments', csp.nassigns)
    assign = csp.infer_assignment()
    # if assign:
    #     for x in sorted(assign.items()):
    #         print(x)
    # for var in csp_vars:
    #     print(ans[var])
    if ans is not None:
        opti = 1
        #solution = [None for _ in range(node_count)]
        #print(sorted(assign.items()))
        solution = [val for var, val in sorted(assign.items())]
        return solution, opti
    return None


def csp_solver(node_count, edge_count, edges):
    num_color, solution_thus_far = 0, None
    while solution_thus_far is None:
        num_color += 1
        solution_thus_far = solve_semi_magic(num_color, node_count, edge_count, edges, algorithm=backtracking_search, select_unassigned_variable=mrv,order_domain_values=lcv, inference=mac)
    return solution_thus_far


def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    first_line = lines[0].split()
    node_count = int(first_line[0])
    edge_count = int(first_line[1])

    edges = []
    for i in range(1, edge_count + 1):
        line = lines[i]
        parts = line.split()
        edges.append((int(parts[0]), int(parts[1])))
    #print(node_count, edge_count, edges)
    # build a trivial solution
    # every node has its own color
    solution, opti = mip_solver(node_count, edge_count, edges)
    #solution, opti = csp_solver(node_count, edge_count, edges)
    # prepare the solution in the specified output format
    output_data = str(len(set(solution))) + ' ' + str(opti) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data

import sys

if __name__ == '__main__':
    import sys
    sys.argv = ['C:/Users/JI YIHONG/Dropbox/Coursera/Discrete Optimization/coloring/solver.py', 'data/gc_4_1']
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/gc__5)')

