from ui import *
from player import *
from skills.general import *
from skills.standard import *
from cards.identity import *
from lib import character
# from extensions.bf.cards.bf import *
from lib.translation import translateTable
import random


class Room:
    __itemType = 'room'
    path = ''

    def __init__(self, iniMode, playerNum):
        self.__ui = set()  # UI(window, self)
        self.__status = Status(self)
        self.characters = character.characters
        self.__tran = translateTable

        self.__mode = iniMode
        self.__identityNum = {'zhu': 0, 'zhong': 0, 'fan': 0, 'nei': 0}
        self.playerNum = playerNum
        self.__players = []  # alive players
        self.__allPlayers = []
        self.__currentPhase = None
        # self.__playList = []

        self.__inPile = []
        self.__drawPile = Pile(self)
        self.__discardPile = DiscardPile(self)
        self.__handleArea = HandleArea(self)
        # self.__judgingArea = JudgingArea(self)
        # self.__pindianArea = PindianArea(self)
        self.__globalSkill = []
        self.__turn = 0
        self.__result = {'gameOver': False, 'winnerTeam': None, 'winner': [], 'gameInterrupted': False}
        self.storage = {}

        self.directory = ['']
        self.test = False

    @property
    def itemType(self):
        return self.__itemType

    @property
    def translateTable(self):
        return self.__tran

    @translateTable.setter
    def translateTable(self, value):
        self.__tran = value

    def translate(self, name):
        if type(name) is not str:
            name = name.name
        info = name.split("_")
        sub = ""
        if info[0] == "re":
            sub = "界"
        return sub + self.__tran[info[-1]]

    @property
    def mode(self):
        return self.__mode

    @property
    def ui(self):
        return self.__ui

    @property
    def status(self):
        return self.__status

    @property
    def players(self):
        return self.__players

    @property
    def allPlayers(self):
        return self.__allPlayers

    @allPlayers.setter
    def allPlayers(self, value):
        self.__allPlayers = value

    @property
    def currentPhase(self):
        return self.__currentPhase

    @currentPhase.setter
    def currentPhase(self, value):
        self.__currentPhase = value

    @property
    def result(self):
        return self.__result

    @property
    def inPile(self):
        return self.__inPile

    @inPile.setter
    def inPile(self, value):
        self.__inPile = value

    @property
    def drawPile(self):
        return self.__drawPile

    @property
    def discardPile(self):
        return self.__discardPile

    def getDrawPileNum(self):
        return self.__drawPile.length

    def getDiscardPileNum(self):
        return self.__discardPile.length

    @property
    def handleArea(self):
        return self.__handleArea

    @property
    def globalSkill(self):
        return self.__globalSkill

    def initialize(self, window, w, h):
        # 添加相应数量玩家
        for i in range(self.playerNum):
            playerType = 'ai' if i else 'human'
            self.addPlayer(Player(self, playerType))

        # self.__allPlayers = self.__players.copy()
        for player in self.__players:
            player.initialize()

        # 玩家UI初始化
        for player in self.__players:
            if player.operator == 'ai':
                continue
            # 初始化游戏环境

            screen = window
            ui = UI(screen, player)
            ui.windowSize = (w, h)
            ui.initialize()
            player.ui = ui

        # 添加全局技能
        for skill in mode.modes[self.__mode]['globalSkill']:
            self.addSkill(skill)

    def addSkill(self, name, temp=False):
        for skill in self.__globalSkill:
            if skill.name == name:
                return False

        skill = self.createSkill(name)
        if skill:
            skill.temp = temp
            skill.owner = self
            self.__globalSkill.append(skill)
            skill.initialize()

    def createSkill(self, name):
        if name and name[0].islower:
            name = chr(ord(name[0]) - 32) + name[1:]
        return eval(name)(self.__status)

    def removeSkill(self, name):
        for i in range(len(self.__globalSkill)):
            if self.__globalSkill[i].name == name:
                self.__globalSkill[i].onRemove()
                self.__globalSkill.pop(i)
                break

    def prepare(self):
        # 分配身份与座次
        # self.identityDistribute()
        self.__players[0].identity = 'zhu'
        self.__players[0].seat = 1
        for i in range(1, len(self.__players)):
            self.__players[i].identity = 'fan'
            self.__players[i].seat = i + 1
            self.__players[0].ai.info[self.__players[i]]['identityKnown'] = True
            for player in self.__players:
                if player != self.__players[i]:
                    self.__players[i].ai.info[player]['identityKnown'] = True

        # 选将
        for player in self.__players:
            player.chooseRole()

        # 亮将
        for player in self.__players:
            player.displayChara()

        self.delay(300)
        # 添加卡牌
        cards, nature = mode.modes[self.__mode]['cards'], None
        for card in cards:
            if 'nature' in card[3]:
                nature = card[3]['nature']
            else:
                nature = None
            newCard = self.createCard(card[0], card[1], card[2], nature)
            # self.__drawPile.addCard(newCard)
            self.addCard(newCard)

        self.__inPile = mode.modes[self.__mode]['inPile'].copy()

        # 洗牌
        # self.__drawPile.getCards(), self.__discardPile = self.__discardPile, self.__drawPile
        self.shuffle()

    def addPlayer(self, player: Player, seat=None):
        self.__players.append(player)
        self.__allPlayers.append(player)
        if len(self.__players) > 1:
            player.previous = self.__players[-2]
            player.next = self.__players[0]
            self.__players[-2].next = player
            self.__players[0].previous = player

    def removeDeadPlayer(self, player):
        for i in range(len(self.__players)):
            if self.__players[i] == player:
                player.previous.next = player.next
                player.next.previous = player.previous
                self.__players.pop(i)
                break

    def identityDistribute(self):
        if self.playerNum == 2:
            identities = ['zhu', 'fan']
        pass

    def createCard(self, name, suit=None, number=0, nature=None, existence='real'):
        if name and name[0].islower:
            name = chr(ord(name[0]) - 32) + name[1:]
        newCard = eval(name)(suit, number, nature, existence)
        if not newCard:
            print("\033[0;31;40m" + "Warning: Failed to create card \"" + name + "\"!" + "\033[0m")
        newCard.setStatus(self.__status)
        return newCard

    def addCard(self, card: Card, area=None):
        if area is None:
            area = self.__drawPile
        area.addCard(card, random.randint(0, self.__drawPile.length))

    def getCards(self, num=1, bottom=False):
        if self.__drawPile.length < num:
            if self.__drawPile.length + self.__discardPile.length < num:
                self.result['gameOver'] = True
                self.status.currentEvent.cancel()
                return []
            self.shuffle()
        if bottom:
            cards = self.__drawPile.cards[self.__drawPile.length - num:]
        else:
            cards = self.__drawPile.cards[:num]
        return cards

    def shuffle(self):
        while self.discardPile.length:
            i = random.randint(0, self.discardPile.length - 1)
            card = self.discardPile.cards[i]
            self.moveCardTo(card, 'drawPile', "Reason_Shuffle")

    def flipSkin(self, seat):
        if seat > len(self.__allPlayers) or seat <= 0:
            return
        self.__allPlayers[seat - 1].flipSkin()

    def process(self):
        # 初始摸牌
        for player in self.__players:
            player.startDraw(4)
        for player in self.__players:
            if player.isUnderControl():
                while True:
                    next = player.chooseBool('是否使用手气卡？')
                    self.status.processNext()
                    if next.result('bool'):
                        player.luckyHandcard()
                    else:
                        break

        self.delay(100)
        for player in self.__players:
            if player.isUnderControl():
                player.ui.setCommonClock("gameStart", 300)
                player.ui.playAudio("gameStart")
        self.delay(400)

        current = self.players[0]
        while True:
            current.phase()
            self.status.processNext()
            if self.result['gameOver']:
                self.broadcastAll(lambda ui: self.setUI_gameOver(ui))
                return
            if self.result['gameInterrupted']:
                return
            current = current.next

    def setUI_gameOver(self, ui):
        ui.playAudio('gameStart')
        ui.delay(1)
        ui.stop()

    def targetSort(self, targets: list = None, player: Player = None):
        if not self.__players:
            return []

        if targets is None:
            targets = self.__players.copy()
        else:
            targets = targets.copy()
        if player is None:
            seat = self.__currentPhase.seat if self.__currentPhase else self.__players[0].seat
        else:
            seat = player.seat

        for i in range(1, len(targets)):
            current = targets[i]
            j = i - 1
            # print(targets[j].seat < seat <= current.seat, seat <= current.seat < targets[j].seat, current.seat < targets[j].seat < seat)
            while j > -1 and (
                    targets[j].seat < seat <= current.seat or seat <= current.seat < targets[j].seat or current.seat <
                    targets[j].seat < seat):
                targets[j + 1] = targets[j]
                j -= 1
            targets[j + 1] = current
        return targets

    def judgeResult(self):
        identities = []
        for player in self.__players:
            if player.isAlive() and player.identity not in identities:
                identities.append(player.identity)

        result = self.__result
        if 'zhu' not in identities:
            result['gameOver'] = True
            if len(identities) == 1 and identities[0] == 'nei':
                result['winnerTeam'] = 'nei'
            else:
                result['winnerTeam'] = 'fan'
        elif 'fan' not in identities and 'nei' not in identities:
            result['gameOver'] = True
            result['winnerTeam'] = 'zhu'

        for player in self.__allPlayers:
            if player.identity == result['winnerTeam'] or result['winnerTeam'] == 'zhu' and player.identity == 'zhong':
                self.__result['winner'].append(player)

    def moveCardTo(self, cards, to='d', pattern="defaultPattern", visible=False):
        ui = self.__players[0].ui

        if to == 'd' or to == 'discardPile':
            to = self.__discardPile
        if to == 'r' or to == 'drawPile':
            to = self.__drawPile
        if to == 't' or to == 'handleArea':
            to = self.__handleArea

        if type(cards) is not list:
            cards = [cards]

        cardsNum = len(cards)
        for card in cards:
            card.area.removeCard(card)
        to.addCard(cards)
        if to == self.__handleArea:
            self.broadcastAll(lambda ui: ui.addToHandling(cards, 9999 if pattern == 'use' else 500, pattern == 'use',
                                                          '八卦' if pattern == 'judge' else None))

        if to.owner:
            toPlayer = to.owner
            if toPlayer == ui.me:
                for i in range(cardsNum):
                    ui.setMovement(cards[i], 'screen_center', ui.getCoordinate(cards[i]))
                    # cards[i].setMovement()
                    # ui.setClock("handcards", 4, oriNum + i)

            # elif pattern == "draw" and visible:
            #     ui.setCommonClock("gain", 45, toPlayer.seat())
            # elif not visible:
            #     ui.setCommonClock("draw", 45, toPlayer.seat)
            #     ui.setCommonClockContent("draw", str(cardsNum) if cardsNum > 1 else "", toPlayer.seat)


        ui.delay(1)
        # 时机：moveCard

    def broadcastAll(self, func):
        if not callable(func):
            return
        for ui in self.ui:
            func(ui)

    def delay(self, time=200):
        pass
        for ui in self.ui:
            ui.delay(time)

    def setCommonClock(self, name, num, index=None):
        pass
        for ui in self.ui:
            ui.setCommonClock(name, num, index)

    def setCommonClockContent(self, key, content, index=None):
        pass
        for ui in self.ui:
            ui.setCommonClock(key, content, index)

    def showResult(self):
        self.broadcastAll(lambda ui: ui.blitText(''))


