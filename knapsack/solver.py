#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np
from collections import namedtuple
Item = namedtuple("Item", ['index', 'value', 'weight'])

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1]) #11

    items = []

    for i in range(1, item_count+1):
        line = lines[i]
        parts = line.split()
        items.append(Item(i, int(parts[0]), int(parts[1]))) #original:items.append(Item(i-1, int(parts[0]), int(parts[1])))

    # a trivial algorithm for filling the knapsack
    # it takes items in-order until the knapsack is full
    value = 0
    taken = [0]*len(items)
    #print("item is",items,",\n capacity is", capacity)
    # items = [Item(index=0, value=8, weight=4), Item(index=1, value=10, weight=5), Item(index=2, value=15, weight=8), Item(index=3, value=4, weight=3)]
    # dp = np.zeros((item_count+1, capacity+1), dtype=int)
    # for item in items:
    #     for j in range(capacity+1):
    #         if item.weight > j:
    #             dp[item.index, j] = dp[item.index-1, j]
    #         else:
    #             dp[item.index, j] = max(dp[item.index-1, j], item.value + dp[item.index-1, j-item.weight])
    # print(dp)
    # value = dp[-1, capacity]
    # i, j = item_count, capacity
    # while (i > 0) and (j > 0):
    #     if (items[i-1].weight <= j) and (dp[i-1, j] < items[i-1].value + dp[i-1, j - items[i-1].weight]):
    #         taken[i-1] = 1
    #         j -= items[i-1].weight
    #     i -= 1
    # con = 0
    # for i in range(item_count):
    #     if taken[i]==1:
    #        con += items[i].weight

    #dic_cur = {key: [] for key in range(capacity + 1)}
    decision_cur = [ [] for key in range(capacity + 1)]
    dp_cur = [0 for _ in range(capacity+1)]
    for item in items:
        dp_old = dp_cur[:]
        decision_old = decision_cur[:]
        for j in range(capacity+1):
            if item.weight > j:
                decision_cur[j] = decision_old[j] + [0]
                dp_cur[j] = dp_old[j]
            else:
                val_dont_pick = dp_old[j]
                val_pick = item.value + dp_old[j-item.weight]
                if val_dont_pick < val_pick:
                    decision_cur[j] = decision_old[j-item.weight] + [1]
                else:
                    decision_cur[j] = decision_old[j] + [0]
                dp_cur[j] = max(val_dont_pick, val_pick)
    value = dp_cur[-1]
    i, j = item_count, capacity
#    print(dp_old,dp_cur)
#    print(dic_cur[capacity]) #[0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0]
    taken = decision_cur[capacity]



    
    # prepare the solution in the specified output format
    output_data = str(value) + ' ' + str(1) + '\n'
    output_data += ' '.join(map(str, taken))
    return output_data


if __name__ == '__main__':
    import sys
    sys.argv = ['C:/Users/JI YIHONG/Dropbox/Coursera/Discrete Optimization/knapsack/solver.py', 'data/ks_19_0']
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)')

