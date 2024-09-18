import time
import heapq

class Vertex:
    def __init__(self, id, children, edges):
        self.id = id
        self.children = children
        self.edges = edges
        self.compute_weighting()

    def __str__(self):
        return str(self.id) + " - " + str(self.children)
    def __repr__(self):
        return self.__str__()
    def __hash__(self):
        return self.id
    def depth(self):
        children_list = list(self.children)
        if len(self.children) > 0 and isinstance(children_list[0], Vertex):
            return children_list[0].depth + 1
        else:
            return 1
    def compute_weighting(self):
        """
        Computes an internal weighting for the density of the graph under this vertex
        Edges are in the format (weight, vertex, subvertex)
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

class Level:
    def __init__(self, vertices, translation):
        self.vertices = vertices
        self.translation = translation
    
    def internal_pathfind(self, start, end, parent_path):
        """
        This pathfinds internally within a given level
        This restricts the path searched to be within the parent path's children
        """
        graph = set()
        if parent_path is not None:
            for vertex in parent_path:
                graph.update(vertex.children)
        else:
            graph.update(self.vertices.values())
        counter = 1
        queue = [(0,0,[self.vertices[start]])]
        dist = {start: 0}
        while queue:
            path = heapq.heappop(queue)[2]
            vertex = path[-1]
            curr_dist = dist[vertex.id]
            if vertex.id == end:
                print("Found", curr_dist)
                return path
            for edge in vertex.edges:
                connected_vertex = self.vertices[edge[1]]
                # Compute weighting that accoounts for graph density
                edge_weighting = edge[0] + vertex.internal_weight + connected_vertex.internal_weight
                new_dist = curr_dist + edge[0]
                if dist.get(connected_vertex.id, 1000000) > new_dist:
                    dist[connected_vertex.id] = new_dist
                    new_path = list(path)
                    new_path.append(connected_vertex)
                    heapq.heappush(queue, (new_dist, counter, new_path))
                    counter += 1
        print("Not found")
        return None

def group_vertices(level: Level, max_in_group):
    vertices = set(level.vertices.values())
    new_vertices = {}
    translation = {}
    id = 0
    groups = {}
    while len(vertices) > 0:
        vertex = vertices.pop()
        children = {vertex.id: vertex}
        translation[vertex.id] = id
        for edge in vertex.edges:
            if len(children.keys()) >= max_in_group:
                break
            if level.vertices[edge[1]] in vertices:
                children[edge[1]] = level.vertices[edge[1]]
                vertices.remove(level.vertices[edge[1]])
                translation[edge[1]] = id
        groups[id] = children
        id += 1
    for gid,children in groups.items():
        edges = {}
        for child in children.values():
            for edge in child.edges:
                new_end = translation[edge[1]]
                if edges.get(new_end, (1000000,None,None))[0] > edge[0]:
                    edges[new_end] = (edge[0],new_end,child.id)
        edges_set = set()
        for edge in edges.values():
            edges_set.add(edge)
        vert = Vertex(gid, children, edges_set)
        new_vertices[gid] = vert
    return Level(new_vertices, translation)

MAX_IN_GROUP = 50

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
            c_list += [(weight, c, 0)]
            o_list = l1_cons.get(c, [])
            o_list += [(weight, id, 0)]
            l1_cons[c] = o_list
        l1_cons[id] = c_list

l1_vertices = {}
for key, value in l1_cons.items():
    l1_vertices[key] = Vertex(key, None, value)
level1 = Level(l1_vertices, {})
levels = [level1]
while True:
    if len(levels) > 1 and len(levels[-1].vertices.keys()) == len(levels[-2].vertices.keys()):
        print("CONVERGED AT", len(levels), "WITH", len(levels[-1].vertices.keys()), "VERTICES")
        break
    levels.append(group_vertices(levels[-1], MAX_IN_GROUP))
    print("iteration", len(levels), "-", len(levels[-1].vertices.keys()))
pre_end = time.time()
print("Converged in", (pre_end-pre_start), "seconds")

START = 100
END = 10001
start = time.time()

lowest_common = -1

start_group = START
end_group = END
level_maps = {}
for i in range(1, len(levels)):
    level = levels[i]
    level_maps[i] = (start_group, end_group)
    start_group = level.translation[start_group]
    end_group = level.translation[end_group]
    if start_group == end_group:
        lowest_common = i
        break
if lowest_common == -1:
    print("Disconnected")
    exit()
path = [levels[lowest_common+1].vertices[start_group]]
for i in range(lowest_common, -1, -1):
    print("level", i)
    level = levels[i]
    if i > 0:
        start_group = level_maps[i][0]
        end_group = level_maps[i][1]
    else:
        start_group = START
        end_group = END
    path = level.internal_pathfind(start_group, end_group, path)
    print("Path length:", len(path), "/", len(levels[i].vertices))

end = time.time()
print("Search took", (end-start), "seconds")
print("Path:", path)

start = time.time()
path = level.internal_pathfind(START, END, None)
end = time.time()
print("Djikstra took", (end-start), "seconds")
print("Djikstra path", path)
print("Path length", len(path))
