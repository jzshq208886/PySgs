import linecache
from room import *
# from extensions.bf.game_bf import game_bf


def show_main_page():
    window = pygame.display.set_mode((w, h), 0, 0)
    pygame.display.set_caption("py三国杀")
    window.blit(background, (0, 0))
    window.blit(logo, (510, 150))
    window.blit(button, (630, 500))
    window.blit(button, (630, 600))
    window.blit(text1, text1_pos)
    window.blit(text2, text2_pos)


def show_log_page(file, page, line_num, size):
    if type(line_num) is not int:
        line_num = int(line_num)
    linecache.checkcache(filename='log.txt')
    for i in range(page * line_num + 1, page * line_num + 1 + line_num):
        line = font_log.render(linecache.getline(file, i), True, (255, 255, 255))
        log_window.blit(line, (0, size * (i - page * line_num - 1)))
        # text+='\n'
    linecache.clearcache()
    return True


def game(window, w, h):
    # 初始界面 

    # 房间初始化，玩家加入
    with open('log.txt', mode='a+', encoding='utf-8') as f:
        f.truncate(0)
    room = Room('identity', 3)
    room.initialize(window, w, h)
    # 游戏准备，包括选将与分发初始手牌
    room.prepare()

    # 进行游戏
    room.process()
    return


