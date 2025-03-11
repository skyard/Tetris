@echo off
echo 正在启动俄罗斯方块游戏...
python tetris.py
if errorlevel 1 (
    echo 游戏启动失败！请确保已安装Python和pygame库。
    echo 可以运行以下命令安装pygame：
    echo pip install pygame
    pause
)
