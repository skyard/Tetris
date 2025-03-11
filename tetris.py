import pygame # type: ignore
import random
import os
import json
import sys
from datetime import datetime

# 初始化
pygame.init()

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
LIGHT_BLUE = (173, 216, 230)  # 添加浅蓝色
GOLD = (255, 215, 0)  # 添加金色
SILVER = (192, 192, 192)  # 添加银色
LIGHT_GRAY = (211, 211, 211)  # 添加浅灰色
BRIGHT_RED = (255, 50, 50)  # 添加亮红色

# 游戏参数
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * GRID_WIDTH  # 恢复原来的宽度
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT
LOGIN_WIDTH = 500
LOGIN_HEIGHT = 450  # 增加登录窗口高度，给提示信息留出更多空间

# 方块形状
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]]   # Z
]

COLORS = [CYAN, YELLOW, MAGENTA, ORANGE, BLUE, GREEN, RED]

# 用户数据文件
USER_DATA_FILE = "tetris_users.json"

# 获取支持中文的字体
def get_font(size, bold=False):
    # 尝试使用系统中可能存在的中文字体
    font_names = [
        'SimHei',  # 中文黑体
        'Microsoft YaHei',  # 微软雅黑
        'SimSun',  # 中文宋体
        'NSimSun',  # 新宋体
        'FangSong',  # 仿宋
        'KaiTi',  # 楷体
        'Arial Unicode MS'  # 通用字体
    ]
    
    # 尝试加载系统字体
    for font_name in font_names:
        try:
            return pygame.font.SysFont(font_name, size, bold=bold)
        except:
            continue
    
    # 如果没有找到合适的系统字体，使用默认字体
    return pygame.font.Font(None, size)

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = GRAY
        self.text = text
        self.font = get_font(24)
        self.txt_surface = self.font.render(text, True, WHITE)
        self.active = False
        self.password = False

    def set_password_mode(self, is_password):
        self.password = is_password

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 如果用户点击了输入框
            if self.rect.collidepoint(event.pos):
                # 切换激活状态
                self.active = True
            else:
                self.active = False
            # 改变颜色
            self.color = BLUE if self.active else GRAY
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # 重新渲染文本
                display_text = '*' * len(self.text) if self.password else self.text
                self.txt_surface = self.font.render(display_text, True, WHITE)
        return False

    def update(self):
        # 调整输入框的宽度以适应文本
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # 绘制输入框
        pygame.draw.rect(screen, self.color, self.rect, 2)
        # 绘制文本
        display_text = '*' * len(self.text) if self.password else self.text
        self.txt_surface = self.font.render(display_text, True, WHITE)
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))

