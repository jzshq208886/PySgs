import os
import pygame.mixer
from pygame import font
from lib import mode
from handle import *


# 颜色
class Color:
    black = (0, 0, 0)
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    yellow = (255, 255, 0)
    lightBlue = (0, 255, 255)
    lightOrange = (255, 212, 152)
    grey = (200, 200, 200)
    white = (255, 255, 255)



class Block:
    def __init__(self, ui, coordinate):
        self.ui = ui
        self.coordinate = coordinate
        self.elements = dict()

    @property
    def rect(self):
        if 'background' in self.elements:
            return self.elements['background'].get_rect()
        return [0, 0, 0, 0]

    def addElement(self, elemName, image, coordinate):
        if type(image) is str:
            image = self.ui.image[image]
        self.elements[elemName] = (image, coordinate)

    def layout(self):
        for key in self.elements:
            coordinate = self.elements[key][1]
            self.ui.window.blit(self.elements[key][0], (coordinate[0]+self.coordinate[0], coordinate[1]+self.coordinate[1]))


class Clock(Block):
    def __init__(self, ui, coordinate, time):
        super().__init__(ui, coordinate)
        self.time = time
        self.counter = 0
        self.onRemove = None

    def forward(self):
        self.counter += 1

    def isFinished(self):
        return self.counter >= self.time


class Control:
    def __init__(self, ui, text, text_grey, background, background_grey, name):
        self.__name = name
        self.__ui = ui
        self.__text = text
        self.__text_grey = text_grey
        self.__background = background
        self.__background_grey = background_grey
        self.__rect = background.get_rect()
        self.__textRect = text.get_rect()
        self.__show = True
        self.__clickable = True

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def rect(self):
        return self.__rect

    @property
    def textRect(self):
        return self.__textRect

    @property
    def center(self):
        return self.__rect.center

    @center.setter
    def center(self, value):
        if self.__rect[2] == 200:
            self.__rect.center = (value[0], value[1] + 1)
            self.__textRect.center = (value[0] - 1, value[1] - 2)

        else:
            self.__rect.center = value
            self.__textRect.center = (value[0] + 1, value[1] - 2)

    @property
    def clickable(self):
        return self.__clickable

    @clickable.setter
    def clickable(self, value):
        self.__clickable = value

    def blit(self):
        window = self.__ui.window
        if self.__clickable:
            window.blit(self.__background, self.__rect)
            window.blit(self.__text, self.__textRect)
        else:
            window.blit(self.__background_grey, self.__rect)
            window.blit(self.__text_grey, self.__textRect)
        # windowSize = self.__ui.windowSize
        # if self.__clickable:
        #     window.blit(self.__background, self.__rect)
        #     window.blit(self.__text, (0, 0))
        # else:
        #     window.blit(self.__background_grey, self.__rect)
        #     window.blit(self.__text_grey, self.__textRect)


class Movement:
    def __init__(self, origin, destination, time=1, visible=True):
        self.__object = None
        self.__origin = origin
        self.__destination = destination
        self.__visible = visible
        self.__vx = (self.__destination[0] - self.__origin[0]) / time
        self.__vy = (self.__destination[1] - self.__origin[1]) / time
        self.__coordinate = [origin[0], origin[1]]

    @property
    def object(self):
        return self.__object

    @object.setter
    def object(self, value):
        self.__object = value

    @property
    def visible(self):
        return self.__visible

    @property
    def coordinate(self):
        return self.__coordinate

    @property
    def finished(self):
        return (self.__coordinate[0] - self.__destination[0]) * (self.__coordinate[0] - self.__origin[0]) > 0 \
               or (self.__coordinate[0] - self.__destination[0]) * (self.__coordinate[0] - self.__origin[0]) > 0

    def move(self):
        self.__coordinate[0] += self.__vx
        self.__coordinate[1] += self.__vy


class Video:
    def __init__(self, frames=None, interval=None):
        self.coordinate = (0, 0)
        self.frames = [] if frames is None else frames
        self.interval = 12 if interval is None else interval
        self.progress = 0
        self.counter = 0

    @property
    def length(self):
        if type(self.interval) is int:
            return self.interval * len(self.frames)
        if type(self.interval) is list:
            return sum(self.interval)
        print('Warning: Video.interval is neither int nor list.')
        return len(self.frames)

    def forward(self):
        self.counter += 1
        if self.counter > self.interval:
            self.progress += 1
            self.counter = 0

    def isFinished(self):
        return self.progress >= len(self.frames)


