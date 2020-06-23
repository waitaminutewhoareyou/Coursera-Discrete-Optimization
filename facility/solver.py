#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
import math
import gurobipy as gp
import numpy as np
from gurobipy import GRB
Point = namedtuple("Point", ['x', 'y'])
Facility = namedtuple("Facility", ['index', 'setup_cost', 'capacity', 'location'])
Customer = namedtuple("Customer", ['index', 'demand', 'location'])

def length(point1, point2):
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)


def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    parts = lines[0].split()
    facility_count = int(parts[0])
    customer_count = int(parts[1])
    
    facilities = []
    for i in range(1, facility_count+1):
        parts = lines[i].split()
        facilities.append(Facility(i-1, float(parts[0]), int(parts[1]), Point(float(parts[2]), float(parts[3])) ))

    customers = []
    for i in range(facility_count+1, facility_count+1+customer_count):
        parts = lines[i].split()
        customers.append(Customer(i-1-facility_count, int(parts[0]), Point(float(parts[1]), float(parts[2]))))

    demand = np.array([customer.demand for customer in customers])
    capacity = np.array([facility.capacity for facility in facilities])
    transCosts = np.array([[length(customer.location, facility.location) for facility in facilities ] for customer in customers])
    fixedCosts = np.array([facility.setup_cost for facility in facilities])
    plants = range(facility_count)
    warehouses = range(customer_count)

    # Model
    m = gp.Model("facility")
    # Plant open decision variables: open[p] == 1 if plant p is open.
    open = m.addVars(plants,
                     vtype=GRB.BINARY,
                     obj=fixedCosts,
                     name="open")

    # Transportation decision variables: transport[w,p] captures the
    # optimal quantity to transport to warehouse w from plant p
    transport = m.addVars(warehouses, plants,
                          vtype=GRB.BINARY,
                          obj=transCosts,
                          name="trans")

    # The objective is to minimize the total fixed and variable costs
    m.modelSense = GRB.MINIMIZE

    # Production constraints
    # Note that the right-hand limit sets the production to zero if the plant
    # is closed
    for p in plants:
        m.addConstr(
            sum(transport[w, p]*demand[w] for w in warehouses) <= capacity[p] * open[p], "Capacity"
        )
    # Demand constraints
    m.addConstrs(
        (transport.sum(w, "*") == 1 for w in warehouses),
        "Assignment")
    # if open[i] == 0, then transport.sum(p,"*")==0
    M = 2*customer_count # bigM
    m.addConstrs(
        (open[p]*M >= transport.sum("*", p) for p in plants),
    "relation")

    # Guess at the starting point: close the plant with the highest fixed costs;
    # open all others

    # First open all plants
    for p in plants:
        open[p].start = 1.0

    # Now close the plant with the highest fixed cost
    maxFixed = max(fixedCosts)
    for p in plants:
        if fixedCosts[p] == maxFixed:
            open[p].start = 0.0
            break
    timeLimit = 45*60
    m.setParam("TimeLimit", timeLimit)
    m.Params.method = 2
    # Solve
    m.optimize()
    solution = [None for _ in range(customer_count)]
    opti = 1 if m.status == GRB.OPTIMAL else 0
    obj = m.objVal
    for p in plants:
        if open[p].x > 0.99:
            for w in warehouses:
                if transport[w, p].x > 0:
                    solution[w] = p


    def trivial_solution():
        # build a trivial solution
        # pack the facilities one by one until all the customers are served
        solution = [-1]*len(customers)
        capacity_remaining = [f.capacity for f in facilities]

        facility_index = 0
        for customer in customers:
            if capacity_remaining[facility_index] >= customer.demand:
                solution[customer.index] = facility_index
                capacity_remaining[facility_index] -= customer.demand
            else:
                facility_index += 1
                assert capacity_remaining[facility_index] >= customer.demand
                solution[customer.index] = facility_index
                capacity_remaining[facility_index] -= customer.demand

        used = [0]*len(facilities)
        for facility_index in solution:
            used[facility_index] = 1

        # calculate the cost of the solution
        obj = sum([f.setup_cost*used[f.index] for f in facilities])
        for customer in customers:
            obj += length(customer.location, facilities[solution[customer.index]].location)
        return solution, obj
    # prepare the solution in the specified output format
    output_data = '%.2f' % obj + ' ' + str(opti) + '\n'
    output_data += ' '.join(map(str, solution))
    # print("capacity is", facilities[413].capacity)
    # demand_ = 0
    # for w in warehouses:
    #     demand_ += demand[w]*transport[w, 413].x
    # print("demand is",demand_)
    # print("capacity is", facilities[412].capacity)
    # demand_ = 0
    # for w in warehouses:
    #     demand_ += demand[w]*transport[w, 412].x
    # print("demand is",demand_)
    return output_data


import sys

if __name__ == '__main__':
    import sys

    sys.argv = ['C:/Users/JI YIHONG/Dropbox/Coursera/Discrete Optimization/facility/solver.py', 'data/fl_1000_2']
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/fl_16_2)')

