import time
import heapq

class Vertex():
    def __init__(self, id, children, edges):
        self.id = id
        self.children = children
        self.edges = edges
        self.compute_weighting()

    def __str__(self):
        return str(children)
    def __repr__(self):
        return self.__str__()
    def __hash__(self):
        return self.id

    def compute_weighting(self):
        """
        Computes an internal weighting for the density of the graph under this vertex
        Edges are in the format (weight, vertex)
        """
        max1 = None
        max2 = None
        for edge in self.edges:
            if max1 is None:
                max1 = edge
                continue
            if max2 is None:
                max2 = edge
                continue
            if edge[0] > max1[0]:
                max1 = edge
            elif edge[0] > max2[0]:
                max2 = edge
        if max2 is not None:
            self.internal_weight = max1[0] + max2[0]
        else:
            self.internal_weight = max1[0]

def Level():
    def __init__(self, vertices, translation):
        self.vertices = vertices
        self.translation = translation
    
    def internal_pathfind(self, start, end, parent_path):
        """
        This pathfinds internally within a given level
        This restricts the path searched to be within the parent path's children
        """
        graph = set()
        for vertex in parent_path:
            graph.update(vertex.children)
        queue = [[self.vertices[start]]]
        visited = set()
        dist = {start: 0}
        while queue:
            path = heapq.heappop(queue)
            vertex = path[-1]
            visited.add(vertex)
            curr_dist = dist[vertex]
            if vertex == end:
                print("Found", curr_dist)
                return path
            for edge in vertex.edges:
                connected_vertex = self.vertices[edge[1]]
                # Compute weighting that accoounts for graph density
                edge_weighting = edge[0] + vertex.internal_weight + connected_vertex.internal_weight
                new_dist = curr_dist + edge[0]
                if dist.get(connected_vertex, 1000000) > new_dist:
                    dist[connected_vertex] = new_dist
                    new_path = list(path)
                    new_path.append(connected_vertex)
                    heapq.heappush(queue, new_path)
        print("Not found")
        return None

def group_vertices(level: Level):
    vertices = set(level.vertices.values())
    new_vertices = {}
    translation = {}
    id = 0
    while len(vertices) > 0:
        vertex = vertices.pop()
        

pre_start = time.time()
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
            spl = c.split(".")
            c = int(spl[0])
            weight = int(spl[1])
            c_list += [(weight, c)]
            o_list = l1_cons.get(c, [])
            o_list += [(weight, id)]
            l1_cons[c] = o_list
        l1_cons[id] = c_list

l1_vertices = {}
for key, value in l1_cons.items():
    l1_vertices[key] = Vertex(key, None, edges)
level1 = Level(l1_vertices, {})

levels = [level1]
while True:
    if len(levels) > 1 and len(levels[-1].vertices.keys()) == len(levels[-2].vertices.keys()):
        print("CONVERGED AT", len(levels), "WITH", len(levels[-1].vertices.keys()), "VERTICES")
    levels.append(group_vertices(levels[-1])
    print("iteration", len(levels), "-", len(levels[-1].vertices.keys()))
