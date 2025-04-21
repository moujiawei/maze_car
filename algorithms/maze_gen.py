# algorithms/maze_gen.py
import random
from enum import Enum

class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

class MazeGenerator:
    def __init__(self, size=15):
        self.size = size
        self.maze = [[15 for _ in range(size)] for _ in range(size)] # 每个单元格4位表示墙

    def generate(self):
        self._divide(0, 0, self.size, self.size)
        self._set_entrance_exit()
        return self.maze

    def _divide(self, x, y, width, height):
        if width < 2 or height < 2:
            return

        # 随机选择分割方向
        if width > height:
            self._divide_vertical(x, y, width, height)
        else:
            self._divide_horizontal(x, y, width, height)

    def _divide_vertical(self, x, y, width, height):
        split = random.randint(x+1, x+width-2)
        gap = random.randint(y, y+height-1)
        
        for row in range(y, y+height):
            if row != gap:
                self.maze[row][split] |= 1 << Direction.LEFT.value
                self.maze[row][split-1] |= 1 << Direction.RIGHT.value

        self._divide(x, y, split-x, height)
        self._divide(split, y, x+width-split, height)

    def _set_entrance_exit(self):
        # 入口在左上，出口在右下
        self.maze[0][0] &= ~(1 << Direction.UP.value)
        self.maze[-1][-1] &= ~(1 << Direction.DOWN.value)