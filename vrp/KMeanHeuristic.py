import numpy as np
import copy
np.random.seed(0)
class ClusterThenTSP(object):
    def __init__(self, depot, customers, vehicle_capacity, vehicle_count):
        self.customers = customers
        self.customers.remove(depot)
        self.vehicle_capacity = vehicle_capacity
        self.vehicle_count = vehicle_count
        self.clusterMatrix = np.zeros((vehicle_count, len(customers)))
        self.centroids = self.initialzeCluster()

    def demandOfPath(self, path):
        return sum([self.customers[int(customer_ix)].demand for customer_ix,assignment in enumerate(path) if assignment==1])

    def distance(self, pair):
        i, j = pair
        centroid = self.centroids[i]
        cityLocation = self.customers[j].x, self.customers[j].y
        return np.sqrt((centroid[0]-cityLocation[0])**2 + (centroid[1]-cityLocation[1])**2)

    def computeCentroid(self, cluster_Ass):
        """Given assignment matirx, update self.centroids"""
        updateCentroid = []
        for clusterAssignment in cluster_Ass:
            xBar = np.mean([self.customers[ix].x for ix in range(len(self.customers)) if clusterAssignment[ix]==1])
            yBar = np.mean([self.customers[ix].y for ix in range(len(self.customers)) if clusterAssignment[ix]== 1])
            updateCentroid.append([xBar, yBar])
        return updateCentroid

    def initialzeCluster(self):
        initialCentroids = []
        xrange = [customer.x for customer in self.customers]
        yrange = [customer.y for customer in self.customers]
        xmin, xmax = min(xrange), max(xrange)
        ymin, ymax = min(yrange), max(yrange)
        for _ in range(self.vehicle_count):
            x = np.random.randint(int(xmin), int(xmax))
            y = np.random.randint(int(ymin), int(ymax))
            initialCentroids.append([x, y])
        return initialCentroids
    def objectve(self,centroids,clusterMatrix):
        res = 0
        for clusterID,centroid in enumerate(centroids):
            cluster = self.clusterMatrix[clusterID]
            for customerIx,assignment in enumerate(cluster):
                if assignment:
                    res += self.distance([clusterID, customerIx])**2
        return res

    def KmeanCluster(self):
        obj = np.inf
        while True: # if no more update then the cluster is done:
            curClusterMatrix = self.clusterMatrix.copy()
            oldObj = obj
            clusterToCityPair = sorted([[i, j] for i in range(self.vehicle_count) for j in range(len(self.customers))],
                                       key=self.distance)
            # distMat = {}
            # for i in range(self.vehicle_count):
            #     for j in range(len(self.customers)):
            #         centroid = self.centroids[i]
            #         cityLocation = self.customers[j].x, self.customers[j].y
            #         distMat[(i, j)] = self.distance([i,j])

            customerAssign = []
            for clusterID, customerIx in clusterToCityPair:
                customer = self.customers[customerIx]
                cluster = self.clusterMatrix[clusterID, :]
                if self.demandOfPath(cluster) + customer.demand < self.vehicle_capacity and (customer not in customerAssign):
                    for ix, assignment in enumerate(curClusterMatrix[:, customerIx]):
                        if assignment:
                            preClusterID = ix
                            self.clusterMatrix[preClusterID, customerIx] = 0
                    self.clusterMatrix[clusterID, customerIx] = 1

                    customerAssign.append(customer)
                if len(customerAssign) == len(self.customers):
                    break
            #print(self.clusterMatrix)
            self.centroids = self.computeCentroid(self.clusterMatrix) # return update centroid
            obj = self.objectve(self.centroids, self.clusterMatrix)
            print(self.centroids)
            if abs(obj-oldObj)<1e-4:
                break
        return self.clusterMatrix

