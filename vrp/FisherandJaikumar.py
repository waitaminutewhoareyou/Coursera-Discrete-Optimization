import numpy as np
import gurobipy as gp
from gurobipy import GRB
from itertools import combinations
from two_opt_heuristic import nearesrNeighborHeuristic

class FisherJaikumar(object):
    def __init__(self, depot, customers, vehicle_capacity, vehicle_count):
        self.customers = customers
        self.depot = depot
        self.customers.remove(depot)
        self.vehicle_capacity = vehicle_capacity
        self.numClusters = vehicle_count
        self.seedVertices = np.random.choice(len(self.customers), size=self.numClusters)

    def length(self,customer1, customer2):
        return np.sqrt((customer1.x - customer2.x)**2 + (customer1.y - customer2.y)**2)

    def pathDistance(self, path):
        """Given a list of customer ix, return the cycle distance"""
        res = 0
        res += self.length(self.depot, self.customers[path[0]])
        for ix in range(len(path)-1):
            res += self.length(self.customers[path[ix]], self.customers[path[ix]+1])
        res += self.length(self.depot, self.customers[path[-1]])
        return res

    def populationCost(self):
        cost = np.zeros((len(self.customers), self.numClusters))
        for i in range(len(self.customers)):
            for j in range(self.numClusters):
                jk = self.seedVertices[j]
                cost[i, j] = self.length(self.depot, self.customers[i]) + self.length(self.customers[i], self.customers[jk]) - self.length(self.depot, self.customers[jk])
        return cost

    def GAP(self):
        cities = range(len(self.customers))
        cluster = range(self.numClusters)
        cosMat = self.populationCost()
        m = gp.Model()

        assign = m.addVars(cities, cluster,
                           vtype=GRB.BINARY,
                           obj=cosMat)

        m.modelSense = GRB.MINIMIZE
        m.Params.OutputFlag = 0
        m.addConstrs(
            (assign.sum(i, "*")==1 for i in cities)
        )
        for k in cluster:
            m.addConstr(
                sum(self.customers[i].demand * assign[i, k] for i in cities) <= self.vehicle_capacity
            )
        timelimit = None
        m.optimize()
        assignmentRes = np.zeros((len(self.customers), self.numClusters))
        for i in range(len(self.customers)):
            for j in range(self.numClusters):
                assignmentRes[i, j] = 1 if assign[i, j].x > 0.99 else 0
        return assignmentRes

    def mip_tsp(self, nodeCount, points, timeLimit = None):
        if nodeCount == 1:
            return points, 0
        elif nodeCount == 2:
            return points, 2*self.length(points[0], points[1])

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
        dist = {(i, j): self.length(points[i], points[j]) for i in range(n) for j in range(i)}

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
        initial_feasible = nearesrNeighborHeuristic(nodeCount, points)
        for var in vars:
            vars[var].start = 0
        for ix in range(len(initial_feasible) - 1):
            vars[(initial_feasible[ix], initial_feasible[ix + 1])].start = 1
            vars[(initial_feasible[ix + 1], initial_feasible[ix])].start = 1
        vars[(initial_feasible[0], initial_feasible[-1])].start = 1
        vars[(initial_feasible[-1], initial_feasible[0])].start = 1

        m._vars = vars
        # set optimizer parameters,
        m.Params.lazyConstraints = 1
        m.Params.OutputFlag = 0
        #m.setParam("TimeLimit", timeLimit)
        m.Params.MIPFocus = 1  # focus on good-quality feasible solution
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
        assert len(tour) == n, "Not all cities are visited"
        #solution = tour
        solution = [points[ix] for ix in tour]
        obj = m.objVal

        return solution, obj

    def refomulateSolution(self, cycle):
        assert self.depot in cycle, "The starting cit is missing!"
        for ix in range(len(cycle)):
            if cycle[ix] == self.depot:
                return cycle[ix+1:] + cycle[:ix]

    def solve(self):
        objTotal = 0
        solutionTotal = []
        assignmentRes = self.GAP()
        assert np.all(np.sum(assignmentRes,axis=1)), "Some customers are missed"

        for clusterID in range(self.numClusters):
            ClusterIx = assignmentRes[:, clusterID]
            customers = [self.customers[i] for i in range(len(self.customers)) if ClusterIx[i] == 1]
            customers.append(self.depot) # remember to add origin
            nodeCount = len(customers)
            solution, obj = self.mip_tsp(nodeCount, customers)
            solutionTotal.append(self.refomulateSolution(solution))
            #print("solution is", solution)
            objTotal += obj

        return solutionTotal, objTotal