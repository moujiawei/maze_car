# widgets/maze_widget.py
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, pyqtSignal
import random
from collections import deque
import heapq


class MazeWidget(QWidget):
    # 添加到达终点的信号
    reached_end = pyqtSignal()

    def __init__(self, size, cell_size):
        super().__init__()
        self.size = size
        self.maze = self.generate_maze()
        self.car_pos = (0, 0)
        self.cell_size = cell_size
        self.setFixedSize(size*cell_size, size*cell_size)
        # 添加方向状态
        self.current_direction = 1  # 0:上, 1:右, 2:下, 3:左
        self.last_turn = 0  # 0:无转向, 1:左转, 2:右转
        self.stuck_count = 0  # 卡住计数器
        self.is_running = False  # 添加运行状态标志
        self.optimal_path = []  # 存储最优路径
        self.path_index = 0     # 当前路径索引
        self.exits = [(self.size-1, self.size-1)]  # 默认出口
        self.is_complex_maze = False

    def generate_maze(self):
        """生成单出口迷宫"""
        self.is_complex_maze = False
        # 初始化迷宫，所有格子都是墙
        maze = [[15 for _ in range(self.size)] for _ in range(self.size)]
        
        def carve_path(x, y):
            visited = [[False for _ in range(self.size)] for _ in range(self.size)]
            visited[y][x] = True
            stack = [(x, y)]
            
            while stack:
                current_x, current_y = stack[-1]
                
                directions = []
                possible_dirs = [
                    (0, -1, 1, 4),  # 上
                    (1, 0, 2, 8),   # 右
                    (0, 1, 4, 1),   # 下
                    (-1, 0, 8, 2)   # 左
                ]
                
                random.shuffle(possible_dirs)
                
                for dx, dy, wall, next_wall in possible_dirs:
                    next_x, next_y = current_x + dx, current_y + dy
                    if (0 <= next_x < self.size and 0 <= next_y < self.size and 
                        not visited[next_y][next_x]):
                        directions.append((dx, dy, wall, next_wall, next_x, next_y))
                
                if directions:
                    dx, dy, wall, next_wall, next_x, next_y = directions[0]
                    maze[current_y][current_x] &= ~wall
                    maze[next_y][next_x] &= ~next_wall
                    visited[next_y][next_x] = True
                    stack.append((next_x, next_y))
                else:
                    stack.pop()
        
        # 从起点开始生成迷宫
        carve_path(0, 0)
        
        # 设置单一出口
        self.exits = [(self.size-1, self.size-1)]
        
        # 确保出口是通的
        maze[0][0] &= ~8  # 移除起点左墙
        maze[self.size-1][self.size-1] &= ~2  # 移除终点右墙
        
        return maze

    def generate_complex_maze(self):
        """生成多出口的复杂迷宫"""
        self.is_complex_maze = True
        # 初始化迷宫，所有格子都是墙
        maze = [[15 for _ in range(self.size)] for _ in range(self.size)]
        
        # 使用改进的DFS生成基本迷宫结构
        def carve_path(x, y):
            visited = [[False for _ in range(self.size)] for _ in range(self.size)]
            visited[y][x] = True
            stack = [(x, y)]
            
            while stack:
                current_x, current_y = stack[-1]
                
                directions = []
                possible_dirs = [
                    (0, -1, 1, 4),  # 上
                    (1, 0, 2, 8),   # 右
                    (0, 1, 4, 1),   # 下
                    (-1, 0, 8, 2)   # 左
                ]
                
                random.shuffle(possible_dirs)
                
                for dx, dy, wall, next_wall in possible_dirs:
                    next_x, next_y = current_x + dx, current_y + dy
                    if (0 <= next_x < self.size and 0 <= next_y < self.size and 
                        not visited[next_y][next_x]):
                        directions.append((dx, dy, wall, next_wall, next_x, next_y))
                
                if directions:
                    dx, dy, wall, next_wall, next_x, next_y = directions[0]
                    maze[current_y][current_x] &= ~wall
                    maze[next_y][next_x] &= ~next_wall
                    visited[next_y][next_x] = True
                    stack.append((next_x, next_y))
                else:
                    stack.pop()
        
        # 从起点开始生成迷宫
        carve_path(0, 0)
        
        # 生成3-4个出口
        num_exits = random.randint(3, 4)
        self.exits = []
        
        # 定义最小距离
        min_distance = self.size // 3  # 确保出口之间至少间隔迷宫大小的1/3
        
        # 可能的出口位置（边界格子）
        possible_exits = []
        
        # 添加右边界的格子
        for y in range(self.size):
            possible_exits.append((self.size-1, y))
        
        # 添加下边界的格子
        for x in range(self.size):
            possible_exits.append((x, self.size-1))
        
        # 移除起点附近的格子（扩大范围）
        possible_exits = [(x, y) for x, y in possible_exits 
                         if abs(x) + abs(y) > self.size//2]
        
        def manhattan_distance(pos1, pos2):
            return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        
        # 选择出口，确保它们之间的距离
        selected_exits = []
        while len(selected_exits) < num_exits and possible_exits:
            # 随机选择一个可能的出口
            candidate = random.choice(possible_exits)
            
            # 检查与已选出口的距离
            is_valid = True
            for existing_exit in selected_exits:
                if manhattan_distance(candidate, existing_exit) < min_distance:
                    is_valid = False
                    break
            
            if is_valid:
                selected_exits.append(candidate)
            
            # 从可能的出口中移除这个候选
            possible_exits.remove(candidate)
            
            # 同时移除候选附近的点（为了加快处理速度）
            possible_exits = [pos for pos in possible_exits 
                            if manhattan_distance(pos, candidate) >= min_distance]
        
        # 如果没有找到足够的合适出口，适当减小距离要求
        while len(selected_exits) < num_exits and min_distance > 2:
            min_distance -= 1
            # 重新生成可能的出口
            possible_exits = []
            for y in range(self.size):
                possible_exits.append((self.size-1, y))
            for x in range(self.size):
                possible_exits.append((x, self.size-1))
            possible_exits = [(x, y) for x, y in possible_exits 
                            if abs(x) + abs(y) > self.size//2]
            
            # 继续选择出口
            for pos in possible_exits:
                if len(selected_exits) >= num_exits:
                    break
                    
                is_valid = True
                for existing_exit in selected_exits:
                    if manhattan_distance(pos, existing_exit) < min_distance:
                        is_valid = False
                        break
                
                if is_valid:
                    selected_exits.append(pos)
        
        self.exits = selected_exits
        
        # 确保每个出口都可以到达
        for exit_x, exit_y in self.exits:
            # 打通到出口的墙
            if exit_x == self.size-1:  # 右边界
                maze[exit_y][exit_x] &= ~2
            if exit_y == self.size-1:  # 下边界
                maze[exit_y][exit_x] &= ~4
        
        # 确保入口是通的
        maze[0][0] &= ~8  # 移除起点左墙
        
        return maze

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制迷宫
        if self.maze:
            for y in range(len(self.maze)):
                for x in range(len(self.maze[y])):
                    self.draw_cell(painter, x, y)

        # 绘制出口标记
        if self.is_complex_maze:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 0, 255, 100))  # 半透明的蓝色
            for exit_x, exit_y in self.exits:
                painter.drawRect(
                    exit_x * self.cell_size,
                    exit_y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )

        # 如果有最优路径，绘制路径
        if self.optimal_path:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 255, 0, 64))
            for x, y in self.optimal_path:
                painter.drawRect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )

        # 绘制小车
        self.draw_car(painter)

    def draw_cell(self, painter, x, y):
        cell = self.maze[y][x]
        x_pix = x * self.cell_size
        y_pix = y * self.cell_size

        pen = QPen(Qt.black, 2)
        painter.setPen(pen)

        if cell & 1:  # 上墙
            painter.drawLine(x_pix, y_pix, x_pix+self.cell_size, y_pix)
        if cell & 2:  # 右墙
            painter.drawLine(x_pix+self.cell_size, y_pix,
                             x_pix+self.cell_size, y_pix+self.cell_size)
        if cell & 4:  # 下墙
            painter.drawLine(x_pix, y_pix+self.cell_size,
                             x_pix+self.cell_size, y_pix+self.cell_size)
        if cell & 8:  # 左墙
            painter.drawLine(x_pix, y_pix, x_pix, y_pix+self.cell_size)

    def draw_car(self, painter):
        x = self.car_pos[0] * self.cell_size + self.cell_size//4
        y = self.car_pos[1] * self.cell_size + self.cell_size//4
        size = self.cell_size//2
        painter.setBrush(QColor(255, 0, 0))
        painter.drawEllipse(x, y, size, size)

    def reset_car(self):
        """重置小车位置"""
        self.car_pos = (0, 0)
        self.update()

    def can_move(self, dx, dy):
        """检查是否可以移动到指定方向"""
        new_x = self.car_pos[0] + dx
        new_y = self.car_pos[1] + dy
        
        if not (0 <= new_x < self.size and 0 <= new_y < self.size):
            return False

        current_cell = self.maze[self.car_pos[1]][self.car_pos[0]]
        if dx == 1 and current_cell & 2:  # 右墙
            return False
        if dx == -1 and current_cell & 8:  # 左墙
            return False
        if dy == 1 and current_cell & 4:  # 下墙
            return False
        if dy == -1 and current_cell & 1:  # 上墙
            return False
        return True

    def wall_follow_step(self):
        """改进的墙壁跟随算法，支持多出口"""
        if not self.is_running or self.car_pos in self.exits:
            if self.car_pos in self.exits:
                self.is_running = False
                self.reached_end.emit()
            return

        # 保持原有的墙壁跟随逻辑
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        current_dx, current_dy = directions[self.current_direction]
        right_direction = (self.current_direction + 1) % 4
        right_dx, right_dy = directions[right_direction]
        front_dx, front_dy = current_dx, current_dy
        left_direction = (self.current_direction - 1) % 4
        left_dx, left_dy = directions[left_direction]
        
        if self.can_move(right_dx, right_dy):
            self.current_direction = right_direction
            self.car_pos = (self.car_pos[0] + right_dx, self.car_pos[1] + right_dy)
            self.last_turn = 2
            self.stuck_count = 0
        elif self.can_move(front_dx, front_dy):
            self.car_pos = (self.car_pos[0] + front_dx, self.car_pos[1] + front_dy)
            self.last_turn = 0
            self.stuck_count = 0
        elif self.can_move(left_dx, left_dy):
            self.current_direction = left_direction
            self.car_pos = (self.car_pos[0] + left_dx, self.car_pos[1] + left_dy)
            self.last_turn = 1
            self.stuck_count = 0
        else:
            self.current_direction = (self.current_direction + 2) % 4
            self.stuck_count += 1
            if self.stuck_count > 3:
                self.current_direction = random.randint(0, 3)
                self.stuck_count = 0
        
        self.update()

    def start_wall_follow(self):
        """开始墙壁跟随"""
        self.is_running = True
        self.current_direction = 1  # 重置方向为向右
        self.stuck_count = 0

    def stop_wall_follow(self):
        """停止墙壁跟随"""
        self.is_running = False

    def manhattan_distance(self, pos1, pos2):
        """计算曼哈顿距离"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def find_optimal_path(self):
        """使用A*算法找到到最近出口的最优路径"""
        start = (0, 0)
        
        # 优先队列，存储 (f_score, pos, path)
        if self.is_complex_maze:
            # 多出口模式：计算到最近出口的距离
            initial_score = min(self.manhattan_distance(start, exit_pos) for exit_pos in self.exits)
        else:
            # 单出口模式：使用唯一的出口
            initial_score = self.manhattan_distance(start, (self.size-1, self.size-1))
            
        open_set = [(initial_score, start, [start])]
        heapq.heapify(open_set)
        
        # 已访问的节点集合
        closed_set = set()
        
        # g_score[pos] 存储从起点到pos的实际距离
        g_score = {start: 0}
        
        while open_set:
            _, current, path = heapq.heappop(open_set)
            
            # 检查是否到达出口
            if self.is_complex_maze:
                if current in self.exits:
                    self.optimal_path = path
                    return True
            else:
                if current == (self.size-1, self.size-1):
                    self.optimal_path = path
                    return True
                
            if current in closed_set:
                continue
                
            closed_set.add(current)
            
            # 检查四个方向
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                next_x = current[0] + dx
                next_y = current[1] + dy
                next_pos = (next_x, next_y)
                
                if not self.can_move_between(current, next_pos):
                    continue
                
                tentative_g_score = g_score[current] + 1
                
                if next_pos in g_score and tentative_g_score >= g_score[next_pos]:
                    continue
                
                g_score[next_pos] = tentative_g_score
                
                # 计算启发式距离
                if self.is_complex_maze:
                    h_score = min(self.manhattan_distance(next_pos, exit_pos) 
                                for exit_pos in self.exits)
                else:
                    h_score = self.manhattan_distance(next_pos, (self.size-1, self.size-1))
                
                f_score = tentative_g_score + h_score
                heapq.heappush(open_set, (f_score, next_pos, path + [next_pos]))
        
        return False

    def can_move_between(self, pos1, pos2):
        """检查两个相邻位置之间是否可以移动"""
        if not (0 <= pos2[0] < self.size and 0 <= pos2[1] < self.size):
            return False
            
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        
        # 检查墙的存在
        if dx == 1:  # 向右移动
            return not (self.maze[pos1[1]][pos1[0]] & 2)
        elif dx == -1:  # 向左移动
            return not (self.maze[pos1[1]][pos1[0]] & 8)
        elif dy == 1:  # 向下移动
            return not (self.maze[pos1[1]][pos1[0]] & 4)
        elif dy == -1:  # 向上移动
            return not (self.maze[pos1[1]][pos1[0]] & 1)
        return False

    def auto_solve_step(self):
        """执行智能寻路的一步"""
        if not self.optimal_path:
            if not self.find_optimal_path():
                print("无法找到路径！")
                return
            self.path_index = 0
            
        # 检查是否到达终点
        if self.is_complex_maze:
            if self.car_pos in self.exits:
                self.reached_end.emit()
                return
        else:
            if self.car_pos == (self.size-1, self.size-1):
                self.reached_end.emit()
                return
            
        # 按照预计算的路径移动
        if self.path_index < len(self.optimal_path):
            self.car_pos = self.optimal_path[self.path_index]
            self.path_index += 1
            self.update()
            
            # 再次检查是否到达终点
            if self.is_complex_maze:
                if self.car_pos in self.exits:
                    self.reached_end.emit()
            else:
                if self.car_pos == (self.size-1, self.size-1):
                    self.reached_end.emit()

    def start_auto_solve(self):
        """开始智能求解"""
        self.optimal_path = []
        self.path_index = 0
        self.car_pos = (0, 0)
        self.update()

    def reset_to_single_exit(self):
        """重置为单出口迷宫"""
        self.maze = self.generate_maze()
        self.car_pos = (0, 0)
        self.optimal_path = []
        self.path_index = 0
        self.is_complex_maze = False
        self.exits = [(self.size-1, self.size-1)]
        self.update()
