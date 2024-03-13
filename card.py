import random
from collections import OrderedDict


class Card:
    __itemType = 'card'
    name = 'blankCard'  # 牌名，规定将类名首字母小写作为牌名，方便统一化创建牌
    type = 'none'  # 基本牌（【杀】【闪】【桃】【酒】）'basic'，锦囊牌'trick'，装备牌'equip'
    subtype = "none"  # 装备分为'weapon''armor''defendHorce''attackHorce'，锦囊分为'normal''delay'
    natures = []  # 属性，除了【杀】都不用写
    tags = []  # 暂未实装

    active = True  # 可主动使用，除了【闪】和【无懈可击】，都是True
    targetNum = 1  # 指定目标数。若是一个范围，则写成[a, b]；若指定所有目标，写-1
    multiTarget = False  # 拥有指向目标，如【借刀杀人】，未实装
    range = True  # 距离要求，如【杀】、【顺手牵羊】和【兵粮寸断】，未实装

    targetBan = False  # 一般def成一个函数（targetFilter也是），判断哪些目标被禁止
    targetFilter = True  # 合法目标中，哪些可以直接指定（如【桃】【酒】【无中生有】等对自己使用的牌需要写）
    usable = 999  # 每回合可使用次数
    updateTrigger = 'none'  # 更新使用次数的时机，【杀】为'phaseUseAfter'，【酒】为'phaseAfter'

    # 装备牌属性
    attackRange = 1  # 武器牌的攻击范围。距离相关未实装
    defendDistance = 0  # 防御马防御距离，距离相关未实装
    attackDistance = 0  # 进攻马进攻距离，距离相关未实装
    skill = None  # 装备技能名，取名规则为装备name+'Skill'

    # ai
    order = 0  # 使用优先级
    value = 0  # 牌的保留价值
    equipValue = 0  # 装备牌的装备价值

    # 对使用者的影响，返回一个值，负值代表负面影响
    def playerResult(self, player, target):
        return 0

    # 对目标的影响，返回一个值，负值代表负面影响
    def targetResult(self, player, target):
        return 0

    def __init__(self, suit="none", number=0, nature=None, existence='real'):
        # self.__id = cardID
        self.__status = None

        self.__suit = suit
        self.__number = number
        self.__nature = nature

        self.__existence = existence
        self.__cards = []
        self.__cardsVisible = True

        self.__area = None

        self.__selectTarget = [1, 1]
        self.__banTarget = False
        self.__rangeFilter = True
        self.__filterTarget = True

    @property
    def itemType(self):
        return self.__itemType

    def setStatus(self, status):
        self.__status = status

    def getName(self, player=None):
        pass
        return self.name

    def getType(self, player=None):
        pass
        return self.type

    def getSubtype(self, player=None):
        pass
        return self.subtype

    @property
    def suit(self):
        return self.__suit

    @suit.setter
    def suit(self, v):
        self.__suit = v

    def getSuit(self, player=None):
        pass
        return self.__suit

    @property
    def color(self):
        if self.__suit == "heart" or self.__suit == "diamond":
            return "red"
        if self.__suit == "spade" or self.__suit == "club":
            return "black"
        return None

    def getColor(self, player=None):
        pass
        return self.color

    @property
    def number(self):
        return self.__number

    @number.setter
    def number(self, v):
        self.__number = v

    def getNumber(self, player=None):
        pass
        return self.__number

    @property
    def nature(self):
        return self.__nature

    @nature.setter
    def nature(self, value):
        self.__nature = value

    def getNature(self, player=None):
        pass
        return self.__nature

    def isReal(self):
        return self.__existence == 'real'

    def isVirtual(self):
        return self.__existence == 'virtual'

    def isConverted(self):
        return self.__existence == 'converted'

    def setExistence(self, existence: str):
        self.__existence = existence

    @property
    def cards(self):
        if self.__existence == 'real':
            return [self]
        return self.__cards

    @cards.setter
    def cards(self, lst):
        if type(lst) is list:
            self.__cards = lst.copy()
        self.__cards = [lst]

    @property
    def area(self):
        return self.__area

    @area.setter
    def area(self, value):
        self.__area = value

    @property
    def position(self):
        return self.__area.positionType

    @property
    def owner(self):
        return self.__area.owner

    @property
    def needTarget(self):
        return self.selectTarget()

    def selectTarget(self, player=None):
        if not self.active:
            return [0, 0]
        numRange = self.targetNum
        if callable(self.targetNum):
            if player is None:
                player = self.__status.currentEvent().player
            numRange = self.targetNum(player)
        if type(numRange) is int:
            numRange = [numRange, numRange]
        return numRange

    def banTarget(self, player, target):
        if callable(self.targetBan):
            return self.targetBan(player, target)
        return self.targetBan

    def rangeFilter(self, player, target):
        if callable(self.range):
            return self.range(player, target)
        if type(self.range) is int:
            return player.getDistance(target) <= self.range
        return self.range

    def filterTarget(self, player, target):
        # if self.banTarget(player, target):
        #     return False
        # if not self.rangeFilter(player, target):
        #     return False
        if callable(self.targetFilter):
            return self.targetFilter(player, target)
        elif self.type == 'equip':
            return target == player
        return self.targetFilter

    def effect(self, player, target=None, addedTarget=None):
        if self.type == 'equip':
            player.room.delay(100)
            return target.equip(self)
        else:
            next = self.__status.addEvent(self.name + 'Effect')
            next.card = self
            next.player = player
            if self.active:
                next.multiTarget = self.multiTarget
                next.target = target
                next.setAddedTarget(target, addedTarget)
            return next


