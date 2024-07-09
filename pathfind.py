#!/bin/python
import time

pre_start = time.time()

class Group:
    def __init__(self, id, nodes, connections):
        self.id = id
        self.nodes = nodes
        self.connections = connections

    def __str__(self):
        return "Group: " + str(self.id) + " - (" + str(self.nodes) + ")"
    def __repr__(self):
        return self.__str__()

class Node:
    def __init__(self, id, connections):
        self.id = id
        self.connections = connections

    def __str__(self):
        return "Node: " + str(self.id)
    def __repr__(self):
        return "Node: " + str(self.id)

class Level:
    def __init__(self, groups, translation):
        self.groups = groups
        self.translation = translation

input = open("graph.txt", "r")
lines = input.readlines()
first = True
l1_cons = {}
for line in lines:
    line = line.replace("\n", "")
    if first:
        first = False
    else:
        split = line.split(":")
        id = int(split[0])
        cons = split[1].split(",")
        c_list = l1_cons.get(id, [])
        for c in cons:
            if c == "":
                continue
            c = int(c)
            c_list += [c]
            o_list = l1_cons.get(c, [])
            o_list += [id]
            l1_cons[c] = o_list
        l1_cons[id] = c_list

l1_nodes = {}
for key, value in l1_cons.items():
    l1_nodes[key] = Node(key, value)

def level_pathfind(start, end, path, levels, levelnum):
    newpath = [start]
    uplevel = levels[levelnum+1]
    downlevel = levels[levelnum]
    for i in range(1, len(path)):
        last_newpath = newpath[-1]
        prevgroup = uplevel.groups[uplevel.translation[last_newpath.id]]
        group = path[i]
        found = False
        if isinstance(group, Group):
            for node in group.nodes:
                if node.id in last_newpath.connections:
                    newpath += [node]
                    found = True
                    break
        else:
            newpath += [group]
        if found:
            continue
        for node in prevgroup.nodes:
            if node != last_newpath:
                newpath += [node]
                last_newpath = node
                break
        # Now do it again
        if isinstance(group, Group):
            for node in group.nodes:
                if node.id in last_newpath.connections and node not in newpath:
                    newpath += [node]
                    found = True
                    break
        else:
            newpath += [group]
        if not found:
            print("Graph not connected!")
    if newpath[-1].id != end.id:
        newpath += [end] # Always will end up in same group as end node
    return newpath

def group_nodes(nodes):
    picked = {}
    id = 0
    tmp_groups = {}
    translation = {}
    for node in nodes.values():
        if picked.get(node.id, False):
            continue
        picked[node.id] = True
        translation[node.id] = id
        group = [node]
        neighbour = None
        for n2 in node.connections:
            if picked.get(n2, False):
                continue
            neighbour = n2
            picked[neighbour] = True
            translation[neighbour] = id
            break
        if neighbour is not None:
            group += [nodes[neighbour]]
        tmp_groups[id] = group
        id += 1
    groups = {}
    for id, nodes in tmp_groups.items():
        cons = set()
        for node in nodes:
            for con in node.connections:
                cons.add(translation[con])
        group = Group(id, nodes, cons)
        groups[id] = group
    return Level(groups, translation)

translation = {}
for key in l1_nodes.keys():
    translation[key] = key

levels = [Level(l1_nodes, translation)]
i = 0
while True:
    new_level = group_nodes(levels[i].groups)
    levels += [new_level]
    print(str(len(levels[i].groups)) + " -> " + str(len(levels[i+1].groups)))
    if len(levels[i].groups) == len(levels[i+1].groups):
        break
    i += 1

pre_time = time.time() - pre_start

print("Converged in", i, "iterations")
print("Preprocessor took", pre_time, "seconds")

run_start = time.time()

START = 100
END = 370

start_groups = {}
end_groups = {}
first_common = -1
for i in range(len(levels)):
    level = levels[i]
    if i == 0:
        start_groups[i] = START
        end_groups[i] = END
    else:
        start_groups[i] = level.translation[start_groups[i-1]]
        end_groups[i] = level.translation[end_groups[i-1]]
    if start_groups[i] == end_groups[i]:
        first_common = i
        break
print(start_groups)
print(end_groups)
# level_pathfind(start, end, path, levels, levelnum):
path = []
for levelnum in range(first_common-1, -1, -1):
    level = levels[levelnum]
    start = level.groups[start_groups[levelnum]]
    end = level.groups[end_groups[levelnum]]
    if levelnum == first_common-1:
        path = [start, end]
        continue
    path = level_pathfind(start, end, path, levels, levelnum)

run_time = time.time() - run_start
print("Final path", path)
print("Path length", len(path))
print("Found path in", run_time, "seconds")
