import time
import heapq
import dijkstra

class Vertex:
    def __init__(self, id, children, edges):
        self.id = id
        self.children = children
        self.edges = edges
        self.compute_weighting()

    def __str__(self):
        return "<" + str(self.id) + ">"
    def __repr__(self):
        return self.__str__()
    def __hash__(self):
        return self.id
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
        graph = dijkstra.Graph()
        counter = 0
        if parent_path is not None:
            for vertex in parent_path:
                for child in vertex.children:
                    counter += 1
                    for edge in self.vertices[child].edges:
                        graph.add_edge(child, edge[1], edge[0])
        else:
            for vertex in self.vertices.values():
                counter += 1
                for edge in vertex.edges:
                    graph.add_edge(vertex.id, edge[1], edge[0])
        print("Search space:", counter)
        paths = dijkstra.DijkstraSPF(graph, start)
        path = paths.get_path(end)
        print("DIJ Path", path)
        vertex_path = []
        for elem in path:
            vertex_path.append(self.vertices[elem])
        return vertex_path

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

MAX_IN_GROUP = 20

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
    level_maps[i-1] = (start_group, end_group)
    start_group = level.translation[start_group]
    end_group = level.translation[end_group]
    if start_group == end_group:
        lowest_common = i
        break
print(levels[2].vertices[18].children, "-", levels[2].translation[32])
if lowest_common == -1:
    print("Disconnected")
    exit()
path = [levels[lowest_common+1].vertices[start_group]]
for i in range(lowest_common-1, -1, -1):
    print("level", i)
    level = levels[i]
    if i > 0:
        start_group = level_maps[i][0]
        end_group = level_maps[i][1]
    else:
        start_group = START
        end_group = END
    print("start", start_group, "end", end_group)
    level_start = time.time()
    path = level.internal_pathfind(start_group, end_group, path)
    print("Level took", (time.time()-level_start), "seconds")
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