class CardSet:
    __itemType = 'cardSet'
    positionType = 'none'

    def __init__(self, room, owner=None):
        self.__room = room
        self.__cards = []
        self.__owner = owner

    def __contains__(self, item):
        return item in self.cards

    def __len__(self):
        return len(self.cards)

    @property
    def itemType(self):
        return self.__itemType

    # @property
    # def positionType(self):
    #     return self.__positionType

    @property
    def room(self):
        return self.__room

    @property
    def cards(self):
        return self.__cards

    @property
    def length(self):
        return len(self.cards)

    def getCards(self, num=1, bottom=False):
        if num >= self.length:
            return self.cards.copy()
        if bottom:
            cards = self.__cards[len(self.__cards)-num:]
        else:
            cards = self.__cards[:num]
        return cards

    def get(self, index):
        if (index >= 0 and index > self.length - 1) \
                or (index < 0 and -index > self.length):
            print("Warning: Plie.get(index) out of index")
            return None
        return self.__cards[index]

    @property
    def owner(self):
        return self.__owner

    def addCard(self, cards, position=-1):
        if type(cards) is not list:
            cards = [cards]
        if position == 'random':
            position = random.randint(0, self.length)
        for card in cards:
            if position == -1:
                self.__cards.append(card)
            else:
                self.__cards.insert(position, card)
            card.area = self

    def removeCard(self, cards):
        if type(cards) is not list:
            cards = [cards]
        for card in cards:

            i = 0
            while i < len(self.__cards):
                if self.__cards[i] == card:
                    self.__cards.pop(i)
                    return
                i += 1


class Pile(CardSet):
    positionType = 'p'

    def __init__(self, room, owner=None):
        super().__init__(room, owner)
        self.__itemType = 'pile'
        self.__owner = owner

    # def top(self):
    #     if self.__cards:
    #         return self.__cards[0]
    #     return None
    #
    # def bottom(self):
    #     pass


class DiscardPile(Pile):
    positionType = 'd'

    def __init__(self, room, owner=None):
        super().__init__(room, owner)

    def top(self):
        if self.__cards:
            return self.__cards[-1]
        return None

    def bottom(self):
        pass

    def get(self, index):
        if index > len(self.__cards) - 1:
            print("Warning: Plie.get(index) out of index")
            return None
        return self.__cards[-index - 1]


class HandleArea(CardSet):
    positionType = 't'

    def __init__(self, room, owner=None):
        super().__init__(room, owner)

    def removeCard(self, cards):
        super().removeCard(cards)

        # def removeUI(ui):
        #     ui.removeHandling(cards)
        #
        # self.room.broadcastAll(removeUI)


class JudgingArea(CardSet):
    pass


class HandcardArea(CardSet):
    positionType = 'h'

    def __init__(self, room, owner=None):
        super().__init__(room, owner)
        # self.__positionType = 'h'


class EquipArea(CardSet):
    positionType = 'e'

    def __init__(self, room, owner=None):
        super().__init__(room, owner)
        self.__equipments = {'weapon': None, 'armor': None, 'defendHorse': None, 'attackHorse': None}

    @property
    def cards(self):
        cards = []
        for subtype in self.__equipments:
            if self.__equipments[subtype] is not None:
                cards.append(self.__equipments[subtype])
        return cards

    @property
    def length(self):
        length = 0
        for subtype in self.__equipments:
            if self.__equipments[subtype] is not None:
                length += 1
        return length

    @property
    def equipments(self):
        return self.__equipments

    def addCard(self, card, subtype=None):
        if card and card.itemType == 'card' and card.type == 'equip':
            if subtype and subtype in self.__equipments and self.__equipments[subtype] is None:
                self.__equipments[subtype] = card
                card.area = self
            else:
                for type in self.__equipments:
                    if type == card.subtype and self.__equipments[type] is None:
                        self.__equipments[type] = card
                        card.area = self
        # if type(equipments) is not dict:
        #     raise RuntimeError('Must pass a dict')
        # for key, value in equipments.items():
        #     if value.subtype not in ["Weapon", "Armor", "OffensiveHorse", "DenfensiveHorse"] and value.type != 'none':
        #         raise RuntimeError('You can only add a Equipment card or an empty card')
        #     self.__equipments[value.subtype]=value

    def removeCard(self, cards):
        if type(cards) is not list:
            cards = [cards]
        for card in cards:
            for subtype in self.__equipments:
                if self.__equipments[subtype] == card:
                    self.__equipments[subtype] = None
            # if card not in ["weapon", "armor", "defendHorse", "attackHorse"]:
            #     raise RuntimeError("No such type \" " + name + " \" to be removed")
            # self.__equipments[name] = Card()


class JudgementArea(CardSet):
    pass


class PrivateCardSet(CardSet):
    pass