class Layer:
    def __init__(self, ui):
        self.ui = ui
        self.blocks = {'general': []}
        self.clocks = {'general': []}
        self.videos = {'general': []}
        self.movements = {'general': []}
        self.controls = {'general': []}

    def addClock(self, clock, name: str = None):
        if name:
            self.clocks[name] = clock
        else:
            self.clocks['general'].append(clock)

    def layout(self):
        # Block和Clock
        for key in self.blocks:
            if type(self.blocks[key]) is list:
                for block in self.blocks[key]:
                    block.layout()
            elif type(self.blocks[key]) is Block:
                self.blocks[key].layout()

        for key in self.clocks:
            if type(self.clocks[key]) is list:
                for clock in self.clocks[key]:
                    clock.layout()
            elif type(self.clocks[key]) is Clock:
                self.clocks[key].layout()

        pass

    def forward(self):
        for key in self.clocks:
            if type(self.clocks[key]) is list:
                for clock in self.clocks[key]:
                    clock.counter += 1
                    if clock.isFinished():
                        self.clocks[key].remove(clock)
            elif type(self.clocks[key]) is Clock:
                self.clocks[key].counter += 1
                if self.clocks[key].isFinished():
                    self.clocks.pop(key)
        pass


class UI:
    def __init__(self, window, player):
        self.room = player.room
        self.__status = None
        self.__window = window
        self.__windowSize = (0, 0)
        self.__rect = {}

        self.__image = dict()
        self.__font = dict()
        self.__audio = dict()
        self.__text = dict()
        self.__block = {}
        self.__timedBlock = dict()
        self.clock = {}
        self.__commonClock = {
            "handling": dict(), "handcards": dict(), "draw": dict(), "damage": dict(),
            'recover': dict(), "gameStart": 0
        }
        self.__commonClockContent = {
            "handcards": dict(), "draw": dict(), "damage": dict(), 'recover': dict()
        }
        self.__controls = []
        self.__basicControl = {}
        self.__movements = {}
        self.videos = {}
        self.playing = []
        self.layers = {}

        self.__originCoors = []
        self.__handling = []
        self.__handlingInfo = {}
        self.__stayHandling = set()
        self.__fading = set()
        self.__players = self.room.players
        self.playerCoordinates = {}
        self.__me = player

        self.__clickable = dict()
        self.__tran = None

    @property
    def window(self):
        return self.__window

    @property
    def windowSize(self):
        return self.__windowSize

    @windowSize.setter
    def windowSize(self, size):
        self.__windowSize = size

    @property
    def image(self):
        return self.__image

    @property
    def audio(self):
        return self.__audio

    @property
    def commonClock(self):
        return self.__commonClock

    @property
    def commonClockContent(self):
        return self.__commonClockContent

    @property
    def controls(self):
        return self.__controls

    @controls.setter
    def controls(self, value):
        self.__controls = value

    @property
    def originCoors(self):
        return self.__originCoors

    @originCoors.setter
    def originCoors(self, coors):
        if type(coors) is not list:
            coors = [coors]
        self.__originCoors = coors

    @property
    def me(self):
        return self.__me

    @me.setter
    def me(self, player):
        self.__me = player

    @property
    def handlingInfo(self):
        return self.__handlingInfo

    def createText(self, text, font=None, color=(0, 0, 0), antialias=True):
        if font is None:
            font = "default"
        if type(font) is str:
            font = self.__font[font]
        return font.render(text, antialias, color)

    def createBlock(self):
        pass

    def createControl(self, text, background='button2', name='generalControl'):
        text_grey = self.createText(text, 'ATLL', Color.grey)
        text = self.createText(text, 'ATLL', Color.lightOrange)
        background_grey = self.__image[background + '_grey']
        background = self.__image[background]
        return Control(self, text, text_grey, background, background_grey, name)

    def initialize(self):
        self.__status = self.room.status
        self.__tran = self.room.translateTable

        # 加载字体
        self.loadFont("default", font.Font("fonts/HYZLSJ.TTF", 35))
        self.loadFont("big", font.Font("fonts/FZLBJW.TTF", 42))
        self.loadFont("biiig", font.Font("fonts/FZLBJW.TTF", 95))
        self.loadFont("small", font.Font("fonts/HYZLSJ.TTF", 25))
        self.loadFont("ATLL", font.Font("fonts/ATLL.OTF", 42))
        # self.loadFont("huangcao", font.Font('fonts/huangcao.ttf', 42))
        # self.loadFont("libian", font.Font('fonts/shousha.ttf', 42))
        # self.loadFont("xiaozhuan", font.Font('fonts/xiaozhuan.ttf', 42))
        # self.loadFont("xingkai", font.Font('fonts/xingkai.ttf', 42))
        self.loadFont("xinwei", font.Font('fonts/xinwei.ttf', 42))
        # self.loadFont("yuanli", font.Font('fonts/yuanli.ttf', 42))
        # room.loadFont("default", font.Font("C:/Windows/Fonts/STXINWEI.TTF", 25))
        # room.loadFont("big", font.Font("C:/Windows/Fonts/STXINWEI.TTF", 45))

        # 加载图像
        self.loadImage("background", "image/game/background.jpg")
        self.loadImage("menu", "image/game/menu.png")
        self.loadImage("cardBack", "image/game/cardback.png")
        self.loadImage("button1", "image/game/interface/button1.png")
        self.loadImage("button1_grey", "image/game/interface/button1_grey.png")
        self.loadImage("button2", "image/game/interface/button2.png")
        self.loadImage("button2_grey", "image/game/interface/button2_grey.png")
        self.loadImage("button3", "image/game/interface/button3.png")
        self.loadImage("button3_grey", "image/game/interface/button3_grey.png")

        self.loadImage("cardSelected", 'image/game/box/cardSelected.png')
        self.loadImage("targetSelected", 'image/game/box/targetSelected.png')

        # determine = Block(self, 'determine', (
        #     self.__windowSize[0] * 0.42 - 85, self.__windowSize[1] - 275), size=self.__image['button1'].get_rect()[2:])
        # determine.addElement('button1', (0, 0))
        # determine.addElement('button1_grey', (0, 0))
        # determine.addElement('text_determine', (0.28, 0.1), Text(self, '确定', self.__font['ATLL'], (255, 212, 152)))
        # determine.addElement('text_determine_grey', (0.28, 0.1), Text(self, '确定', self.__font['ATLL'], (200, 200, 200)))
        # self.__block['determine'] = determine
        #
        # cancel = Block(self, 'cancel', (
        #     self.__windowSize[0] * 0.58 - 85, self.__windowSize[1] - 275), 'button2', self.__image['button2'].get_rect()[2:])
        # cancel.addElement('text_cancel', (0.23, 0.12), Text(self, '取消', self.__font['ATLL'], (255, 220, 150)))
        # cancel.addElement('text_cancel_grey', (0.23, 0.12), Text(self, '取消', self.__font['ATLL'], (200, 200, 200)))
        # cancel.addElement('text_end', (0.23, 0.12), Text(self, '结束', self.__font['ATLL'], (255, 220, 150)))
        # cancel.addElement('text_end_grey', (0.23, 0.12), Text(self, '结束', self.__font['ATLL'], (200, 200, 200)))
        # self.__block['cancel'] = cancel

        self.loadImage("frame_qun", "image/game/qun.png")
        self.loadImage("frame_wei", "image/game/wei.png")
        self.loadImage("frame_shu", "image/game/shu.png")
        self.loadImage("frame_wu", "image/game/wu.png")
        self.loadImage("frame_jin", "image/game/jin.png")
        self.loadImage("frame_shen", "image/game/shen.png")

        self.loadImage("identity_cai", "image/game/decoration/identity_cai.png")
        self.loadImage("identity_zhu", "image/game/decoration/identity_zhu.png")
        self.loadImage("identity_zhong", "image/game/decoration/identity_zhong.png")
        self.loadImage("identity_fan", "image/game/decoration/identity_fan.png")
        self.loadImage("identity_nei", "image/game/decoration/identity_nei.png")

        self.loadImage("hp_high", "image/game/hp/high.png")
        self.loadImage("hp_middle", "image/game/hp/middle.png")
        self.loadImage("hp_low", "image/game/hp/low.png")
        self.loadImage("hp_lost", "image/game/hp/lost.png")
        self.loadImage("cardCount", "image/game/decoration/card_count.png")

        self.loadImage("dead_zhu", "image/game/dead/dead_zhu.png")
        self.loadImage("dead_zhong", "image/game/dead/dead_zhong.png")
        self.loadImage("dead_fan", "image/game/dead/dead_fan.png")
        self.loadImage("dead_nei", "image/game/dead/dead_nei.png")

        self.loadImage("heart", "image/card/suit/heart.png")
        self.loadImage("diamond", "image/card/suit/diamond.png")
        self.loadImage("spade", "image/card/suit/spade.png")
        self.loadImage("club", "image/card/suit/club.png")

        for i in range(13):
            self.loadImage(str(i + 1) + "_red", "image/card/number/red/" + str(i + 1) + ".png")
            self.loadImage(str(i + 1) + "_black", "image/card/number/black/" + str(i + 1) + ".png")

        self.loadImage("unknown_card", "image/card/unknown_card.png")
        self.loadInPile()
        self.loadEquipTitle()

        rect = self.__image[mode.modes['identity']['inPile']['basic'][0]].get_rect()
        self.__rect['card'] = rect
        shadow_card = pygame.Surface((rect[2], rect[3]))
        shadow_card.convert_alpha()
        shadow_card.set_alpha(100)
        shadow_card.fill((*Color.black, 15))
        self.__image["shadow_card"] = shadow_card

        rect = self.__image['frame_qun'].get_rect()
        self.__rect['player'] = rect
        shadow_target = pygame.Surface((rect[2] * 0.98, rect[3] * 0.98))
        shadow_target.convert_alpha()
        shadow_target.set_alpha(200)
        shadow_target.fill((*Color.black, 15))
        self.__image["shadow_target"] = shadow_target

        zuijiu = pygame.Surface((rect[2] * 0.83, rect[3] * 0.98))
        zuijiu.convert_alpha()
        zuijiu.set_alpha(60)
        zuijiu.fill((*Color.red, 15))
        self.__image["zuijiu"] = zuijiu

        dialog = pygame.Surface((900, 500))
        dialog.convert_alpha()
        dialog.set_alpha(180)
        dialog.fill((*Color.black, 15))
        self.__image["dialog"] = dialog

        # 加载音频
        self.loadAudio('gameStart', 'audio/game_start.mp3')
        self.loadAudio('damage', 'audio/event/damage.mp3')
        self.loadAudio('recover', 'audio/event/recover.mp3')
        self.loadAudio('equip1', 'audio/event/equip1.mp3')
        self.loadAudio('equip2', 'audio/event/equip2.mp3')
        self.loadAudio('equip3', 'audio/event/equip3.mp3')
        self.loadAudio('win', 'audio/event/win.mp3')

        # 临时
        self.loadAudio('jianxiong1', 'audio/skill/jianxiong1.mp3')
        self.loadAudio('jianxiong2', 'audio/skill/jianxiong2.mp3')
        self.loadAudio('caocao_die', 'audio/die/caocao.mp3')
        self.loadAudio('huangyueying_die', 'audio/die/huangyueying.mp3')

        # 创建基础按钮
        determine = self.createControl('确定', 'button1', 'determine')
        determine.center = (self.__windowSize[0] * 0.43, self.__windowSize[1]*0.686)
        self.__basicControl['determine'] = determine

        cancel = self.createControl('取消', name='cancel')
        cancel.center = (self.__windowSize[0] * 0.572, self.__windowSize[1]*0.686)
        self.__basicControl['cancel'] = cancel

        cancel2 = self.createControl('结束', name='cancel')
        cancel2.center = (self.__windowSize[0] * 0.572, self.__windowSize[1]*0.686)
        self.__basicControl['cancel2'] = cancel2

        # 玩家定位
        self.playerLocate()

    def loadInPile(self, inPile: dict = None, path=''):
        if inPile is None:
            inPile = mode.modes['identity']['inPile']
        if path and not path[-1] == '/':
            path += '/'

        for cardtype in inPile:
            if type(inPile[cardtype]) is dict:
                self.loadInPile(inPile[cardtype], path)
            elif type(inPile[cardtype]) is list:
                for cardName in inPile[cardtype]:
                    self.loadImage(cardName, path + "image/card/" + cardName + ".png")
                    self.loadAudio(cardName + '_male', path + 'audio/card/male/' + cardName + '.mp3')
                    self.loadAudio(cardName + '_female', path + 'audio/card/female/' + cardName + '.mp3')
                    if cardName == 'sha':
                        for nature in mode.modes['identity']['inPile_nature']:
                            self.loadImage(cardName + '_' + nature,
                                           path + "image/card/" + cardName + '_' + nature + ".png")
                            self.loadAudio(cardName + '_' + nature + '_male',
                                           path + 'audio/card/male/' + cardName + '_' + nature + '.mp3')
                            self.loadAudio(cardName + '_' + nature + '_female',
                                           path + 'audio/card/female/' + cardName + '_' + nature + '.mp3')

    def loadEquipTitle(self, inPile: dict = None, path=''):
        if inPile is None:
            inPile = mode.modes['identity']['inPile']
        if path and not path[-1] == '/':
            path += '/'

        for equipType in inPile['equip']:
            for cardName in inPile['equip'][equipType]:
                self.loadImage(cardName + 'Title', path + "image/card/equipTitle/" + cardName + '.png')

    def playerLocate(self):
        ws, rect, me = self.__windowSize, self.__image['frame_qun'].get_rect(), self.__me
        self.playerCoordinates[me] = (ws[0] - rect[2] - 10, ws[1] - rect[3] - 10)
        others = self.__players.copy()
        seat = self.__players.index(me)
        others = others[:seat][::-1] + others[seat + 1:]  # 按屏幕顺序排列
        others.reverse()
        for i in range(len(others)):
            self.playerCoordinates[others[i]] = (
                10 + (i + 1) * (self.__windowSize[0] - 20) / (len(others) + 1) - rect[2] / 2, 10)

    def loadImage(self, name, imagePath):
        if os.path.isfile(imagePath):
            self.__image[name] = pygame.image.load(imagePath).convert_alpha()
        else:
            print('Temp Warning: No file', imagePath, 'found!')

    def loadFont(self, name, font):
        self.__font[name] = font

    def loadAudio(self, name, audioPath):
        if os.path.isfile(audioPath):
            self.__audio[name] = pygame.mixer.Sound(audioPath)
        else:
            print('Temp Warning: No file', audioPath, 'found!')
        # self.__audio[name].set_volume(0.5)

    def getLayer(self, num=-1):
        if num < -1:
            num = -1
        if num not in self.layers:
            self.layers[num] = Layer(self)
        return self.layers[num]

    def blit(self, name, position):
        self.__window.blit(self.__image[name], position)

    def blitText(self, text, coordinate, color=(0, 0, 0), font=None, a=True):
        if type(text) is str:
            if font is None:
                font = "default"
            if type(font) is str:
                font = self.__font[font]
            text = font.render(text, a, color)
            rect = text.get_rect()
            if type(coordinate) is str:
                if coordinate == 'center':
                    coordinate = [(self.__windowSize[0] - rect[2]) / 2, (self.__windowSize[1] - rect[3]) / 2]
            else:
                if coordinate[0] == 'center':
                    coordinate[0] = (self.__windowSize[0] - rect[2]) / 2
                if coordinate[1] == 'center':
                    coordinate = (self.__windowSize[1] - rect[3]) / 2
            self.__window.blit(text, coordinate)

    def playAudio(self, name):
        # self.__audio[name].play()
        if name in self.__audio:
            self.__audio[name].play()
        else:
            pass
            # print('Warning: No audio named \"' + name + "\"!")

    def playVideo(self, video, coordinate):
        if type(video) is str:
            video = Video(self.videos[video].frames.copy(), self.videos[video].interval)
        elif type(video) is not Video:
            print('Warning: UI.playVideo(video): \"video\" is not a Video or video name')
            return
        video.coordinate = coordinate[:]
        self.playing.append(video)

    def addClock(self, clock, coordinate=None, layer: int = -1, name: str = None):
        if coordinate is None:
            coordinate = (0, 0)
        if type(clock) is str:
            image = clock
            clock = Clock(self, coordinate, time)
            clock.addElement('background', image, (0, 0))
            clock.coordinate = coordinate
            clock.time = time
        elif type(clock) is not Clock:
            pass  # 直接传入图片情况
        self.getLayer(layer).addClock(clock, name)

    def setClock(self, image, coordinate, time):
        clock = Clock(self, coordinate, time)
        clock.addElement('background', image, (0, 0))
        clock.coordinate = coordinate
        clock.time = time
        self.clock[image] = clock

    def getCommonClock(self, name=None):
        if name:
            return self.__commonClock[name]
        return self.__commonClock

    def setCommonClock(self, name, num, index=None):
        if index is not None:
            self.__commonClock[name][str(index)] = num
        else:
            self.__commonClock[name] = num

    def setCommonClockContent(self, key, content, index=None):
        if index is None:
            self.__commonClockContent[key] = content
        else:
            self.__commonClockContent[key][str(index)] = content

    def clockDecrease(self):
        for key in self.__commonClock:
            if type(self.__commonClock[key]) is int:
                if self.__commonClock[key] > 0:
                    self.__commonClock[key] -= 1
            else:
                handlingToRemove = []
                for key2 in self.__commonClock[key]:
                    if self.__commonClock[key][key2] > 0:
                        self.__commonClock[key][key2] -= 1
                    if key == 'handling' and self.__commonClock[key][key2] == 0:
                        if key2 in self.__fading:
                            handlingToRemove.append(key2)
                        elif key2 not in self.__stayHandling:
                            # for i in range(len(self.__handling)-1, -1):
                            #     pass
                            self.setFadingClock(key2)
                self.removeHandling(handlingToRemove)

        for key in self.clock.copy():
            self.clock[key].counter += 1
            if self.clock[key].isFinished():
                self.clock.pop(key)

        for layer in self.layers:
            self.layers[layer].forward()

    def setControls(self, pattern):
        if type(pattern) is list:
            self.__controls = pattern
        elif pattern == 'phaseUse':
            self.__controls = [self.__basicControl['determine'], self.__basicControl['cancel2']]
        elif pattern == 'choose':
            self.__controls = [self.__basicControl['determine'], self.__basicControl['cancel']]

    # def clickable(self, arg: str = None):
    #     if arg is None:
    #         return self.__clickable
    #     return self.__clickable[arg]

    def isClickable(self, arg: str):
        if arg not in self.__basicControl:
            return False
        return self.__basicControl[arg].clickable

    def setClickable(self, arg: str, clickable: bool):
        if arg not in self.__basicControl:
            return
        self.__basicControl[arg].clickable = clickable
        if arg == 'cancel':
            self.__basicControl['cancel2'].clickable = clickable
            # self.__clickable[arg] = clickable

    def setOriginCoors(self, cards):
        if type(cards) is not list:
            cards = [cards]
        self.__originCoors = [self.getCoordinate(card) for card in cards]

    def setMovement(self, element, origin, destination, time=50, visible=True):
        rect = self.__rect['card']
        if type(origin) is int:
            origin = self.__originCoors[origin]
        if origin == 'screen_center':
            origin = ((self.__windowSize[0] - rect[1]) / 2, (self.__windowSize[1] - rect[2]) / 2)
        if destination == 'screen_center':
            destination = ((self.__windowSize[0] - rect[1]) / 2, (self.__windowSize[1] - rect[2]) / 2)
        self.__movements[element] = Movement(origin, destination, time, visible)
        # print(self.__movements[element])

    def isMoving(self, element):
        if element in self.__movements:
            return self.__movements[element]
        return None

    def move(self):
        for key in self.__movements.copy():
            movement = self.__movements[key]
            movement.move()
            if movement.finished:
                self.__movements.pop(key)

    def layout(self):
        room = self.room

        # 游戏基础
        self.blit("background", (0, 0))
        self.blit("menu", (1356, 0))
        self.blit("cardBack", (1270, 10))
        self.blitText(str(room.drawPile.length), (1283, 22), color=Color.white, font="xinwei")

        # 武将信息
        for player in self.room.allPlayers:
            self.layoutPlayer(player)

        # 结算区的牌
        cards = self.__handling
        for card in cards:
            coordinate = self.getCoordinate(card)  # [iniPosi[0] + i * 152, iniPosi[1]]
            self.layoutCard(card, coordinate)
            if card in self.__handlingInfo:
                self.blitText(self.__handlingInfo[card], (coordinate[0] + 35, coordinate[1] + 130), Color.red, 'small')
            if card in self.__fading:
                self.blit('shadow_card', coordinate)

        # 操作接口展示
        me = self.__me
        # 我的手牌
        myHc = me.getCards('h')
        for i in range(len(myHc)):
            if not self.isMoving(myHc[i]):
                self.layoutCard(myHc[i])

        # 技能
        skills = me.skill
        for i in range(len(skills)):
            if skills[i].skillType == 'trigger' and skills[i].isSkill and not skills[i].equipSkill:
                self.blitText(self.translate(skills[i].name), (1200, 725 - 40 * i), (255, 255, 180), 'default')

        # 按钮显示
        # if me.choosing:
        #     if self.__clickable['determine']:
        #         self.__block['determine'].showElement('button1', 'text_determine')
        #         self.__block['determine'].hideElement('button1_grey', 'text_determine_grey')
        #     else:
        #         self.__block['determine'].showElement('button1_grey', 'text_determine_grey')
        #         self.__block['determine'].hideElement('button1', 'text_determine')
        #     self.displayBlock('determine')
        #
        #     if self.__status.currentEvent.getParent(2).name == 'phaseUse':
        #         if self.__clickable['cancel']:
        #             self.__block['cancel'].showElement('text_end').hideElement('text_end_grey', 'text_cancel',
        #                                                                        'text_cancel_grey')
        #         else:
        #             self.__block['cancel'].showElement('text_end_grey').hideElement('text_end', 'text_cancel',
        #                                                                             'text_cancel_grey')
        #     else:
        #         if self.__clickable['cancel']:
        #             self.__block['cancel'].showElement('text_cancel').hideElement('text_cancel_grey', 'text_end',
        #                                                                           'text_end_gray')
        #         else:
        #             self.__block['cancel'].showElement('text_cancel_grey').hideElement('text_cancel', 'text_end',
        #                                                                                'text_end_grey')
        #     self.displayBlock('cancel')
        if me.choosing:
            for control in self.__controls:
                control.blit()

        # 提示语
        if me.choosing:
            self.blitText(me.getStatus().currentEvent.prompt, ['center', 0.61 * self.__windowSize[1]], font='small')

        # 正在移动的对象
        for card in self.__movements:
            movement = self.__movements[card]
            if movement.visible:
                self.layoutCard(card, movement.coordinate)
            else:
                self.blit("unknown_card", movement.coordinate)

        # Block和Clock
        for key in self.clock:
            self.clock[key].layout()

        # 帧动画
        for video in self.playing.copy():
            self.blit(video.frames[video.progress], video.coordinate)
            video.forward()
            if video.isFinished():
                self.playing.remove(video)

        # 重大事件
        if self.__commonClock["gameStart"]:
            self.blitText("游戏开始！", (550, 350), font="biiig")

        result = room.result
        if result['gameOver']:
            if result['winnerTeam'] is None:
                self.blitText("平局！", 'center', Color.green, "biiig")
            elif me in result['winner']:
                self.blitText("胜利！", 'center', Color.red, "biiig")
            else:
                self.blitText("败北！", 'center', Color.blue, "biiig")

        # 上层显示
        for layer in self.layers:
            self.layers[layer].layout()

    def translate(self, name):
        info = name.split("_")
        sub = ""
        if info[0] == "re":
            sub = "界"
        return sub + self.__tran[info[-1]]

    def display(self):
        self.layout()
        pygame.display.update()

    def layoutBlock(self, name):
        self.__block[name].blit()

    def layoutCard(self, card, position=None):
        if position is None:
            position = self.getCoordinate(card)
        position = list(position).copy()

        if self.isMoving(card):
            position = self.__movements[card].coordinate

        rect = self.__rect['card']
        me = self.__me
        if card in me.selected('card'):
            position[1] -= 30
            self.blit('cardSelected', (position[0] - 0.058 * rect[2], position[1] - 0.058 * rect[3]))

        if card.name == 'blankCard':
            print()

        self.blit(card.name + (('_' + card.nature) if card.nature else ''), (position[0], position[1]))
        if card.suit != "none":
            self.blit(card.suit, (position[0] + 0.062 * rect[2], position[1] + 0.17 * rect[3]))
        if 1 <= card.number <= 13:
            self.blit(str(card.number) + ("_red" if card.getColor() == 'red' else "_black"),
                      (position[0] + 0.06 * rect[2], position[1] + 0.04 * rect[2]))

        if card in self.__fading or me.choosing and card in me.getCards('hes') \
                and card not in me.selectable('card') and card not in me.selected('card'):
            self.blit('shadow_card', position)

    def layoutPlayer(self, player, position: list = None):
        if position is None:
            position = list(self.getCoordinate(player)).copy()
        me = self.__me
        rect = self.__rect['player']

        # 框架，姓名与皮肤
        if player in me.selected('target'):
            self.blit('targetSelected', (position[0] - 13, position[1] - 15))
        self.blit("frame_" + player.kingdom, (position[0], position[1]))
        if player.name:
            name = self.translate(player.name)
            if player.skin:
                self.blit(player.name + '_' + player.skin, (position[0] + 35, position[1] + 6))
            for i in range(len(name)):
                self.blitText(name[i], (position[0] + 6, position[1] + 40 + i * 25), font="small")

        if player.isAlive():
            # 酒状态的红色显示
            if player.hasSkill('zuijiu'):
                self.blit('zuijiu', (position[0] + 0.17 * rect[2], position[1] + 0.01 * rect[3]))

            # 体力值
            X, firstY = 6, 238
            for i in range(player.hp):
                if player.hp < player.maxHp * 0.34:
                    self.blit("hp_low", (position[0] + X, position[1] + firstY - i * 25))
                elif player.hp < player.maxHp * 0.67:
                    self.blit("hp_middle", (position[0] + X, position[1] + firstY - i * 25))
                else:
                    self.blit("hp_high", (position[0] + X, position[1] + firstY - i * 25))
            for i in range(min(player.maxHp - player.hp, player.maxHp)):
                self.blit("hp_lost", (position[0] + X, position[1] + firstY - (player.maxHp - i - 1) * 25))

            # 手牌数
            self.blit("cardCount", (position[0] + 168, position[1] + 231))
            self.blitText(str(player.handcardNum), (position[0] + 179, position[1] + 234), Color.white)

            # 装备显示
            weapon, armor, defendHorse, attackHorce = player.getEquip('weapon'), player.getEquip(
                'armor'), player.getEquip(
                'defendHorse'), player.getEquip('attackHorse')
            if weapon:
                self.blit(weapon.name + "Title", (position[0] + 50, position[1] + 135))
            if armor:
                self.blit(armor.name + "Title", (position[0] + 50, position[1] + 160))
            if defendHorse:
                self.blit(defendHorse.name + "Title", (position[0] + 50, position[1] + 185))
            if attackHorce:
                self.blit(attackHorce.name + "Title", (position[0] + 50, position[1] + 210))

            # 选择目标时的阴影显示
            if len(me.selectable('target')):
                if me.choosingTarget \
                        and player not in me.selectable('target') and player not in me.selected('target'):
                    self.blit('shadow_target', (position[0] + 0.01 * rect[2], position[1] + 0.01 * rect[3]))
        else:
            # 死亡显示
            self.blit('shadow_target', (position[0] + 0.01 * rect[2], position[1] + 0.01 * rect[3]))
            self.blit('dead_' + player.identity, (position[0] + 0.24 * rect[2], position[1] + 0.08 * rect[3]))

        # 身份标识
        self.blit('identity_' + player.identity, (position[0] + 0.825 * rect[2], position[1] - 0.005 * rect[3]))

        # 伤害显示
        if player in self.__commonClock["damage"] and self.__commonClock["damage"][player]:
            self.blitText(self.__commonClockContent["damage"][player],
                          (position[0] + rect[2] * 0.28, position[1] + rect[3] * 0.3), Color.red, "biiig")

        # 回复显示
        if player in self.__commonClock["recover"] and self.__commonClock["recover"][player]:
            self.blitText(self.__commonClockContent["recover"][player],
                          (position[0] + rect[2] * 0.28, position[1] + rect[3] * 0.3), Color.green, "biiig")

    def getCoordinate(self, item):
        if not item.itemType:
            return
        windowSize = self.__windowSize
        if item.itemType == 'card':
            rect = self.__rect['card']
            if item.owner == self.__me:
                if item.position == 'e' or item.position == 'j':
                    return self.getCoordinate(item.owner)
                cards = item.area.cards
                for i in range(len(cards)):
                    if cards[i] == item:
                        return 10 + i * (rect[2] + 1), windowSize[1] - rect[3] - 10
            elif item.owner:
                coordinate = self.playerCoordinates[item.owner]
                return coordinate[0] + 44, coordinate[1] + 50
            elif item in self.__handling:
                length = len(self.__handling)
                for i in range(length):
                    if self.__handling[i] == item:
                        return (windowSize[0] - length * (rect[2] + 2)) / 2 + i * (rect[2] + 2), (
                                    windowSize[1] - rect[3]) / 2.1
            return (windowSize[0] - rect[2]) / 2, (windowSize[1] - rect[3]) / 2
        if item.itemType == 'player':
            if item in self.playerCoordinates:
                return self.playerCoordinates[item]
            return

    def delay(self, t):
        while t:
            if self.room.result['gameInterrupted']:
                return
            t -= 1
            time.sleep(0.001)
            self.display()
            self.clockDecrease()
            self.move()
            result = clickHandle()
            if type(result) == int:
                self.room.flipSkin(result - 48)
            else:
                x, y = result
                if 1356 <= x <= 1540 and 0 <= y <= 139:
                    self.room.result['gameInterrupted'] = True
            # quitHandle()

    def stop(self):
        while True:
            time.sleep(0.1)
            result = clickHandle()
            if type(result) == int:
                continue
            x, y = result
            if 1356 <= x <= 1540 and 0 <= y <= 139:
                self.room.result['gameInterrupted'] = True
                return

    def waitForClick(self):
        while True:
            time.sleep(0.001)
            self.display()
            self.clockDecrease()
            self.move()
            result = clickHandle()
            if type(result) == int:
                self.room.flipSkin(result - 48)
            else:
                x, y = result
                if x:
                    return x, y

    def waitForChoosing(self):
        while True:
            if not self.__me.isUnderControl():
                pass
            x, y = self.waitForClick()
            if not x:
                continue

            me = self.__me
            rect = self.__rect['card']
            for card in me.selectable('card'):
                a, b = self.getCoordinate(card)
                if a <= x <= a + rect[2] and b <= y <= b + rect[3]:
                    return card

            for card in me.selected('card'):
                a, b = self.getCoordinate(card)
                if a <= x <= a + rect[2] and b - 30 <= y <= b - 30 + rect[3]:
                    return card

            rect = self.__rect['player']
            for target in me.selectable('target'):
                a, b = self.getCoordinate(target)
                if a <= x <= a + rect[2] and b <= y <= b + rect[3]:
                    return target

            for target in me.selected('target'):
                a, b = self.getCoordinate(target)
                if a <= x <= a + rect[2] and b - 30 <= y <= b - 30 + rect[3]:
                    return target

            for control in self.__controls:
                rect = control.rect
                if rect[0] < x < rect[0] + rect[2] and rect[1] < y < rect[1] + rect[3]:
                    if not control.clickable:
                        continue
                    if control.name == 'generalControl':
                        return self.__controls.index(control)
                    return control.name
            # for name in self.__block:
            #     # print(name, ':', self.__clickable[name])
            #     if name in self.__clickable and not self.__clickable[name]:
            #         continue
            #     a, b = self.__block[name].coordinate()
            #     size = self.__block[name].size()
            #     if a <= x <= a + size[0] and b <= y <= b + size[1]:
            #         return name
            if 1356 <= x <= 1540 and 0 <= y <= 139:
                self.room.result['gameInterrupted'] = True
                return 'gameInterrupted'

    def addToHandling(self, cards, remainTime=500, stayHandling=False, info=None):
        if type(cards) is not list:
            cards = [cards]
        for card in cards:
            self.__handling.insert(0, card)
            self.__commonClock['handling'][card] = remainTime
            if stayHandling:
                self.__stayHandling.add(card)
            if info:
                self.__handlingInfo[card] = info

    def removeHandling(self, cards):
        if type(cards) is not list:
            cards = [cards]
        for card in cards:
            if card in self.__handling:
                pass
                self.__handling.remove(card)
                self.__commonClock['handling'].pop(card)
                if card in self.__handlingInfo:
                    self.__handlingInfo.pop(card)
                if card in self.__stayHandling:
                    self.__stayHandling.remove(card)
                if card in self.__fading:
                    self.__fading.remove(card)

    def setHandlingClock(self, cards, num=300):
        if type(cards) is not list:
            cards = [cards]
        for card in cards:
            if card in self.__handling:
                self.__commonClock['handling'][card] = num
                if num < 1000:
                    if card in self.__stayHandling:
                        self.__stayHandling.remove(card)

    def setFadingClock(self, cards, num=300):
        if type(cards) is not list:
            cards = [cards]
        for card in cards:
            if card in self.__handling:
                self.__fading.add(card)
                self.__commonClock['handling'][card] = num