class Button:
    def __init__(self, x, y, w, h, text, color=BLUE):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.text = text
        self.font = get_font(24)
        self.txt_surface = self.font.render(text, True, WHITE)

    def draw(self, screen):
        # 绘制按钮
        pygame.draw.rect(screen, self.color, self.rect)
        # 绘制文本
        text_rect = self.txt_surface.get_rect(center=self.rect.center)
        screen.blit(self.txt_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class UserManager:
    def __init__(self):
        self.users = {}
        self.current_user = None
        self.load_users()

    def load_users(self):
        if os.path.exists(USER_DATA_FILE):
            try:
                with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
            except:
                self.users = {}
        else:
            self.users = {}

    def save_users(self):
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=4)
    
    def generate_user_id(self):
        # 生成新的用户ID，从00001开始累加
        if not self.users:
            return "00001"
        
        # 找到当前最大的用户ID
        max_id = 0
        for user_id in self.users.keys():
            try:
                id_num = int(user_id)
                if id_num > max_id:
                    max_id = id_num
            except ValueError:
                continue
        
        # 返回下一个ID
        return f"{max_id + 1:05d}"

    def register_user(self, username, password):
        # 检查用户名是否已存在
        for user_id, user_data in self.users.items():
            if user_data.get("username") == username:
                return False, "用户名已存在"
                
        # 生成新的用户ID
        user_id = self.generate_user_id()
        
        self.users[user_id] = {
            "username": username,
            "password": password,
            "highest_score": 0,
            "lowest_score": 0,
            "game_count": 0,
            "last_played": ""
        }
        self.save_users()
        return True, f"注册成功，您的用户名是: {username}"

    def login(self, username, password):
        # 通过用户名查找用户
        user_id = None
        for uid, user_data in self.users.items():
            if user_data.get("username") == username:
                user_id = uid
                break
                
        if user_id is None:
            return False, "用户不存在"
        
        if self.users[user_id]["password"] != password:
            return False, "密码错误"
        
        self.current_user = user_id
        return True, "登录成功"

    def update_user_stats(self, score):
        if not self.current_user:
            return
        
        user = self.users[self.current_user]
        user["game_count"] += 1
        user["last_played"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 更新最高分
        if score > user["highest_score"]:
            user["highest_score"] = score
        
        # 更新最低分（如果是第一次玩或者当前分数低于最低分）
        if user["lowest_score"] == 0 or score < user["lowest_score"]:
            user["lowest_score"] = score
        
        self.save_users()

class LoginScreen:
    def __init__(self, user_manager):
        self.screen = pygame.display.set_mode((LOGIN_WIDTH, LOGIN_HEIGHT))
        pygame.display.set_caption("俄罗斯方块 - 登录")
        self.clock = pygame.time.Clock()
        self.user_manager = user_manager
        
        # 登录界面元素 - 调整输入框位置，使其与标签对齐
        self.username_input = InputBox(180, 150, 250, 32)  # 用户名输入框
        self.password_input = InputBox(180, 230, 250, 32)  # 密码输入框
        self.password_input.set_password_mode(True)
        
        # 调整按钮位置和大小
        self.login_button = Button(130, 350, 100, 40, "登录")  # 调整垂直位置
        self.register_button = Button(270, 350, 100, 40, "注册")  # 调整垂直位置
        
        self.message = ""
        self.message_color = WHITE
        self.is_registering = False

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                
                # 处理输入 - 确保两个输入框都能接收事件
                username_entered = self.username_input.handle_event(event)
                password_entered = self.password_input.handle_event(event)
                
                # 如果按下回车键并且在用户名或密码输入框中，尝试登录或注册
                if (username_entered or password_entered) and not self.is_registering:
                    # 登录
                    success, message = self.user_manager.login(
                        self.username_input.text, self.password_input.text)
                    if success:
                        return self.user_manager.current_user
                    else:
                        self.message = message
                        self.message_color = RED
                elif (username_entered or password_entered) and self.is_registering:
                    # 注册
                    if not self.username_input.text or not self.password_input.text:
                        self.message = "所有字段都必须填写"
                        self.message_color = RED
                    else:
                        success, message = self.user_manager.register_user(
                            self.username_input.text, self.password_input.text)
                        if success:
                            self.is_registering = False
                            self.message = message
                            self.message_color = GREEN
                        else:
                            self.message = message
                            self.message_color = RED
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.login_button.is_clicked(event.pos):
                        if not self.is_registering:
                            # 登录
                            success, message = self.user_manager.login(
                                self.username_input.text, self.password_input.text)
                            if success:
                                return self.user_manager.current_user
                            else:
                                self.message = message
                                self.message_color = RED
                        else:
                            # 切换到登录模式
                            self.is_registering = False
                            self.message = ""
                            # 清空输入框
                            self.username_input.text = ""
                            self.username_input.txt_surface = self.username_input.font.render("", True, WHITE)
                            self.password_input.text = ""
                            self.password_input.txt_surface = self.password_input.font.render("", True, WHITE)
                    
                    elif self.register_button.is_clicked(event.pos):
                        if self.is_registering:
                            # 注册
                            if not self.username_input.text or not self.password_input.text:
                                self.message = "所有字段都必须填写"
                                self.message_color = RED
                            else:
                                success, message = self.user_manager.register_user(
                                    self.username_input.text, self.password_input.text)
                                if success:
                                    self.is_registering = False
                                    self.message = message
                                    self.message_color = GREEN
                                else:
                                    self.message = message
                                    self.message_color = RED
                        else:
                            # 切换到注册模式
                            self.is_registering = True
                            self.message = "请填写注册信息"
                            self.message_color = WHITE
                            # 清空输入框
                            self.username_input.text = ""
                            self.username_input.txt_surface = self.username_input.font.render("", True, WHITE)
                            self.password_input.text = ""
                            self.password_input.txt_surface = self.password_input.font.render("", True, WHITE)
            
            # 更新输入框
            self.username_input.update()
            self.password_input.update()
            
            self.screen.fill(BLACK)
            
            # 绘制标题
            font = get_font(32)
            title = "注册新用户" if self.is_registering else "用户登录"
            title_surface = font.render(title, True, WHITE)
            self.screen.blit(title_surface, (LOGIN_WIDTH // 2 - title_surface.get_width() // 2, 30))
            
            # 绘制提示消息 - 移到标题下方，增加间距
            if self.message:
                # 如果消息太长，分行显示
                words = self.message.split()
                lines = []
                current_line = ""
                label_font = get_font(24)
                
                for word in words:
                    test_line = current_line + word + " "
                    if label_font.size(test_line)[0] < LOGIN_WIDTH - 60:
                        current_line = test_line
                    else:
                        lines.append(current_line)
                        current_line = word + " "
                
                if current_line:
                    lines.append(current_line)
                
                # 绘制每一行 - 在标题下方显示，增加垂直间距
                for i, line in enumerate(lines):
                    message_surface = label_font.render(line, True, self.message_color)
                    message_rect = message_surface.get_rect(center=(LOGIN_WIDTH // 2, 90 + i * 30))
                    self.screen.blit(message_surface, message_rect)
            
            # 绘制标签和输入框
            label_font = get_font(24)
            
            # 显示用户名和密码字段
            username_label = label_font.render("用户名:", True, WHITE)
            username_label_rect = username_label.get_rect(right=170, centery=166)
            self.screen.blit(username_label, username_label_rect)
            self.username_input.draw(self.screen)
            
            password_label = label_font.render("密码:", True, WHITE)
            password_label_rect = password_label.get_rect(right=170, centery=246)
            self.screen.blit(password_label, password_label_rect)
            self.password_input.draw(self.screen)
            
            # 调整按钮位置
            self.login_button.rect.y = 350
            self.register_button.rect.y = 350
            
            # 更新按钮文本
            login_text = "返回登录" if self.is_registering else "登录"
            self.login_button.text = login_text
            self.login_button.txt_surface = self.login_button.font.render(login_text, True, WHITE)
            
            register_text = "确认注册" if self.is_registering else "注册"
            self.register_button.text = register_text
            self.register_button.txt_surface = self.register_button.font.render(register_text, True, WHITE)
            
            # 绘制按钮
            self.login_button.draw(self.screen)
            self.register_button.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(30)
        
        return None

class Tetris:
    def __init__(self, user_manager, user_id):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("俄罗斯方块")
        self.clock = pygame.time.Clock()
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()  # 添加下一个方块
        self.game_over = False
        self.score = 0
        self.user_manager = user_manager
        self.user_id = user_id
        self.last_fall_time = pygame.time.get_ticks()  # 使用精确的时间控制
        
    def new_piece(self):
        shape = random.choice(SHAPES)
        color = COLORS[SHAPES.index(shape)]
        x = GRID_WIDTH // 2 - len(shape[0]) // 2
        y = 0
        return {'shape': shape, 'x': x, 'y': y, 'color': color}
    
    def valid_move(self, piece, x, y):
        for i in range(len(piece['shape'])):
            for j in range(len(piece['shape'][0])):
                if piece['shape'][i][j]:
                    if (x + j < 0 or x + j >= GRID_WIDTH or
                        y + i >= GRID_HEIGHT or
                        (y + i >= 0 and self.grid[y + i][x + j])):
                        return False
        return True
    
    def merge_piece(self):
        for i in range(len(self.current_piece['shape'])):
            for j in range(len(self.current_piece['shape'][0])):
                if self.current_piece['shape'][i][j]:
                    self.grid[self.current_piece['y'] + i][self.current_piece['x'] + j] = self.current_piece['color']
    
    def clear_lines(self):
        lines_cleared = 0
        i = GRID_HEIGHT - 1
        while i >= 0:
            if all(self.grid[i]):
                del self.grid[i]
                self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
                lines_cleared += 1
            else:
                i -= 1
        self.score += lines_cleared * 100
    
    def draw_grid_lines(self):
        # 绘制虚线网格
        for i in range(GRID_HEIGHT + 1):
            # 绘制水平虚线
            for x in range(0, GRID_WIDTH * BLOCK_SIZE, 5):  # 每5像素绘制一个点
                pygame.draw.line(self.screen, LIGHT_GRAY, 
                               (x, i * BLOCK_SIZE), 
                               (x + 2, i * BLOCK_SIZE), 1)
        
        for j in range(GRID_WIDTH + 1):
            # 绘制垂直虚线
            for y in range(0, GRID_HEIGHT * BLOCK_SIZE, 5):  # 每5像素绘制一个点
                pygame.draw.line(self.screen, LIGHT_GRAY, 
                               (j * BLOCK_SIZE, y), 
                               (j * BLOCK_SIZE, y + 2), 1)
    
    def draw_piece(self, piece, offset_x=0, offset_y=0, scale=1.0):
        # 绘制方块（可用于主游戏区和预览区）
        for i in range(len(piece['shape'])):
            for j in range(len(piece['shape'][0])):
                if piece['shape'][i][j]:
                    color = piece['color']
                    x = (piece['x'] + j) * BLOCK_SIZE * scale + offset_x
                    y = (piece['y'] + i) * BLOCK_SIZE * scale + offset_y
                    block_size = int(BLOCK_SIZE * scale)
                    
                    pygame.draw.rect(self.screen, color,
                                  (x, y, block_size - 1, block_size - 1))
                    # 添加高光效果
                    pygame.draw.line(self.screen, WHITE, 
                                   (x, y), 
                                   (x, y + block_size - 1), 1)
                    pygame.draw.line(self.screen, WHITE, 
                                   (x, y), 
                                   (x + block_size - 1, y), 1)
    
    def draw_next_piece_preview(self):
        # 绘制下一个方块预览区域 - 放在信息面板中
        preview_x = SCREEN_WIDTH - 140  # 向左移动
        preview_y = 15  # 进一步向上移动，与分数对齐
        preview_size = 80  # 预览区域大小
        
        # 计算预览方块的位置
        shape_width = len(self.next_piece['shape'][0]) * (BLOCK_SIZE * 0.6)  # 缩小比例
        shape_height = len(self.next_piece['shape']) * (BLOCK_SIZE * 0.6)
        
        # 居中显示预览方块
        preview_piece = self.next_piece.copy()
        preview_piece['x'] = 0
        preview_piece['y'] = 0
        
        # 绘制预览方块 - 使用缩小的比例
        center_x = preview_x + (preview_size - shape_width) / 2
        center_y = preview_y + (preview_size - shape_height) / 2
        self.draw_piece(preview_piece, center_x, center_y, 0.6)  # 缩小为原来的60%
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # 绘制虚线网格
        self.draw_grid_lines()
        
        # 绘制网格
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                if self.grid[i][j]:
                    # 添加3D效果
                    color = self.grid[i][j]
                    pygame.draw.rect(self.screen, color,
                                  (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1))
                    # 添加高光效果
                    pygame.draw.line(self.screen, WHITE, 
                                   (j * BLOCK_SIZE, i * BLOCK_SIZE), 
                                   (j * BLOCK_SIZE, (i+1) * BLOCK_SIZE - 1), 1)
                    pygame.draw.line(self.screen, WHITE, 
                                   (j * BLOCK_SIZE, i * BLOCK_SIZE), 
                                   ((j+1) * BLOCK_SIZE - 1, i * BLOCK_SIZE), 1)
        
        # 绘制当前方块
        if self.current_piece:
            self.draw_piece(self.current_piece)
        
        # 创建信息面板背景
        info_panel = pygame.Rect(0, 0, SCREEN_WIDTH, 110)
        pygame.draw.rect(self.screen, (30, 30, 30), info_panel)  # 深灰色背景
        pygame.draw.rect(self.screen, BLUE, info_panel, 1)  # 蓝色边框，减小宽度
        
        # 使用更小的字体
        title_font = get_font(18)  # 标题字体
        bold_font = get_font(18, bold=True)  # 粗体字体
        info_font = get_font(16)  # 信息字体
        bold_info_font = get_font(16, bold=True)  # 粗体信息字体
        
        # 绘制玩家信息
        if self.user_id:
            user_info = self.user_manager.users[self.user_id]
            
            # 玩家标签 - 使用白色粗体
            player_label = bold_font.render("玩家:", True, WHITE)
            player_label_rect = player_label.get_rect(topleft=(15, 15))
            self.screen.blit(player_label, player_label_rect)
            
            # 玩家名称 - 使用红色粗体
            player_name = bold_font.render(f'{user_info["username"]}', True, BRIGHT_RED)
            player_name_rect = player_name.get_rect(left=player_label_rect.right + 5, top=15)
            self.screen.blit(player_name, player_name_rect)
            
            # 当前分数标签 - 使用白色粗体，放在右边
            score_label = bold_font.render("当前分数:", True, WHITE)
            score_label_rect = score_label.get_rect()
            score_label_rect.right = SCREEN_WIDTH - 80  # 向左移动一小部分，不要太靠边
            score_label_rect.top = 15
            self.screen.blit(score_label, score_label_rect)
            
            # 当前分数值 - 使用红色粗体
            score_value = bold_font.render(f'{self.score}', True, BRIGHT_RED)
            score_value_rect = score_value.get_rect()
            score_value_rect.left = score_label_rect.right + 5
            score_value_rect.top = 15
            self.screen.blit(score_value, score_value_rect)
            
            # 绘制下一个方块预览 - 放在信息面板中
            self.draw_next_piece_preview()
            
            # 最高分标签 - 使用白色粗体
            high_score_label = bold_info_font.render("最高分:", True, WHITE)
            high_score_label_rect = high_score_label.get_rect(topleft=(15, 45))
            self.screen.blit(high_score_label, high_score_label_rect)
            
            # 最高分值 - 使用红色粗体
            high_score = user_info["highest_score"]
            high_score_value = bold_info_font.render(f'{high_score}', True, BRIGHT_RED)
            high_score_value_rect = high_score_value.get_rect(left=high_score_label_rect.right + 5, top=45)
            self.screen.blit(high_score_value, high_score_value_rect)
            
            # 最低分标签 - 使用白色粗体
            low_score_label = bold_info_font.render("最低分:", True, WHITE)
            low_score_label_rect = low_score_label.get_rect(topleft=(15, 65))
            self.screen.blit(low_score_label, low_score_label_rect)
            
            # 最低分值 - 使用红色粗体
            low_score = user_info["lowest_score"] if user_info["lowest_score"] > 0 else 0
            low_score_value = bold_info_font.render(f'{low_score}', True, BRIGHT_RED)
            low_score_value_rect = low_score_value.get_rect(left=low_score_label_rect.right + 5, top=65)
            self.screen.blit(low_score_value, low_score_value_rect)
            
            # 游戏次数标签 - 使用白色粗体
            game_count_label = bold_info_font.render("游戏次数:", True, WHITE)
            game_count_label_rect = game_count_label.get_rect(topleft=(15, 85))
            self.screen.blit(game_count_label, game_count_label_rect)
            
            # 游戏次数值 - 使用红色粗体
            game_count_value = bold_info_font.render(f'{user_info["game_count"]}', True, BRIGHT_RED)
            game_count_value_rect = game_count_value.get_rect(left=game_count_label_rect.right + 5, top=85)
            self.screen.blit(game_count_value, game_count_value_rect)
            
            # 最近游戏时间（如果有）- 放在右侧，调整位置
            if user_info["last_played"]:
                # 格式化日期时间，显示到年月日时分
                try:
                    date_time = user_info["last_played"]
                    date_parts = date_time.split(' ')[0]  # 年-月-日
                    time_parts = date_time.split(' ')[1].split(':')  # 时:分:秒
                    
                    # 确保显示分钟
                    hour = time_parts[0]
                    minute = time_parts[1] if len(time_parts) > 1 else "00"
                    formatted_time = f"{date_parts} {hour}:{minute}"
                    
                    # 上次游戏标签 - 使用白色粗体
                    last_played_label = bold_info_font.render("上次:", True, WHITE)
                    last_played_label_rect = last_played_label.get_rect(left=game_count_label_rect.right + 40, top=85)  # 向左移动
                    self.screen.blit(last_played_label, last_played_label_rect)
                    
                    # 上次游戏时间值 - 使用红色普通字体（非粗体）
                    last_played_value = info_font.render(formatted_time, True, BRIGHT_RED)
                    last_played_value_rect = last_played_value.get_rect(left=last_played_label_rect.right + 5, top=85)
                    self.screen.blit(last_played_value, last_played_value_rect)
                except:
                    # 如果时间格式解析失败，显示原始时间
                    last_played_label = bold_info_font.render("上次:", True, WHITE)
                    last_played_label_rect = last_played_label.get_rect(left=game_count_label_rect.right + 40, top=85)  # 向左移动
                    self.screen.blit(last_played_label, last_played_label_rect)
                    
                    last_played_value = info_font.render(user_info["last_played"], True, BRIGHT_RED)
                    last_played_value_rect = last_played_value.get_rect(left=last_played_label_rect.right + 5, top=85)
                    self.screen.blit(last_played_value, last_played_value_rect)
        
        pygame.display.flip()
    
    def run(self):
        # 使用基于时间的更新，而不是基于帧的更新
        fall_speed = 500  # 毫秒，值越小，下落速度越快
        
        while not self.game_over:
            current_time = pygame.time.get_ticks()
            delta_time = current_time - self.last_fall_time
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # 更新用户统计信息
                    if self.user_id:
                        self.user_manager.update_user_stats(self.score)
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if self.valid_move(self.current_piece, self.current_piece['x'] - 1, self.current_piece['y']):
                            self.current_piece['x'] -= 1
                    elif event.key == pygame.K_RIGHT:
                        if self.valid_move(self.current_piece, self.current_piece['x'] + 1, self.current_piece['y']):
                            self.current_piece['x'] += 1
                    elif event.key == pygame.K_DOWN:
                        if self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y'] + 1):
                            self.current_piece['y'] += 1
                            # 重置下落时间
                            self.last_fall_time = current_time
                    elif event.key == pygame.K_UP:
                        rotated = list(zip(*reversed(self.current_piece['shape'])))
                        if self.valid_move({'shape': rotated, 'x': self.current_piece['x'], 'y': self.current_piece['y']},
                                         self.current_piece['x'], self.current_piece['y']):
                            self.current_piece['shape'] = rotated
            
            # 基于时间的方块下落
            if delta_time >= fall_speed:
                if self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y'] + 1):
                    self.current_piece['y'] += 1
                else:
                    self.merge_piece()
                    self.clear_lines()
                    self.current_piece = self.next_piece
                    self.next_piece = self.new_piece()
                    if not self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y']):
                        self.game_over = True
                self.last_fall_time = current_time
            
            self.draw()
            
            # 限制帧率，但不影响游戏逻辑
            self.clock.tick(60)
        
        # 更新用户统计信息
        if self.user_id:
            self.user_manager.update_user_stats(self.score)
        
        # 创建半透明的游戏结束覆盖层
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # 黑色半透明
        self.screen.blit(overlay, (0, 0))
        
        # 创建游戏结束面板
        panel_width = 280
        panel_height = 200
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        # 绘制面板背景
        panel = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, (50, 50, 50), panel)  # 深灰色背景
        pygame.draw.rect(self.screen, RED, panel, 2)  # 红色边框
        
        # 游戏结束显示 - 使用更精致的字体和颜色
        font = get_font(32)  # 减小字体
        game_over_text = font.render('游戏结束!', True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 40))
        self.screen.blit(game_over_text, game_over_rect)
        
        # 显示最终分数 - 使用金色
        score_font = get_font(24)  # 减小字体
        final_score_text = score_font.render(f'最终分数:{self.score}', True, GOLD)
        final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 90))
        self.screen.blit(final_score_text, final_score_rect)
        
        # 添加重玩按钮 - 使用更精致的按钮设计
        restart_font = get_font(20)  # 减小字体
        restart_text = restart_font.render('再玩一次', True, WHITE)
        restart_rect = pygame.Rect(panel_x + 40, panel_y + 130, 200, 40)
        
        # 绘制按钮背景和边框
        pygame.draw.rect(self.screen, BLUE, restart_rect)
        pygame.draw.rect(self.screen, LIGHT_BLUE, restart_rect, 1)  # 减小边框宽度
        
        # 绘制按钮文本
        restart_text_rect = restart_text.get_rect(center=restart_rect.center)
        self.screen.blit(restart_text, restart_text_rect)
        
        # 添加返回登录按钮
        logout_text = restart_font.render('返回登录', True, WHITE)
        logout_rect = pygame.Rect(panel_x + 40, panel_y + 180, 200, 40)
        
        # 绘制按钮背景和边框
        pygame.draw.rect(self.screen, RED, logout_rect)
        pygame.draw.rect(self.screen, (255, 150, 150), logout_rect, 1)  # 浅红色边框，减小宽度
        
        # 绘制按钮文本
        logout_text_rect = logout_text.get_rect(center=logout_rect.center)
        self.screen.blit(logout_text, logout_text_rect)
        
        pygame.display.flip()
        
        # 等待玩家点击重玩按钮或关闭游戏
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if restart_rect.collidepoint(mouse_pos):
                        # 重置游戏状态
                        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
                        self.current_piece = self.new_piece()
                        self.next_piece = self.new_piece()  # 重置下一个方块
                        self.game_over = False
                        self.score = 0
                        self.last_fall_time = pygame.time.get_ticks()  # 重置时间
                        return self.run()
                    elif logout_rect.collidepoint(mouse_pos):
                        return "logout"

def main():
    user_manager = UserManager()
    
    while True:
        # 显示登录界面
        login_screen = LoginScreen(user_manager)
        user_id = login_screen.run()
        
        if user_id is None:
            break  # 用户关闭了窗口
        
        # 开始游戏
        game = Tetris(user_manager, user_id)
        result = game.run()
        
        if result != "logout":
            break  # 用户关闭了窗口

if __name__ == '__main__':
    main()
    pygame.quit() 