class Status:
    def __init__(self, room):
        self.__room = room
        self.__next = []
        self.__currentEvent = None
        self.__result = {
            'bool': False, 'card': None, 'cards': [], 'target': None, 'targets': []
        }

    @property
    def room(self):
        return self.__room

    @property
    def currentEvent(self):
        return self.__currentEvent

    @currentEvent.setter
    def currentEvent(self, event):
        self.__currentEvent = event

    @property
    def next(self):
        return self.__next

    def clearResult(self):
        self.__result = {'bool': False, 'card': None, 'cards': [], 'target': None, 'targets': []}

    def setResult(self, arg: str, value):
        self.__result[arg] = value

    def createEvent(self, name):
        if name and name[0].islower:
            name = chr(ord(name[0]) - 32) + name[1:]
        return eval(name)(self)

    def addEvent(self, event):
        if type(event) is str:
            event = self.createEvent(event)

        if self.__currentEvent:
            self.__currentEvent.pushNext(event)
        else:
            self.__next.append(event)
        return event

    def processNext(self):
        while len(self.__next):
            self.__next[0].process()
            self.__next.pop(0)

# if len(name) > 6:
        #     if name[-6:] == 'Effect':
        #         if name == 'shaEffect':
        #             return ShaEffect(self)
        #         if name == 'shanEffect':
        #             return ShanEffect(self)
        #         if name == 'jiuEffect':
        #             return JiuEffect(self)
        #         if name == 'taoEffect':
        #             return TaoEffect(self)
        #         if name == 'wuzhongEffect':
        #             return WuzhongEffect(self)
        #         if name == 'juedouEffect':
        #             return JuedouEffect(self)
        #         if name == 'guoheEffect':
        #             return GuoheEffect(self)
        #         if name == 'shunshouEffect':
        #             return ShunshouEffect(self)
        #         if name == 'nanmanEffect':
        #             return NanmanEffect(self)
        #         if name == 'wanjianEffect':
        #             return WanjianEffect(self)
        #         if name == 'tiesuoEffect':
        #             return TiesuoEffect(self)
        #     if name[:6] == 'choose':
        #         if name == 'chooseToUse':
        #             return ChooseToUse(self)
        #         if name == 'chooseToDiscard':
        #             return ChooseToDiscard(self)
        #         if name == 'chooseToInvoke':
        #             return ChooseToInvoke(self)
        #         if name == 'chooseCard':
        #             return ChooseCard(self)
        #         if name == 'chooseCardTarget':
        #             return ChooseCardTarget(self)
        #     if name[-6:] == 'Invoke':
        #         if name == 'updateAIInvoke':
        #             return UpdateAIInvoke(self)
        #         if name == 'onPhaseUseAfterInvoke':
        #             return OnPhaseUseAfterInvoke(self)
        #         if name == 'onPhaseAfterInvoke':
        #             return OnPhaseAfterInvoke(self)
        #         if name == 'zuijiuInvoke':
        #             return ZuijiuInvoke(self)
        #         if name == 'jizhiInvoke':
        #             return JizhiInvoke(self)
        #         if name == 'jianxiongInvoke':
        #             return JianxiongInvoke(self)
        #         if name == 'huodeInvoke':
        #             return HuodeInvoke(self)
        #         if name == 'guanshiSkillInvoke':
        #             return GuanshiSkillInvoke(self)
        #         if name == 'baguaSkillInvoke':
        #             return BaguaSkillInvoke(self)
        #         if name == 'renwangSkillInvoke':
        #             return RenwangSkillInvoke(self)
        # if name == 'trigger':
        #     return Trigger(self)
        # if name == 'phase':
        #     return Phase(self)
        # if name == 'phasePrepare':
        #     # self.getRoom().wait(1000)
        #     return PhasePrepare(self)
        # if name == 'phaseJudge':
        #     return PhaseJudge(self)
        # if name == 'phaseDraw':
        #     return PhaseDraw(self)
        # if name == 'phaseUse':
        #     return PhaseUse(self)
        # if name == 'phaseDiscard':
        #     return PhaseDiscard(self)
        # if name == 'phaseFinish':
        #     return PhaseFinish(self)
        # if name == 'draw':
        #     return Draw(self)
        # if name == 'gain':
        #     return Gain(self)
        # if name == 'discard':
        #     return Discard(self)
        # if name == 'lose':
        #     return Lose(self)
        # if name == 'useCard':
        #     return UseCard(self)
        # if name == 'useSkill':
        #     return UseSkill(self)
        # if name == 'useCardToTarget':
        #     return UseCardToTarget(self)
        # if name == 'damage':
        #     return Damage(self)
        # if name == 'recover':
        #     return Recover(self)
        # if name == 'changeHp':
        #     return ChangeHp(self)
        # if name == 'dying':
        #     return Dying(self)
        # if name == 'die':
        #     return Die(self)
        # print("\033[0;31;40m" + "Warning: Failed to create event \"" + name + "\"!" + "\033[0m")
        # return Event(self)

        # status = self.__status
        # if name == 'zuijiu':
        #     return Zuijiu(status)
        # if name == 'updateAI':
        #     return UpdateAI(status)
        # if name == 'jizhi':
        #     return Jizhi(status)
        # if name == 'jianxiong':
        #     return Jianxiong(status)
        # if name == 'huode':
        #     return Huode(status)
        # # if name == 'zhuge':
        # #     return ZhugeSkill(status)
        # if name == 'guanshiSkill':
        #     return GuanshiSkill(status)
        # if name == 'baguaSkill':
        #     return BaguaSkill(status)
        # if name == 'renwangSkill':
        #     return RenwangSkill(status)
        # if name == 'onPhaseUseAfter':
        #     return OnPhaseUseAfter(status)
        # if name == 'onPhaseAfter':
        #     return OnPhaseAfter(status)
        # print("\033[0;31;40m" + "Warning: Failed to create skill \"" + name + "\"!" + "\033[0m")
        # return Skill(status)

        # newCard = None
        # # newCard = Card(self.createID(), suit, number)
        # if name == "sha":
        #     newCard = Sha(suit, number, nature)
        # if name == "shan":
        #     newCard = Shan(suit, number)
        # if name == "tao":
        #     newCard = Tao(suit, number)
        # if name == "jiu":
        #     newCard = Jiu(suit, number)
        # if name == "zhuge":
        #     newCard = Zhuge(suit, number)
        # if name == "guanshi":
        #     newCard = Guanshi(suit, number)
        # if name == "bagua":
        #     newCard = Bagua(suit, number)
        # if name == "renwang":
        #     newCard = Renwang(suit, number)
        # if name == "juedou":
        #     newCard = Juedou(suit, number)
        # if name == "guohe":
        #     newCard = Guohe(suit, number)
        # if name == "shunshou":
        #     newCard = Shunshou(suit, number)
        # if name == "tiesuo":
        #     newCard = Tiesuo(suit, number)
        # if name == "nanman":
        #     newCard = Nanman(suit, number)
        # if name == "wuzhong":
        #     newCard = Wuzhong(suit, number)
        # if name == "wanjian":
        #     newCard = Wanjian(suit, number)
