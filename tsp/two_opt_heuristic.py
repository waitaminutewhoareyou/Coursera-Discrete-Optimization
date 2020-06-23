import numpy as np
import time


def length(point1, point2):
    return np.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)


def nearesrNeighborHeuristic(nodeCount, points):
    solution = [0]
    unvisited_node = list(range(1, nodeCount)) # from 1 to nodeCount - 1
    while len(unvisited_node) != 0:
        exploring_node = solution[-1] # the current city we are in
        closed_distance = -1
        closed_node = None
        for node in unvisited_node:
            if closed_distance < 0:
                closed_distance = length(points[exploring_node], points[node])
                closed_node = node
            elif length(points[exploring_node], points[node]) < closed_distance:
                closed_distance = length(points[exploring_node], points[node])
                closed_node = node
        next_visit_node = closed_node
        solution.append(next_visit_node)
        unvisited_node.remove(next_visit_node)
    return solution


def objectiveVal(path, points):
    totalDist = 0
    nodeCount = len(path)
    for i in range(nodeCount):
        totalDist += length(points[path[i] % (nodeCount-2)], points[path[i+1] % (nodeCount-2)])
    return totalDist


def two_opt(nodeCount, points, timelimit = None):
    feasible_sol = nearesrNeighborHeuristic(nodeCount, points)
    start_time = time.time()
    def checkCrossArcs(path):
        crossArc = False
        largest_diff = 0
        swap_ix = None
        for pair1 in range(0, len(path)-2):
            for pair2 in range(pair1+1, len(path)-1):
                i, j = path[pair1], path[pair1+1]
                k, l = path[pair2], path[pair2+1]
                d_ij = length(points[i], points[j])
                d_kl = length(points[k], points[l])
                d_ik = length(points[i], points[k])
                d_jl = length(points[j], points[l])
                if d_ij + d_kl > d_ik + d_jl:
                    if (d_ij + d_kl)- (d_ik + d_jl) > largest_diff:
                        largest_diff = (d_ij + d_kl)  - (d_ik + d_jl)
                        swap_ix = pair1, pair1+1, pair2, pair2+1
                        crossArc = True
        return crossArc, swap_ix
    terminal,swap_ix = checkCrossArcs(feasible_sol)
    while terminal:
        i, j, k, l = swap_ix
        improved_sol = feasible_sol[:j] + feasible_sol[j:k+1][::-1] + feasible_sol[k+1:]
        feasible_sol = improved_sol
        terminal, swap_ix = checkCrossArcs(feasible_sol)
        if time.time() - start_time > timelimit:
            return feasible_sol, objectiveVal(feasible_sol, points)
        #print(objectiveVal(feasible_sol, points))
    totalDist = objectiveVal(feasible_sol, points)
    assert len(feasible_sol) == nodeCount, "There are some nodes left unvisited."
    return feasible_sol, totalDist