import heapq
import logging

class Graph:
    def __init__(self, directed=False):
        self.directed = directed
        self.adj_list = dict()

    def __repr__(self):
        graph_str = "Graph Representation:\n"
        for node, neighbors in self.adj_list.items():
            neighbors_str = ', '.join(str(neighbor) for neighbor in neighbors)
            graph_str += f"{node} -> {neighbors_str}\n"
        return graph_str
    
    def __str__(self):
        return self.__repr__()

    def add_node(self, node):
        if node not in self.adj_list:
            self.adj_list[node] = set()
        else:
            raise ValueError("Node is already in Graph")

    def remove_node(self, node):
        if node not in self.adj_list:
            raise ValueError("Node does not exist in Graph")
        else:
            for neighbors in self.adj_list.values():
                neighbors.discard(node)
            del self.adj_list[node]

    def add_edge(self, from_node, to_node, weight=None):
        if to_node not in self.adj_list:
            self.add_node(to_node)

        if from_node not in self.adj_list:
            self.add_node(from_node)

        if weight is None:
            self.adj_list[from_node].add(to_node)
            if not self.directed:
                self.adj_list[to_node].add(from_node)
        else:
            self.adj_list[from_node].add((to_node, weight))
            if not self.directed:
                self.adj_list[to_node].add((from_node, weight))

        
    def remove_edge(self, from_node, to_node):
        if to_node not in self.adj_list:
            raise ValueError(f"{to_node} is not in the Graph")
        
        if from_node not in self.adj_list:
            raise ValueError(f"{from_node} is not in the Graph")

        if from_node in self.adj_list:
            if to_node in self.adj_list[from_node]:
                self.adj_list[from_node].remove(to_node)

            if not self.directed:
                self.adj_list[to_node].remove(from_node)

    def create_artistMap(self, file_path, delimiter=','):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, start=1):
                    try:
                        artist1, artist2 = map(str.strip, line.strip().split(delimiter))
                        if artist1 and artist2:
                            self.add_edge(artist1, artist2)
                        else:
                            logging.warning(f'Line: {line_num} is missing an artist. Skipping...')
                    except ValueError:
                        logging.error(f'Line {line_num} is malformed: {line.strip()}. Skipping...')
        except FileNotFoundError:
            logging.critical(f'File not found: {file_path}. Please check the path for any errors')
        except Exception as e:
            logging.critical(f'Unexpected error: {e}')

    def get_neighbors(self, node):
        return self.adj_list.get(node, set())

    def has_node(self, node):
        return node in self.adj_list

    def has_edge(self, from_node, to_node):
        if from_node in self.adj_list:
            return to_node in self.adj_list[from_node]
        return False

    def get_nodes(self):
        return list(self.adj_list.keys())

    def get_edges(self):
        edges = []
        for from_node, neighbors in self.adj_list.items():
            for to_node in neighbors:
                edges.append(from_node, to_node)
        return edges

    def size_nodes(self):
        return len(self.adj_list.keys())

    def size_edges(self):
        size = 0
        for vertex in self.adj_list.keys():
            size += len(self.adj_list[vertex])
        return size

    def bfs(self, start):
        visited = set()
        queue = [start]
        order = []

        while queue:
            node = queue.pop(0)
            if node not in visited:
                visited.add(node)
                order.append(node)
                neighbors = self.get_neighbors(node)
                for neighbor in neighbors:
                    if isinstance(neighbor, tuple):
                        neighbor = neighbor[0]
                    if neighbor not in visited:
                        queue.append(neighbor)
        
        return order

    def dfs(self, start):
        visited = set()
        stack = [start]
        order = []

        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                order.append(node)
                neighbors = self.get_neighbors(node)
                for neighbor in sorted(neighbors, reverse=True):
                    if isinstance(neighbor, tuple):
                        neighbor = neighbor[0]
                    if neighbor not in visited:
                        stack.append(neighbor)

        return order

    def dijkstra(self, start):
        distances = {node: float('inf') for node in self.adj_list}
        distances[start] = 0
        heap = [(0, start)]
        while heap:
            current_distance, current_node = heapq.heap.pop(heap)
            if current_distance > distances[current_node]:
                continue
            neighbors = self.adj_list.get(current_node, set())
            for neighbor in neighbors:
                if isinstance(neighbor, tuple):
                    to, weight = neighbor
                else:
                    to, weight = neighbor, 1
                distance = current_distance + weight
                if distance < distances[to]:
                    distances[to] = distance
                    heapq.heappush(heap, (distance, to))
        return distances

    
    def shortest_path(self, start, end):
        distances = {node: float('inf') for node in self.adj_list}
        previous = {node: None for node in self.adj_list}
        distances[start] = 0
        heap = [(0, start)]
        while heap:
            current_distance, current_node = heapq.heappop(heap)
            if current_node == end:
                break
            if current_distance > distances[current_node]:
                continue
            neighbors = self.adj_list.get(current_node, set())
            for neighbor in neighbors:
                if isinstance(neighbor, tuple):
                    to, weight = neighbor
                else:
                    to, weight = neighbor, 1
                distance = current_distance + weight
                if distance < distances[to]:
                    distances[to] = distance
                    previous[to] = current_node
                    heapq.heappush(heap, (distance, to))
        path = []
        node = end
        while node is not None:
            path.append(node)
            node = previous.get(node)
        path.reverse()
        if path[0] == start:
            return path
        return []

    def to_adj_matrix(self):
        nodes = self.get_nodes()
        index = {node: i for i, node in enumerate(nodes)}
        size = len(nodes)
        matrix = [[0 for _ in range(size) for _ in range(size)]]
        for from_node, neighbors in self.adj_list.items():
            for to_node in neighbors:
                if isinstance(to_node, tuple):
                    to, weight = to_node
                    matrix[index[from_node]][index[to]] = weight
                else:
                    matrix[index[from_node]][index[to_node]] = 1
        return matrix