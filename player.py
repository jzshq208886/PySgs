import random
from card import *
from event import *

from ai import *
import os


class Player:
    __itemType = 'player'

    def __init__(self, room, operator='human'):
        self.__operator = operator

        self.__room = room
        self.__status = room.status
        self.__ui = None
        self.__ai = AI(self)

        self.__identity = 'fan'
        self.__seat = 0
        self.__previous = None
        self.__next = None

        self.__character = 'shibing'
        self.__charaDisplayed = True
        self.__skill = []
        self.__name = 'xiaosha' if operator == 'ai' else 'wanjia'
        self.__sex = 'male'
        self.__kingdom = 'qun'
        self.__hp = 0
        self.__maxHp = 0
        self.skin = None
        self.skins = []

        self.__alive = True
        self.__playing = False
        self.__drunk = 0
        self.__turnOver = False
        self.__tied = False
        self.__dying = False
        self.__onHook = False

        self.__stat = {
            'card': {'sha': 0, 'jiu': 0},
            'skill': {},
        }
        self.__handcardArea = CardSet(room, self)
        self.__equipArea = EquipArea(room, self)
        self.__judgementArea = JudgementArea(room, self)

        self.storage = {'skin_f': None}

        self.__choosing = False
        self.__choosingTarget = False
        self.__selectable = {'card': [], 'target': [], 'button': []}
        self.__selected = {'card': [], 'target': [], 'button': []}
        self.__controls = []
        self.__choosableControls = []

    @property
    def itemType(self):
        return self.__itemType

    @property
    def operator(self):
        return self.__operator

    def isUnderControl(self):
        return self.__operator == 'human' and not self.__onHook

    @property
    def room(self):
        return self.__room

    def getRoom(self):
        return self.__room

    @property
    def ui(self):
        pass
        return self.__ui

    @ui.setter
    def ui(self, value):
        self.__ui = value
        self.__room.ui.add(value)

    @property
    def ai(self):
        return self.__ai

    @property
    def status(self):
        return self.__status

    def getStatus(self):
        return self.__status

    @property
    def character(self):
        return self.__character

    @character.setter
    def character(self, value):
        self.__character = value

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def sex(self):
        return self.__sex

    @sex.setter
    def sex(self, value):
        self.__sex = value

    @property
    def kingdom(self):
        return self.__kingdom

    @kingdom.setter
    def kingdom(self, value):
        self.__kingdom = value

    @property
    def identity(self):
        return self.__identity

    @identity.setter
    def identity(self, value):
        self.__identity = value

    @property
    def seat(self):
        return self.__seat

    @seat.setter
    def seat(self, v):
        self.__seat = v

    @property
    def previous(self):
        return self.__previous

    @previous.setter
    def previous(self, v):
        self.__previous = v

    @property
    def next(self):
        return self.__next

    @next.setter
    def next(self, nextPlayer):
        self.__next = nextPlayer

    @property
    def hp(self):
        return self.__hp

    @hp.setter
    def hp(self, value):
        self.__hp = value

    @property
    def maxHp(self):
        return self.__maxHp

    @maxHp.setter
    def maxHp(self, value):
        self.__maxHp = value

    @property
    def handcardLimit(self):
        pass
        return self.__hp

    def isWounded(self):
        return self.__hp < self.__maxHp

    @property
    def lostHp(self):
        return self.__maxHp - self.__hp

    @property
    def alive(self):
        return self.__alive

    @alive.setter
    def alive(self, value):
        self.__alive = value

    @property
    def drunk(self):
        return self.__drunk

    @drunk.setter
    def drunk(self, value):
        self.__drunk = value

    @property
    def stat(self):
        return self.__stat

    def isAlive(self):
        return self.__alive

    def isDying(self):
        return self.__dying

    def setDying(self, value):
        self.__dying = value

    # @stat.setter
    # def stat(self, value):
    #     self.__stat = value

    def getCards(self, position, arg: dict = None, filter=None):
        if filter is None and callable(arg):
            filter = arg
            arg = None

        cards, cds = [], []
        for char in position:
            if char == 'h':
                cards += self.handcard
            if char == 'e':
                cards += self.equipArea.cards
            if char == 'j':
                pass
        for card in cards:
            if arg and ('name' in arg and card.getName(self) != arg['name']
                        or 'suit' in arg and card.getSuit(self) != arg['suit']
                        or 'color' in arg and card.getColor(self) != arg['color']
                        or 'number' in arg and card.getNumber(self) != arg['number']
                        or 'type' in arg and card.getType(self) != arg['type']
                        or 'subtype' in arg and card.getSubtype(self) != arg['subtype']):
                continue
            if filter and not filter(card):
                continue
            cds.append(card)
        return cds

    def countCards(self, position, arg: dict = None, filter=None):
        if filter is None and callable(arg):
            filter = arg
            arg = None

        cards, num = [], 0
        for char in position:
            if char == 'h':
                cards += self.handcard
            if char == 'e':
                cards += self.equipArea.cards
            if char == 'j':
                pass
        for card in cards:
            if arg and ('name' in arg and card.getName(self) != arg['name']
                        or 'suit' in arg and card.getSuit(self) != arg['suit']
                        or 'color' in arg and card.getColor(self) != arg['color']
                        or 'number' in arg and card.getNumber(self) != arg['number']
                        or 'type' in arg and card.getType(self) != arg['type']
                        or 'subtype' in arg and card.getSubtype(self) != arg['subtype']):
                continue
            if filter and not filter(card):
                continue
            num += 1
        return num

    def getEquip(self, subtype):
        if subtype not in self.__equipArea.equipments:
            return None
        return self.__equipArea.equipments[subtype]

    @property
    def handcardArea(self):
        return self.__handcardArea

    @property
    def handcard(self):
        return self.__handcardArea.cards

    @property
    def handcardNum(self):
        return self.__handcardArea.length

    @property
    def equipArea(self):
        return self.__equipArea

    @property
    def skill(self):
        return self.__skill

    def setStorage(self, arg, element):
        self.storage[arg] = element

    def addStorage(self, arg, num=1):
        if arg in self.storage and type(self.storage[arg]) is int:
            self.storage[arg] += num

    def appendStorage(self, arg, element):
        if arg in self.storage and type(self.storage[arg]) is list:
            self.storage[arg].append(element)

    def selectable(self, arg: str = None):
        if arg is None:
            return self.__selectable
        return self.__selectable[arg]

    def setSelectable(self, arg: str, elements):
        self.__selectable[arg].clear()
        self.__selectable[arg].extend(elements)

    def selected(self, arg: str = None):
        if arg is None:
            return self.__selected
        return self.__selected[arg]

    def setSelected(self, arg: str, elements):
        self.__selected[arg].clear()
        self.__selected[arg].extend(elements)

    @property
    def choosing(self):
        return self.__choosing

    @choosing.setter
    def choosing(self, value):
        self.__choosing = value

    @property
    def choosingTarget(self):
        return self.__choosingTarget

    @choosingTarget.setter
    def choosingTarget(self, value):
        self.__choosingTarget = value

    def startChoosing(self):
        self.choosing = True

    def endChoosing(self):
        self.__selected['card'].clear()
        self.__selected['target'].clear()
        self.__selectable['card'].clear()
        self.__selectable['target'].clear()
        if self.__ui:
            self.__ui.setControls([])
        self.__choosing = False

    def initialize(self):
        pass
        self.ai.updateInfo()

    def chooseRole(self):
        names = ['caocao', 'huangyueying', 'jiayahui', 'jiayahui']
        if self.__operator == 'human':
            self.changeChara(names[random.randint(0, 3)])
            self.initChara()
        else:
            num = random.randint(0, 3)
            while names[num] == self.next.name:
                num = random.randint(0, 3)
            self.changeChara(names[num])
            self.initChara()
        pass

    def changeChara(self, name):
        for skillName in self.__character[3]:
            self.removeSkill(skillName)

        self.__name = name
        self.__character = self.room.characters[name]
        self.skins = []

        self.initChara()

    def initChara(self):
        self.changeSkin('1')

        hp = self.__character[2]
        if type(hp) == int:
            self.__hp, self.__maxHp = hp, hp
        else:
            hpm = hp.split('/')
            self.__hp, self.__maxHp = int(hpm[0]), int(hpm[1])
        self.__sex = self.__character[0]
        self.__kingdom = self.__character[1]
        # 添加技能
        for skillName in self.__character[3]:
            # print("\033[0;31;40m"+skillName+"\033[0m")
            self.addSkill(skillName)

    def changeSkin(self, name):
        self.skin = name
        for ui in self.__room.ui:
            if self.name + '_' + self.skin not in ui.image:
                # 遍历所有路径
                for dire in self.room.directory:
                    directory = os.path.join(dire, "image\\character\\" + self.__name + "_" + name + ".png")
                    if os.path.exists(directory):
                        ui.loadImage(self.__name + '_' + name, directory)
                        # print('bf_caocao_1' in ui.image)
                        break
            # audioPath = os.path.join(r'D:\Applications\Amusement\无名杀\noname\resources\app\audio\die',
            #                          f'{self.name}.mp3')
            # if os.path.exists(audioPath):
            #     ui.loadAudio(self.name + '_die', audioPath)
        if name not in self.skins:
            self.skins.append(name)

    def flipSkin(self):
        num = self.skins.index(self.skin) + 1
        if num >= len(self.skins):
            num = 0
        self.changeSkin(self.skins[num])

    def addSkill(self, name, temp=False):
        if not name or self.hasSkill(name):
            return False

        skill = self.__room.createSkill(name)

        if skill:
            skill.temp = temp
            skill.owner = self
            self.__skill.append(skill)
            skill.initialize()

    def removeSkill(self, name):
        for i in range(len(self.__skill)):
            if self.__skill[i].name == name or self.__skill[i] == name:
                self.__skill[i].onRemove()
                self.__skill.pop(i)
                break

    def hasSkill(self, name):
        for skill in self.__skill:
            if skill.name == name:
                return True
        return False

    def getSkill(self, skillType=None):
        return list(
            filter(lambda skill: skill.skillType == skillType, self.__skill)) if skillType else self.__skill.copy()

    def displayChara(self):
        self.__charaDisplayed = False

    def phase(self):
        next = Phase(self.__status)
        next.player = self
        next.addToNext()
        return next
        # next = self.__status.addEvent('phase')
        # next.player = self
        # return next

    def phaseStage(self, stage):
        next = self.__status.addEvent(stage)
        next.player = self
        return next

    def startDraw(self, num=4, bottom=False, visible=False):
        if self.room.test:
            num = 1
        next = self.draw(num)
        next.noTrigger = True
        self.status.processNext()

    def luckyHandcard(self):
        num = self.countCards('h')
        drawPile = self.room.drawPile
        for i in range(num):
            drawPile.addCard(self.handcard[i], 'random')
        next = self.lose(self.handcard)
        next.noTrigger = True
        self.startDraw(num)

    def draw(self, num=1, visible=False, bottom=False):
        next = self.__status.addEvent('draw')
        next.player = self
        next.num = num
        next.visible = visible
        next.bottom = bottom
        return next

    def discard(self, cards, source=None):
        if type(cards) is str:
            cards = self.getCards(cards)
        elif type(cards) is not list:
            cards = [cards]
        if source is None:
            source = self

        next = self.__status.addEvent('discard')
        next.player = self
        next.cards = cards
        next.source = source
        return next

    def gain(self, cards, pattern='gain', source=None):
        if type(cards) != list:
            cards = [cards]
        next = self.__status.addEvent('gain')
        next.player = self
        next.cards = cards
        next.pattern = pattern
        next.source = source
        return next

    def lose(self, cards, pattern='lose'):
        if type(cards) != list:
            cards = [cards]
        next = self.__status.addEvent('lose')
        next.player = self
        next.cards = cards
        next.pattern = pattern
        return next

    def gainTargetCard(self, target, position='he', forced=False, num=1):
        pass
        cards = target.getCards(position)
        card = None
        if cards:
            card = random.choice(cards)
        if 'e' in position:
            if target.getEquip('armor'):
                card = target.getEquip('armor')
            elif target.getEquip('weapon'):
                card = target.getEquip('weapon')
        if card:
            return self.gain(card, 'gain', target)

    def discardTargetCard(self, target, position='he', forced=False, num=1):
        cards = target.getCards(position)
        card = None
        if cards:
            card = random.choice(cards)
        if 'e' in position:
            if target.getEquip('armor'):
                card = target.getEquip('armor')
            elif target.getEquip('weapon'):
                card = target.getEquip('weapon')
        if card:
            return target.discard(card, self)

    def loseCardTo(self, cards, pile, pattern='lose', visible=True):
        # 省略insert事件
        room = self.room
        if type(cards) is not list:
            cards = [cards]
        if pile == 'discardPile':
            pile = room.discardPile
        elif pile == 'handleArea':
            pile = room.handleArea

        if pile == room.discardPile or pile == room.handleArea:
            room.broadcastAll(lambda ui: ui.addToHandling(cards, 9999 if pattern == 'use' else 500, pattern == 'use',
                                                          info="弃置" if pattern == 'discard' else None))

        room.broadcastAll(lambda uix: uix.setOriginCoors(cards))
        pile.addCard(cards)
        for i in range(len(cards)):
            room.broadcastAll(lambda ui: ui.setMovement(cards[i], i, ui.getCoordinate(cards[i]), visible=visible))

        return self.lose(cards, pattern)

    def insert(self):
        pass

    def useCard(self, card, targets=None):
        if not card.multiTarget:
            self.__room.targetSort(targets)
        next = self.__status.addEvent('useCard')
        next.card = card
        next.player = self
        if card.active:
            next.targets = targets
        return next

    def useCardToTarget(self, card, targets):
        if type(targets) is not list:
            targets = [targets]
        next = self.__status.addEvent('useCardToTarget')
        next.player = self
        next.card = card
        next.targets = targets
        return next

    def useSkill(self, skill, cards=None, targets=None):
        next = self.__status.addEvent('useSkill')
        next.skill = skill
        next.player = self
        next.cards = cards
        next.targets = targets
        return next

    def skillInvoke(self, skill, cards=None, targets=None):
        next = self.__status.addEvent(skill.name + 'Invoke')
        next.skill = skill
        next.player = self
        next.cards = cards
        next.targets = targets
        return next

    def respond(self, card):
        next = Respond(self.__status)
        next.player = self
        next.card = card
        next.addToNext()
        return next

    def damage(self, num=1, source=None, card=None, nature=None):
        next = self.__status.addEvent('damage')
        next.player = self
        next.num = num
        next.source = source
        next.card = card
        next.nature = nature
        return next

    def recover(self, num=1, source=None, card=None):
        next = self.__status.addEvent('recover')
        next.player = self
        next.num = num
        next.source = source
        next.card = card
        return next

    def changeHp(self, num, source=None, card=None):
        next = self.__status.addEvent('changeHp')
        next.player = self
        next.num = num
        next.source = source
        next.card = card
        return next

    def loseMaxHp(self, num=1, source=None):
        pass
        self.maxHp -= num
        if self.hp > self.maxHp:
            self.hp = self.maxHp
        if self.maxHp == 0:
            self.die()

    def dying(self, source=None, card=None):
        next = self.__status.addEvent('dying')
        next.player = self
        next.source = source
        next.card = card
        return next

    def die(self, source=None, card=None):
        next = self.__status.addEvent('die')
        next.player = self
        next.source = source
        next.card = card
        return next

    def judge(self):
        pass
        next = Judge(self.__status)
        next.player = self
        next.addToNext()
        return next

    def chooseToUse(self, prompt: str = None, cardFilter=True, targetFilter=True, phaseUse=False):
        next = self.__status.addEvent('chooseToUse')
        next.player = self
        next.cardFilter = cardFilter
        next.targetFilter = targetFilter
        next.phaseUse = phaseUse
        if prompt:
            next.prompt = prompt
        return next

    def chooseToResponse(self, prompt: str = None, cardFilter=True):
        next = ChooseToRespond(self.__status)
        next.player = self
        next.cardFilter = cardFilter
        if prompt:
            next.prompt = prompt
        next.addToNext()
        return next

    def chooseToDiscard(self, prompt: str = None, position='he', selectCardNum=1, cardFilter=True, forced=False):
        next = self.__status.addEvent('chooseToDiscard')
        next.player = self
        next.position = position
        next.selectCardNum = selectCardNum
        next.cardFilter = cardFilter
        next.forced = forced
        if prompt:
            next.prompt = prompt
        return next

    def chooseToInvoke(self, skills):
        next = self.__status.addEvent('chooseToInvoke')
        next.player = self
        next.invokableSkill = skills
        return next

    def chooseBool(self, prompt: str = None):
        next = ChooseBool(self.status)
        next.player = self
        if prompt:
            next.prompt = prompt
        next.addToNext()
        return next

    def chooseCard(self, prompt: str = None, position='he', selectCardNum=1, cardFilter=True, forced=False):
        next = self.__status.addEvent('chooseCard')
        next.player = self
        next.position = position
        next.selectCardNum = selectCardNum
        next.cardFilter = cardFilter
        next.forced = forced
        if prompt:
            next.prompt = prompt
        return next

    def chooseCardTarget(self, prompt: str = None, position: str = 'he', selectCardNum=1, selectTarget=1,
                         cardFilter=True, targetFilter=True, forced=False, skillFilter=False):
        next = self.__status.addEvent('chooseCardTarget')
        if prompt:
            next.prompt = prompt
        next.player = self
        next.position = position
        next.selectCardNum = selectCardNum
        next.cardFilter = cardFilter
        next.selectTargetNum = selectTarget
        next.targetFilter = targetFilter
        next.forced = forced
        return next

    def makeChoice(self, event=None):
        self.choosing = True
        if event is None:
            event = self.status.currentEvent

        # ai选择延迟
        if not self.isUnderControl():
            self.room.delay(250)

        sableC = self.selectable('card')
        sedC = self.selected('card')
        sableT = self.selectable('target')
        sedT = self.selected('target')

        while True:
            cardRange = event.selectCardNum
            targetRange = event.selectTargetNum

            # 确定可选牌
            if event.cardFilter:
                cards = list(
                    filter(lambda card: card not in sedC and event.filterCard(card), self.getCards(event.position)))
                self.setSelectable('card', cards)
                # print('Player.makeChoice-selectable(card):', self.selectable('card'))

            # 确定可选目标
            if event.targetFilter:
                targets = []
                if not event.filterCard or len(self.selected('card')) >= cardRange[0]:
                    self.choosingTarget = True
                    targets = list(filter(lambda current: current not in self.selected('target'), event.room.players))
                    if callable(event.filterTarget):
                        targets = list(filter(event.filterTarget, targets))
                else:
                    self.choosingTarget = False
                self.setSelectable('target', targets)
                # print('Player.makeChoice-selectable(target):', sableT)

            # 全选
            if targetRange[0] == -1:
                sedT.extend(sableT)
                sableT.clear()
            # 唯一可选目标时，自动选择
            elif not len(sedT) and len(sableT) == 1 and targetRange[0] == 1 and targetRange[1] == 1:
                sedT.append(sableT[0])
                sableT.remove(sedT[0])

            # 进行选择
            if self.isUnderControl():
                # 设置选项
                if self.ui:
                    self.ui.setControls('phaseUse' if event.parent and event.parent.name == 'phaseUse' else 'choose')
                    pass  # 设置重铸
                    self.ui.setClickable('determine', (not event.cardFilter or len(sedC) >= cardRange[0])
                                         and (not event.targetFilter or len(sedT) >= targetRange[0]))
                    # print(len(sedC))
                    # print(self.ui.isClickable('determine'))
                    self.ui.setClickable('cancel', not event.forced)
                result = self.ui.waitForChoosing()
            else:
                result = self.ai.singleChoose()
            if result == 'gameInterrupted':
                return

            # print('chooseCardTarget-singleChoose_result:', result)
            if type(result) is int:
                pass
            elif result in ['determine', 'cancel']:
                if result == 'determine':
                    event.setResult('bool', True)
                    event.setResult('cards', self.selected('card').copy())
                    if len(self.selected('card')) == 1:
                        event.setResult('card', self.selected('card')[0])
                    targets = self.selected('target').copy()
                    if not event.multiTarget:
                        self.room.targetSort(targets)
                    event.setResult('targets', targets)
                    if len(self.selected('target')) == 1:
                        event.setResult('target', self.selected('target')[0])
                    # self.setResult('skill', )
                self.endChoosing()
                return
            elif result:
                resultType = result.itemType
                if resultType == 'card':
                    if result in self.selected('card'):
                        if cardRange[0] != -1:
                            self.selected('card').remove(result)
                            self.selected('target').clear()
                    else:
                        self.selected('card').append(result)
                        if len(self.selected('card')) > cardRange[1]:
                            self.selected('card').pop(0)
                            self.selected('target').clear()
                        if event.complexSelect:
                            self.selected('target').clear()
                elif resultType == 'player':
                    if result in self.selected('target'):
                        if cardRange[0] != -1:
                            self.selected('target').remove(result)
                    else:
                        self.selected('target').append(result)
                        if len(self.selected('target')) > targetRange[1]:
                            self.selected('target').pop(0)

    def available(self, item):
        if item.itemtype != 'card' and item.itemtype != 'skill':
            print('\033[1;31mWarning: player.getUseOrder(item): Parameter \"item\" is neither card nor skill!\033[0m')
            return -100
        pass

    def hasAvailableTarget(self, card, event=None, ignoreDistance=False, ignoreUsable=False, ignoreFilter=False):
        for target in self.room.players:
            if self.canUse(card, target, event, ignoreDistance, ignoreUsable, ignoreFilter):
                return True
        return False

    def getAvailableTarget(self, card, event=None, ignoreDistance=False, ignoreUsable=False, ignoreFilter=False):
        targets = []
        for target in self.room.players:
            if self.canUse(card, target, event, ignoreDistance, ignoreUsable, ignoreFilter):
                targets.append(target)
        return targets

    def playerEnabled(self, card):
        room = self.room
        if type(card) is str:
            card = room.createCard(card, virtual=True)
        pass
        return True

    def targetEnabled(self, card):
        room = self.room
        if type(card) is str:
            card = room.createCard(card, existence='virtual')
        pass
        return True

    # 可以主动使用，如桃不能对他人使用，杀不能对自己使用
    def canUse(self, card, target, event=None, ignoreDistance=False, ignoreUsable=False, ignoreFilter=False):
        # 强行单独考虑濒死使用桃情况
        if event and card.name == 'tao' and event.getParent().name == 'dying':
            return target == event.getParent().player

        room = self.room
        if type(card) is str:
            card = room.createCard(card, existence='virtual')
        if not target.targetEnabled(card):  # 目标不可
            return False
        if not self.playerEnabled(card):  # 使用不可
            return False

        if not ignoreUsable and card.name in self.__stat['card'] \
                and self.__stat['card'][card.name] >= self.getCardUsable(card) \
                and not (card.name == 'jiu' and self.isDying()) \
                and not (card.name == 'sha' and self.countCards('e', {'name': 'zhuge'})):  # 使用次数
            return False

        if card.selectTarget()[0] == 0:
            return False
        if card.banTarget(self, target):
            return False
        if not ignoreDistance and not self.ignoreDistance(card, target) and not card.rangeFilter(self, target):
            return False
        if not ignoreFilter and not card.filterTarget(self, target):
            return False
        # if not ignoreUsable and self == room.getCurrent() and self.__phaseStage == 'phaseUse' \
        #         and self.__useTimes[card.name()] > card.usable():
        #     return False
        return True

    def canDiscard(self, card):
        pass  # checkMod
        return True

    def getCardUsable(self, card):
        pass  # checkMod
        return card.usable

    # 可以成为目标，如桃可以指定他人为目标，杀不能指定自己为目标
    def canTarget(self, card, target):
        room = self.room
        if type(card) is str:
            card = room.createCard(card, existence='virtual')
        if not target.targetEnabled(card):
            return False
        if card.banTarget(self, target):
            return False
        return True

    def cardIgnoreDistance(self, card):
        pass

    def targetIgnoreDistance(self, target):
        pass

    def cardTargetIgnoreDistance(self, card, target):
        pass

    def ignoreDistance(self, card=None, target=None):
        pass
        return False
        # if card is None and target is None:
        #     return False
        # if card is None:
        #     pass
        # if type(card) is str:
        #     card = self.room().createCard(card, virtual=True)
        # if target is None:
        #     pass
        # pass

    def ignoreUsable(self, card=None, target=None):
        pass
        return False

    def getDistance(self, target):
        pass
        return 1

    def targetInRange(self, target):
        pass
        return True

    def getUseOrder(self, item):
        if item.itemType != 'card' and item.itemType != 'skill':
            print('\033[1;31mWarning: player.getUseOrder(item): Parameter \"item\" is neither card nor skill!\033[0m')
            return -100
        pass  # player个性化
        return item.order

    def getUseValue(self, item, event=None):
        if item.itemType != 'card' and item.itemType != 'skill':
            print('\033[1;31mWarning: player.getUseValue(item): Parameter \"item\" is neither card nor skill!\033[0m')
            return -100

        if event is None:
            event = self.status.currentEvent

        if not item.active:
            return self.getEffect(item, self)

        if item.itemType == 'card' and item.type == 'equip':
            equip = self.getEquip(item.subtype)
            if equip and item.equipValue <= equip.equipValue:
                return 0
            if self.countCards('h', filter=lambda
                    card: card.type == 'equip' and card.subtype == item.subtype and card.equipValue > item.equipValue):
                return 0
            return 1
        nt = item.needTarget
        targets = self.getAvailableTarget(item, event)
        # print('Player.getUseValue-availableTargets', targets)
        if len(targets) < nt[0]:
            print('\033[1;31mError: player.getUseValue(item): Available targets of item not enough!\033[0m')
            return 0
        if nt[0] == -1:
            return sum([self.getEffect(item, self, target) for target in targets])
        targetEffects = list(
            filter(lambda t: t[1] > 0, [(target, self.getEffect(item, self, target)) for target in targets]))
        targetEffects.sort(key=lambda tpl: tpl[1], reverse=True)
        if len(targetEffects) > nt[1]:
            return sum([tpl[1] for tpl in targetEffects][:nt[1]])
        return sum([tpl[1] for tpl in targetEffects])

    def getEffect(self, item, player=None, target=None):
        if self.name == 'xinxianying' and player.name == 'xinxianying' and item.name == 'shan':
            print("\033[0;31;40m" + "getEffect-in" + "\033[0m")

        if player is None:
            player = self

        playerEnemy = 1
        if self.getAttitude(player) < 0:
            playerEnemy = -1
        elif self.getAttitude(player) == 0:
            playerEnemy = 0

        if target is None:
            return playerEnemy * item.playerResult(player)

        targetEnemy = 1
        if self.getAttitude(target) < 0:
            targetEnemy = -1
        elif self.getAttitude(target) == 0:
            targetEnemy = 0

        playerResult = item.playerResult(player, target)
        if not playerResult:
            playerResult = 0
        targetResult = item.targetResult(player, target)
        if not targetResult:
            targetResult = 0

        # print('player.getEffect()-item:', item)
        # print('player.getEffect()-playerEnemy:', playerEnemy)
        # print('player.getEffect()-playerResult:', playerResult)
        # print('player.getEffect()-targetEnemy:', targetEnemy)
        # print('player.getEffect()-targetResult:', targetResult)
        return playerEnemy * playerResult + targetEnemy * targetResult

    def getAttitude(self, player):
        if player is None:
            print('Warning:', self.name, 'try to get attitude to None')
            return 0
        info = self.ai.info
        if info[player]['identityKnown']:
            if player.identity == self.identity:
                return 5
            if player.identity == 'zhu':
                if self.identity == 'zhong':
                    return 10
                if self.identity == 'fan':
                    return -10
                if self.identity == 'nei':
                    pass
            pass
            return -5
        return info[player]['attitude']

    def hook(self):
        self.__onHook = True

    ###pzh更改部分
    def equip(self, card):
        next = Equip(self.__status, card)
        next.player = self
        next.card = card
        next.addToNext()
        return next
