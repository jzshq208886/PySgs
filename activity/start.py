import pygame
from pygame.locals import *
import sys
from extensions.bf.game_bf import game_bf


def activity_start(window, size):
    background = pygame.image.load(r"image\game\background.jpg").convert_alpha()
    button = pygame.image.load(r"image\game\interface\button1_big.png").convert_alpha()
    logo = pygame.image.load(r"image\Sanguoshaicon.jpg").convert_alpha()

    font1 = pygame.font.Font(r'fonts\HYZLSJ.TTF', 40)
    font2 = pygame.font.Font(r'fonts\HYZLSJ.TTF', 25)
    text1 = font1.render("开始游戏", True, (0, 0, 0))
    text1_pos = (680, 515)
    text2_pos = (670, 625)
    text2 = font2.render("查看上一局记录", True, (0, 0, 0))
    text1_area = text1.get_rect(center=(text1_pos[0] + text1.get_size()[0] / 2, text1_pos[1] + text1.get_size()[1] / 2))
    text2_area = text2.get_rect(center=(text2_pos[0] + text2.get_size()[0] / 2, text2_pos[1] + text2.get_size()[1] / 2))

    window.blit(background, (0, 0))
    window.blit(logo, (510, 150))

    window.blit(button, (630, 500))
    window.blit(button, (630, 600))

    window.blit(text1, text1_pos)
    window.blit(text2, text2_pos)

    while True:
        for event in pygame.event.get():
            begin = False
            show_log = False
            if event.type == QUIT:  # 若检测到事件类型为退出，则退出系统
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                begin = True if text1_area.collidepoint(event.pos) else False
                show_log = True if text2_area.collidepoint(event.pos) else False

            if begin:
                game_bf(window, w, h)
            if show_log:
                pass
