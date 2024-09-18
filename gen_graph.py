#!/bin/python

import random
import time

start_time = time.time()

NUM_NODES = 10000
CONS_PER_NODE = 5

output = open("graph.txt", "w")
output.write(str(NUM_NODES) + "\n")

for i in range(NUM_NODES):
    cons = set()
    for j in range(CONS_PER_NODE):
        cons.add(random.randint(0, i))
    if i in cons:
        cons.remove(i)
    output.write(str(i) + ":")
    for val in cons:
        output.write(str(val) + "." + str(random.randint(0, 10)) + ",")
    output.write("\n")

total_time = time.time() - start_time
print("Generation finished in", total_time, "seconds")
