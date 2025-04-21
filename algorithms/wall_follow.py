# algorithms/wall_follow.py
class WallFollower:
    def __init__(self, maze):
        self.maze = maze
        self.direction = 0  # 0:右,1:下,2:左,3:上
        self.pos = (0, 0)

    def next_move(self):
        # 优先右转，其次直行，最后左转
        right_dir = (self.direction - 1) % 4
        front_dir = self.direction
        left_dir = (self.direction + 1) % 4

        if self.can_move(right_dir):
            self.direction = right_dir
            return self.get_vector()
        elif self.can_move(front_dir):
            return self.get_vector()
        else:
            self.direction = left_dir
            return (0, 0)  # 需要转向

    def can_move(self, direction):
        x, y = self.pos
        cell = self.maze[y][x]
        return not (cell & (1 << direction))
