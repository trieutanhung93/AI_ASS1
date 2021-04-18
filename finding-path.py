from __future__ import annotations
from typing import Protocol, Dict, List, Iterator, Tuple, TypeVar, Optional
from termcolor import colored
import random

"""Định nghĩa các kiểu dữ liệu cho bài toán"""
# Tạo ra biến kiểu có tên là Location - đại diện cho một vị trí trong graph.
Location = TypeVar('Location')
# Tạo ra biến kiểu có tên là T - có thể là một kiểu dữ liệu bất kì.
T = TypeVar('T')
# Tạo ra biến kiểu có tên là GridLocation - là một tuple với 2 phần tử kiểu int
GridLocation = Tuple[int,int]

# Định nghĩa class Graph - kiểu dữ liệu sẽ là đầu vào cho thuật toán tìm đường A*.
class Graph():
    # Phương thức neighbors giúp trả về danh sách các lân cận của một vị trí bất kì trên graph.
    def neighbors(self, id: Location) -> List[Location]: pass

# Định nghĩa class WeightedGraph - kiểu dữ liệu sẽ là đầu vào cho thuật toán tìm đường A* trong trường
# hợp các đường đi có chi phí khác nhau.
class WeightedGraph(Graph):
    def cost(self, from_id: Location, to_id: Location) -> float: pass

# Định nghĩa class SquareGrid - kiểu dữ liệu mà chúng ta sẽ sử dụng để mô tả bài toán.
class SquareGrid:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.walls: List[GridLocation] = []

    # Kiểm tra một điểm có vượt quá giới hạn của mạng lưới hay không.
    def in_bound(self, id: GridLocation) -> bool:
        (x,y) = id
        return 0 <= x <= self.width and 0 <= y <= self.height

    # Kiểm tra có thể đi qua một điểm hay không ( điểm đó có phải là tường hay không ).
    def passable(self, id: GridLocation) -> bool:
        return id not in self.walls

    # Trả về danh sách các lân cận của một điểm trong mạng lưới.
    def neighbors(self, id: GridLocation) -> Iterator[GridLocation]:
        (x,y) = id
        neighbors = [(x+1, y), (x-1, y), (x, y-1), (x, y+1)]
        if (x+y) % 2 == 0:
            neighbors.reverse()
        results = filter(self.in_bound, neighbors)
        results = filter(self.passable, neighbors)
        return results

# Định nghĩa class GridWithWeights - kiểu dữ liệu mà chúng ta sẽ sử dụng để mô tả bài toán
# trong trường hợp chi phí các bước di chuyển là khác nhau.
class GridWithWeights(SquareGrid):
    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        self.weights: Dict[GridLocation, float] = {}

    # Hàm trả về chi phí để di chuyển đến một vị trí bất kì trong mạng lưới
    # với giá trị chi phí mặc định là 1.
    def cost(self, from_node: GridLocation, to_node: GridLocation) -> float:
        return self.weights.get(to_node, 1)

# Định nghĩa class GridWithAdjustedWeights - kiểu dữ liệu mà chúng ta sẽ sử dụng để mô tả bài toán
# trong trường hợp chi phí các bước di chuyển là khác nhau. Tuy nhiên kiểu dữ liệu này giúp xây dựng
# đường đi "đẹp" hơn.
class GridWithAdjustedWeights(GridWithWeights):
    def cost(self, from_node, to_node):
        prev_cost = super().cost(from_node, to_node)
        nudge = 0
        (x1, y1) = from_node
        (x2, y2) = to_node
        # Tăng chi phí cho di chuyển dọc tại vị trí có tọa độ chẵn ( x,y đều chẵn )
        # và tăng chi phí cho di chuyển ngang tại vị trí có tọa độ lẻ ( x,y đều lẻ ).
        if (x1 + y1) % 2 == 0 and x2 != x1: nudge = 1
        if (x1 + y1) % 2 == 1 and y2 != y1: nudge = 1
        return prev_cost + 0.001 * nudge


import heapq
# Định nghĩa class PriorityQueue với những phương thức hỗ trợ cho bài toán tìm đường.
class PriorityQueue:
    def __init__(self):
        self.elements: List[Tuple[float, T]] = []

    def empty(self) -> bool:
        return not self.elements

    def put(self, item: T, priority: float):
        heapq.heappush(self.elements, (priority, item))

    def get(self) -> T:
        return heapq.heappop(self.elements)[1]

