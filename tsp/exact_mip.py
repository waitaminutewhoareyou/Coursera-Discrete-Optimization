from itertools import combinations
import gurobipy as gp
from gurobipy import GRB
import numpy as np
from two_opt_heuristic import nearesrNeighborHeuristic

def length(point1, point2):
    return np.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)


def mip_tsp(nodeCount, points,timeLimit = None):
    if nodeCount == 1:
        return points, 0
    elif nodeCount == 2:
        return points, 2 * length(points[0], points[1])
    def subtourelim(model, where):
        if where == GRB.Callback.MIPSOL:
            # make a list of edges selected in the solution
            vals = model.cbGetSolution(model._vars)
            selected = gp.tuplelist((i, j) for i, j in model._vars.keys()
                                    if vals[i, j] > 0.5)
            # find the shortest cycle in the selected edge list
            tour = subtour(selected)
            if len(tour) < n:
                # add subtour elimination constr. for every pair of cities in tour
                model.cbLazy(gp.quicksum(model._vars[i, j]
                                         for i, j in combinations(tour, 2))
                             <= len(tour) - 1)

    def subtour(edges):
        unvisited = list(range(n))
        cycle = range(n + 1)  # initial length has 1 more city
        while unvisited:  # true if list is non-empty
            thiscycle = []
            neighbors = unvisited
            while neighbors:
                current = neighbors[0]
                thiscycle.append(current)
                unvisited.remove(current)
                neighbors = [j for i, j in edges.select(current, '*')
                             if j in unvisited]
            if len(cycle) > len(thiscycle):
                cycle = thiscycle
        return cycle
    n = nodeCount
    dist = {(i, j): length(points[i], points[j]) for i in range(n) for j in range(i)}

    # dist = np.zeros((n,n))
    # for i in range(n):
    #     for j in range(i):
    #         dist[i, j] = length(points[i], points[j])
    m = gp.Model()
    vars = m.addVars(dist.keys(), obj=dist, vtype=GRB.BINARY, name='e')
    for i, j in vars.keys():
        vars[j, i] = vars[i, j]  # edge in opposite direction
        m.addConstr(vars[i, j] == vars[j, i])
    m.addConstrs(vars.sum(i, '*') == 2 for i in range(n))


    # randomly generate a trivial solution
    initial_feasible = nearesrNeighborHeuristic(nodeCount,points)
    for var in vars:
        vars[var].start = 0
    for ix in range(len(initial_feasible)-1):
        vars[(initial_feasible[ix], initial_feasible[ix+1])].start = 1
        vars[(initial_feasible[ix + 1], initial_feasible[ix])].start = 1
    vars[(initial_feasible[0], initial_feasible[-1])].start = 1
    vars[(initial_feasible[-1], initial_feasible[0])].start = 1

    m._vars = vars
    # set optimizer parameters,
    m.Params.lazyConstraints = 1
    m.setParam("TimeLimit", timeLimit)
    m.Params.MIPFocus = 1  # focus on good-quality feasible solution
    #m.Params.NodefileStart = 0.5
    m.optimize(subtourelim)
    # If there is no feasible solution available after time limit, multiply time limit by 2 and restart, however,
    # this is unnecessary because we could provide an initial solution
    # while m.solCount == 0:
    #     timeLimit *= 2
    #     m.Params.MIPFocus = 1
    #     m.setParam("TimeLimit", timeLimit)
    #     m.optimize(subtourelim)

    opti = 1 if m.status == GRB.OPTIMAL else 0
    vals = m.getAttr('x', vars)
    selected = gp.tuplelist((i, j) for i, j in vals.keys() if vals[i, j] > 0.5)

    tour = subtour(selected)
    assert len(tour) == n
    solution = tour
    obj = m.objVal

    return solution, obj, opti