if __name__ == '__main__':
    pygame.init()

    musics = ['danji', 'default', 'diaochan', 'shezhan']
    volume = {'danji': 1, 'default': 0.5, 'diaochan': 1, 'shezhan': 1}
    music = random.choice(musics)
    music_path = os.path.join(r"audio\background", f'music_{music}.mp3')
    pygame.mixer.music.load(music_path)
    if music in volume:
        pygame.mixer.music.set_volume(volume[music])
    pygame.mixer.music.play(-1)

    w, h = 1500, 780
    window = pygame.display.set_mode((w, h), 0, 0)  # 创建游戏窗口 # 第一个参数是元组：窗口的长和宽
    pygame.display.set_caption("py三国杀")  # 添加游戏标题
    background = pygame.image.load("image\\game\\background.jpg").convert_alpha()
    button = pygame.image.load("image\\game\\interface\\button1_big.png").convert_alpha()
    logo = pygame.image.load("image\\Sanguoshaicon.jpg").convert_alpha()
    window.blit(background, (0, 0))
    window.blit(logo, (510, 150))

    window.blit(button, (630, 500))
    window.blit(button, (630, 600))

    font1 = pygame.font.Font(r'fonts\HYZLSJ.TTF', 40)
    font2 = pygame.font.Font(r'fonts\HYZLSJ.TTF', 25)
    text1 = font1.render("开始游戏", True, (0, 0, 0))
    text1_pos = (680, 515)
    text2_pos = (670, 625)
    text2 = font2.render("查看上一局记录", True, (0, 0, 0))
    text1_area = text1.get_rect(center=(text1_pos[0] + text1.get_size()[0] / 2, text1_pos[1] + text1.get_size()[1] / 2))
    text2_area = text2.get_rect(center=(text2_pos[0] + text2.get_size()[0] / 2, text2_pos[1] + text2.get_size()[1] / 2))

    window.blit(text1, text1_pos)
    window.blit(text2, text2_pos)

    while True:
        begin = False
        for event in pygame.event.get():
            show_log = False
            if event.type == QUIT:  # 若检测到事件类型为退出，则退出系统
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                begin = True if text1_area.collidepoint(event.pos) else False
                show_log = True if text2_area.collidepoint(event.pos) else False

            if begin:
                break
            if show_log:
                w1, h1 = 1000, 600
                log_window = pygame.display.set_mode((w1, h1), 0, 0)
                log_background = pygame.image.load("image\\log_background.bmp").convert_alpha()
                log_window.blit(log_background, (0, 0))
                # log_window.fill((255, 255, 255))
                pygame.display.set_caption("上局记录")
                font_log_size = 20
                font_log = pygame.font.Font("fonts\\xingkai.ttf", font_log_size)
                page = 0
                show_log_page('log.txt', page, h1 / font_log_size, font_log_size)
                turn_page_forward_botton = pygame.image.load(
                    "image\\game\\interface\\confirm-bg-c.png").convert_alpha()
                turn_page_forward_text = font1.render("下一页", True, (255, 255, 255))
                turn_page_forward_botton_pos = (w1 - 150, h1 - 60)
                turn_page_forward_text_pos = (w1 - 137, h1 - 50)
                log_window.blit(turn_page_forward_botton, turn_page_forward_botton_pos)
                log_window.blit(turn_page_forward_text, turn_page_forward_text_pos)
                turn_page_forward_text_area = turn_page_forward_text.get_rect(
                    center=(turn_page_forward_text_pos[0] + turn_page_forward_text.get_size()[0] / 2, \
                            turn_page_forward_text_pos[1] + turn_page_forward_text.get_size()[1] / 2))

                turn_page_backward_botton = pygame.image.load(
                    "image\\game\\interface\\confirm-bg-c.png").convert_alpha()
                turn_page_backward_text = font1.render("上一页", True, (255, 255, 255))
                turn_page_backward_botton_pos = (w1 - 150, h1 - 120)
                turn_page_backward_text_pos = (w1 - 137, h1 - 110)
                log_window.blit(turn_page_backward_botton, turn_page_backward_botton_pos)
                log_window.blit(turn_page_backward_text, turn_page_backward_text_pos)
                turn_page_backward_text_area = turn_page_backward_text.get_rect(
                    center=(turn_page_backward_text_pos[0] + turn_page_backward_text.get_size()[0] / 2, \
                            turn_page_backward_text_pos[1] + turn_page_backward_text.get_size()[1] / 2))
                while True:
                    quit_log = False
                    for event in pygame.event.get():
                        if event.type == QUIT:  # 若检测到事件类型为退出，则退出log
                            quit_log = True
                            # 重现主界面
                            window = pygame.display.set_mode((w, h), 0, 0)
                            pygame.display.set_caption("py三国杀")
                            window.blit(background, (0, 0))
                            window.blit(logo, (510, 150))
                            window.blit(button, (630, 500))
                            window.blit(button, (630, 600))
                            window.blit(text1, text1_pos)
                            window.blit(text2, text2_pos)
                            break
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            if turn_page_forward_text_area.collidepoint(event.pos):
                                page += 1
                                log_window.fill((255, 255, 255))
                                log_window.blit(log_background, (0, 0))
                                show_log_page('log.txt', page, h1 / font_log_size, font_log_size)
                                log_window.blit(turn_page_forward_botton, turn_page_forward_botton_pos)
                                log_window.blit(turn_page_forward_text, turn_page_forward_text_pos)
                                log_window.blit(turn_page_backward_botton, turn_page_backward_botton_pos)
                                log_window.blit(turn_page_backward_text, turn_page_backward_text_pos)
                            if turn_page_backward_text_area.collidepoint(event.pos):
                                page -= 1
                                log_window.fill((255, 255, 255))
                                log_window.blit(log_background, (0, 0))
                                show_log_page('log.txt', page, h1 / font_log_size, font_log_size)
                                log_window.blit(turn_page_forward_botton, turn_page_forward_botton_pos)
                                log_window.blit(turn_page_forward_text, turn_page_forward_text_pos)
                                log_window.blit(turn_page_backward_botton, turn_page_backward_botton_pos)
                                log_window.blit(turn_page_backward_text, turn_page_backward_text_pos)
                        pygame.display.update()
                    if quit_log:
                        break

            pygame.display.update()
        if begin:
            game(window, w, h)  # 正式开始
            window = pygame.display.set_mode((w, h), 0, 0)
            pygame.display.set_caption("py三国杀")
            window.blit(background, (0, 0))
            window.blit(logo, (510, 150))
            window.blit(button, (630, 500))
            window.blit(button, (630, 600))
            window.blit(text1, text1_pos)
            window.blit(text2, text2_pos)

