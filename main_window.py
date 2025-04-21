# main_window.py
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from widgets.maze_widget import MazeWidget


class MainWindow(QMainWindow):
    def __init__(self): 
        super().__init__()
        self.maze_size = 15
        self.cell_size = 30
        self.init_ui()
        self.current_mode = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.auto_move)
        
        # 手动模式的移动定时器
        self.manual_timer = QTimer(self)
        self.manual_timer.timeout.connect(self.manual_move)
        self.manual_timer.setInterval(100)  # 100ms移动一次
        self.current_direction = None  # 当前按下的方向键
        
        # 设置窗口接收键盘焦点
        self.setFocusPolicy(Qt.StrongFocus)

    def init_ui(self):
        self.setWindowTitle("迷宫小车")
        self.maze_widget = MazeWidget(self.maze_size, self.cell_size)
        
        # 连接到达终点信号
        self.maze_widget.reached_end.connect(self.on_maze_completed)

        # 控制按钮
        self.btn_manual = QPushButton("手动模式 (1)")
        self.btn_auto = QPushButton("自动避障 (2)")
        self.btn_smart = QPushButton("智能求解 (3)")
        
        # 迷宫生成按钮
        self.btn_single = QPushButton("生成单出口迷宫")
        self.btn_complex = QPushButton("生成多出口迷宫")

        # 模式按钮布局
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(self.btn_manual)
        mode_layout.addWidget(self.btn_auto)
        mode_layout.addWidget(self.btn_smart)

        # 迷宫生成按钮布局
        maze_layout = QHBoxLayout()
        maze_layout.addWidget(self.btn_single)
        maze_layout.addWidget(self.btn_complex)

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.maze_widget)
        main_layout.addLayout(mode_layout)
        main_layout.addLayout(maze_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # 信号连接
        self.btn_manual.clicked.connect(self.enter_manual_mode)
        self.btn_auto.clicked.connect(self.start_wall_follow)
        self.btn_smart.clicked.connect(self.start_auto_solve)
        self.btn_single.clicked.connect(self.generate_single_maze)
        self.btn_complex.clicked.connect(self.generate_complex_maze)

    def keyPressEvent(self, event):
        """处理按键按下事件"""
        if self.current_mode != 'manual':
            return

        key = event.key()
        # 如果是新的方向键被按下
        if key in [Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right]:
            self.current_direction = key
            # 如果定时器未运行，启动它
            if not self.manual_timer.isActive():
                self.manual_timer.start()
            # 立即移动一次，避免初次按下的延迟感
            self.manual_move()

    def keyReleaseEvent(self, event):
        """处理按键释放事件"""
        if self.current_mode != 'manual':
            return

        key = event.key()
        # 如果释放的是当前方向键，停止移动
        if key == self.current_direction:
            self.current_direction = None
            self.manual_timer.stop()

    def manual_move(self):
        """手动模式下的移动处理"""
        if self.current_direction is None:
            return

        dx, dy = 0, 0
        if self.current_direction == Qt.Key_Up:
            dy = -1
        elif self.current_direction == Qt.Key_Down:
            dy = 1
        elif self.current_direction == Qt.Key_Left:
            dx = -1
        elif self.current_direction == Qt.Key_Right:
            dx = 1

        if self.maze_widget.can_move(dx, dy):
            current_x, current_y = self.maze_widget.car_pos
            self.maze_widget.car_pos = (current_x + dx, current_y + dy)
            self.maze_widget.update()
            
            # 检查是否到达终点
            if self.maze_widget.car_pos == (self.maze_size-1, self.maze_size-1):
                self.manual_timer.stop()
                self.current_direction = None
                self.maze_widget.reached_end.emit()

    def enter_manual_mode(self):
        """进入手动模式"""
        self.current_mode = 'manual'
        self.timer.stop()
        self.manual_timer.stop()
        self.current_direction = None
        self.maze_widget.reset_car()
        self.maze_widget.stop_wall_follow()
        print("进入手动模式")

    def start_wall_follow(self):
        """开始自动避障模式"""
        self.current_mode = 'wall_follow'
        self.manual_timer.stop()
        self.current_direction = None
        self.maze_widget.reset_car()
        self.maze_widget.start_wall_follow()
        self.timer.start(100)  # 每100ms移动一次
        print("进入自动避障模式")

    def start_auto_solve(self):
        """开始智能求解模式"""
        self.current_mode = 'auto_solve'
        self.manual_timer.stop()
        self.current_direction = None
        self.maze_widget.start_auto_solve()  # 重置路径
        self.timer.start(100)  # 控制移动速度
        print("进入智能求解模式")

    def auto_move(self):
        """自动移动的定时器回调函数"""
        if self.current_mode == 'wall_follow':
            self.maze_widget.wall_follow_step()
        elif self.current_mode == 'auto_solve':
            self.maze_widget.auto_solve_step()

    def on_maze_completed(self):
        """迷宫完成时的回调函数"""
        self.timer.stop()
        self.manual_timer.stop()
        self.current_direction = None
        QMessageBox.information(self, "提示", "恭喜！小车已到达终点！")

    def generate_single_maze(self):
        """生成单出口迷宫"""
        # 停止所有定时器
        self.timer.stop()
        self.manual_timer.stop()
        self.current_direction = None
        
        # 重置为单出口迷宫
        self.maze_widget.reset_to_single_exit()
        
        # 显示提示信息
        QMessageBox.information(self, "提示", "已生成单出口迷宫！\n出口位置在右下角。")

    def generate_complex_maze(self):
        """生成复杂迷宫"""
        # 停止所有定时器
        self.timer.stop()
        self.manual_timer.stop()
        self.current_direction = None
        
        # 生成新的复杂迷宫
        self.maze_widget.maze = self.maze_widget.generate_complex_maze()
        self.maze_widget.car_pos = (0, 0)
        self.maze_widget.optimal_path = []
        self.maze_widget.path_index = 0
        self.maze_widget.update()
        
        # 显示提示信息
        num_exits = len(self.maze_widget.exits)
        QMessageBox.information(self, "提示", f"已生成带有{num_exits}个出口的复杂迷宫！\n蓝色方块标记为出口位置。")
