import numpy as np


def length(customer1, customer2):
    return np.sqrt((customer1.x - customer2.x)**2 + (customer1.y - customer2.y)**2)


def ClarkWright(depot, customers, vehicle_capacity, vehicle_count):

    customers.remove(depot)
    def saving(pair):
        i, j = pair
        c_oi = length(depot, customers[i])
        c_oj = length(depot, customers[j])
        c_ij = length(customers[i], customers[j])
        return c_oi + c_oj - c_ij

    def checkCapacity(route):
        return sum([customer.demand for customer in route]) <= vehicle_capacity
    vehicle_tours = [[customers[i]] for i in range(len(customers))]
    #vehicle_tours = [[customers[i]] for i in range(vehicle_count)] # make n routes
   # visited_cities = [customers[i] for i in range(vehicle_count)]
    savingList = [[i, j] for i in range(len(customers)-1) for j in range(i+1, len(customers))]
    savingList = np.array(sorted(savingList, key=saving, reverse=True))
    for saving in savingList:

        i, j = saving
        interior = 0
        for vehicle_tour in vehicle_tours:
            if (i == vehicle_tour[0].index) or (i == vehicle_tour[-1].index):
                route1 = vehicle_tour
                interior += 1
            if (j == vehicle_tour[0].index) or (j == vehicle_tour[-1].index):
                route2 = vehicle_tour
                interior += 1


        if interior == 2:
            if route1 != route2 and checkCapacity(route1+route2):
                vehicle_tours.remove(route1)
                vehicle_tours.remove(route2)
                vehicle_tours.append(route1+route2)
    #print(np.array(vehicle_tours))
    obj = 0
    for v in range(0, vehicle_count):
        try:
            vehicle_tour = vehicle_tours[v]
        except IndexError:
            vehicle_tour = []
            vehicle_tours.append(vehicle_tour)
        if len(vehicle_tour) > 0:
            obj += length(depot, vehicle_tour[0])
            for i in range(0, len(vehicle_tour) - 1):
                obj += length(vehicle_tour[i], vehicle_tour[i + 1])
            obj += length(vehicle_tour[-1], depot)

    return vehicle_tours, obj