# Hàm hỗ trợ xây dựng những bức tường trong bài toán tìm đường.
# Với đầu vào là 2 số nguyên dương id và width, hàm trả về tọa
# độ của một điểm sẽ tạo nên bức tường.
def from_id_width(id, width):
    return (id % width, id // width)


# Hàm xử lí một điểm trong quá trình vẽ mạng lưới
def draw_point(graph, id, style):
    r = " . "
    if 'number' in style and id in style['number']: r = " %-2d" % style['number'][id]
    if 'point_to' in style and style['point_to'].get(id, None) is not None:
        (x1, y1) = id
        (x2, y2) = style['point_to'][id]
        if x2 == x1 + 1: r = " > "
        if x2 == x1 - 1: r = " < "
        if y2 == y1 + 1: r = " v "
        if y2 == y1 - 1: r = " ^ "
    if 'path' in style and id in style['path']:   r = " @ "
    if 'start' in style and id == style['start']: r = " A "
    if 'goal' in style and id == style['goal']:   r = " Z "
    if id in graph.walls: r = "###"
    return r

# Hàm giúp vẽ mạng lưới với đầu vào là một graph.
def draw_grid(graph, **style):
    path = []
    graph_matrix = [[0 for x in range(0,graph.width)] for x in range(graph.height)]
    print("___" * graph.width)
    for y in range(graph.height):
        for x in range(graph.width):
            tmp = draw_point(graph, (x, y), style)
            if tmp == ' @ ':
                print(colored(tmp, 'green', 'on_blue', attrs=['reverse', 'blink']), end="")
            elif tmp == '###':
                print(colored(tmp, 'white', 'on_red'), end="")
            else:
                print(tmp, end="") 
        print()
    print("~~~" * graph.width)

# Hàm xây dựng lại đường đi.
def reconstruct_path(came_from: Dict[Location, Location],start: Location, goal: Location) -> List[Location]:
    current: Location = goal
    path: List[Location] = []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start) # optional
    path.reverse() # optional
    return path


def heuristic(a: GridLocation, b: GridLocation) -> float:
    (x1,y1) = a
    (x2,y2) = b
    return abs(x1-x2) + abs(y1-y2)


def a_star_search(graph: WeightedGraph, start: GridLocation, goal: GridLocation):
    frontier = PriorityQueue()
    frontier.put(start,0)
    came_from: Dict[Location, Optional[Location]] = {}
    cost_so_far: Dict[Location, float] = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current = frontier.get()
        if current == goal:
            break
        for next in graph.neighbors(current):
            new_cost = cost_so_far[current] + graph.cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(next,goal)
                frontier.put(next, priority)
                came_from[next] = current
    return came_from, cost_so_far

# Hàm sinh ngẫu nhiên hai điểm bắt đầu và mục tiêu.
'''
def generate_grid_and_walls():
    random.seed(None, 2)
    state = random.getstate()
    random.setstate(state)
    diagram = GridWithAdjustedWeights(random.randrange(0, 20), random.randrange(0, 20))
    point_count = diagram.height * diagram.width
    walls_point = (random.randrange(0, point_count))
    for i in range(0, walls_point):
        diagram.walls += [(random.randrange(0, diagram.width), random.randrange(0, diagram.height ))]
    return diagram
'''

def generate_start_goal_point(width, height, walls):
    start = tuple()
    goal = tuple()
    not_filled = True
    random.seed(None, 2)
    state = random.getstate()
    random.setstate(state)
    while not_filled:
        start = (random.randrange(0, width), random.randrange(0, height))
        goal = (random.randrange(0, width), random.randrange(0, height))
        not_filled = start in walls or goal in walls
    return start, goal


diagram4 = GridWithAdjustedWeights(15, 15)
diagram4.walls = [
                    (2, 12), (3, 12), (4, 12), (5, 12), (6, 12), (7, 12),(8, 12), (9, 12), (10, 12),(11, 12), (12, 12),
                    (12, 2), (12, 3), (12, 4), (12, 5), (12, 6), (12, 7),(12, 8), (12, 9), (12, 10),(12, 11),
                    (5,2),(6,2),(7,2),(8,2),(9,2),(10,2),(11,2)
                 ]
diagram4.weights = {loc: 1 for loc in [(3, 4), (3, 5), (4, 1), (4, 2),
                                       (4, 3), (4, 4), (4, 5), (4, 6),
                                       (4, 7), (4, 8), (5, 1), (5, 2),
                                       (5, 3), (5, 4), (5, 5), (5, 6),
                                       (5, 7), (5, 8), (6, 2), (6, 3),
                                       (6, 4), (6, 5), (6, 6), (6, 7),
                                       (7, 3), (7, 4), (7, 5)]}

start,goal = generate_start_goal_point(diagram4.width, diagram4.height, diagram4.walls)
came_from, cost_so_far = a_star_search(diagram4, start, goal)
# draw_grid(diagram4, number = cost_so_far, start=start, goal=goal)
print()
draw_grid(diagram4, path=reconstruct_path(came_from, start=start, goal=goal), start=start, goal=goal)