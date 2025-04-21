# algorithms/auto_solver.py
import heapqd

class AStarSolver:
    def __init__(self, maze):
        self.maze = maze
        self.size = len(maze)
        
    def solve(self, start=(0,0), end=None):
        end = end or (self.size-1, self.size-1)
        open_set = []
        heapq.heappush(open_set, (0, start))
        
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, end)}

        while open_set:
            current = heapq.heappop(open_set)[1]
            
            if current == end:
                return self.reconstruct_path(came_from, current)
                
            for neighbor in self.get_neighbors(current):
                tentative_g = g_score[current] + 1
                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + self.heuristic(neighbor, end)
                    heapq.heappush(open_set, (f, neighbor))
                    
        return None

    def heuristic(self, a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def get_neighbors(self, pos):
        x, y = pos
        neighbors = []
        cell = self.maze[y][x]
        
        if not (cell & (1 << 0)): # 可向上
            neighbors.append((x, y-1))
        if not (cell & (1 << 1)): # 可向右
            neighbors.append((x+1, y))
        # ... 检查其他方向
        
        return neighbors