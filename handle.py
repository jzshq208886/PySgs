import pygame
import sys
import time
from pygame.locals import *


def clickHandle():
    for event in pygame.event.get():
        if event.type == QUIT:  # 事件类型为退出时
            pygame.quit()
            sys.exit()
        if event.type == MOUSEBUTTONDOWN:  # 当点击鼠标时
            x, y = pygame.mouse.get_pos()  # 获取点击鼠标的位置坐标
            return x, y
        if event.type == KEYDOWN:
            return int(event.key)
    return 0, 0


def quitHandle():
    for event in pygame.event.get():
        if event.type == QUIT:  # 事件类型为退出时
            pygame.quit()
            sys.exit()
        if event.type == MOUSEBUTTONDOWN:  # 当点击鼠标时
            x, y = pygame.mouse.get_pos()  # 获取点击鼠标的位置坐标
            if 1356 <= x <= 1540 and 0 <= y <= 139:
                pygame.quit()
                sys.exit()
