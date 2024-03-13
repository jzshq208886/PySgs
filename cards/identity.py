from card import Card
from event import *
from skill import *


class Sha(Card):
    name = 'sha'
    type = 'basic'
    natures = ['fire', 'thunder']
    targetNum = 1

    def range(self, player, target):
        return player.targetInRange(target)

    def targetBan(self, player, target):
        return player == target
    usable = 1
    updateTrigger = 'phaseUseAfter'

    # ai
    order = 5.5
    value = 4.5

    def playerResult(self, player, target):
        return 0  # 【杀】对使用者本身无影响

    def targetResult(self, player, target):
        if self.getColor(player) == 'black' and target.hasSkill('renwangSkill'):
            return 0  # 黑色【杀】对装备了【仁王盾】的角色无影响
        if target.hasSkill('baguaSkill'):
            return -1  # 【杀】对装备了【八卦阵】的角色影响较小
        return -1.5  # 【杀】对目标有负面影响


class ShaEffect(CardEvent):
    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0, self.step1, self.step2, self.step3, self.step4, self.step5, self.step6]

    def step0(self):
        if self.directHit:
            self.goto(4)
        else:
            self.target.chooseToUse('请使用一张【闪】响应【杀】', 'shan')

    def step1(self):
        if self.childResult('bool'):
            if self.childResult('shanned'):
                self.respondedCard.append(self.childResult('card'))
            if len(self.respondedCard) < self.neededRespondNum:
                self.goto(0)
        else:
            self.goto(4)

    def step2(self):
        self.trigger('Miss')

    def step3(self):
        self.trigger('Undamage')
        self.finish()

    def step4(self):
        self.trigger('Hit')

    def step5(self):
        self.target.damage(self.damage, self.player, self.card, self.card.nature)

    def step6(self):
        if self.currentChild.name == 'damage' and self.childResult('num') == 0:
            self.goto(3)


class Shan(Card):
    name = 'shan'
    type = 'basic'
    active = False

    order = 1

    def playerResult(self, player, target=None):
        return 1
    value = 7


class ShanEffect(CardEvent):
    def __init__(self, status):
        super().__init__(status)
        self.content.append(self.step0)

    def step0(self):
        self.setResult('shanned', True)
        if self.getParent(2).name == 'chooseToUse':
            self.getParent(2).setResult('shanned', True)


class Tao(Card):
    __itemType = 'card'
    name = 'tao'
    type = 'basic'
    active = True
    targetNum = 1

    def targetBan(self, player, target):
        return not target.isWounded()

    def targetFilter(self, player, target):
        return player == target

    # ai
    order = 3

    def targetResult(self, player, target):
        return 2
    value = 6


class TaoEffect(CardEvent):
    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0]

    def step0(self):
        self.target.recover(1, self.target, self.card)


class Jiu(Card):
    name = 'jiu'
    type = 'basic'

    def targetFilter(self, player, target):
        return player == target

    usable = 1
    updateTrigger = 'phaseAfter'

    order = 6
    value = 4.4

    # ai
    def playerResult(self, player, target):
        return 0

    def targetResult(self, player, target):
        if target.isDying():
            return 2
        if target.countCards('h', {'name': 'sha'}, lambda card: target.getUseValue(card) > 0):
            return 1
        return 0


class JiuEffect(CardEvent):
    def __init__(self, status):
        super().__init__(status)
        self.content.append(self.step0)

    def step0(self):
        target = self.target
        if target.isDying():
            self.target.recover(1, self.player, self.card)
        else:
            self.target.addSkill('zuijiu')
            self.target.drunk += 1


class Juedou(Card):
    name = 'juedou'
    type = 'trick'
    active = True
    targetNum = 1

    def targetBan(self, player, target):
        return player == target
    targetFilter = True

    order = 7
    value = 1

    def playerResult(self, player, target):
        hsx = target.getCards('h')
        hs = player.countCards('h', {'name': 'sha'})
        if len(hsx) > 2 and hs == 0 and hsx[0].number < 6:  # 通过敌方未知牌产生随机
            return -2
        if len(hsx) > 3 and hs == 0:
            return -2
        return -0.5

    def targetResult(self, player, target):
        return -1.5


class JuedouEffect(CardEvent):
    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0, self.step1, self.step2]
        self.__currentTurn = None

    def step0(self):
        self.__currentTurn = self.target

    def step1(self):
        self.__currentTurn.chooseToResponse('请打出一张【杀】响应【决斗】直到一方没有【杀】', 'sha')

    def step2(self):
        if self.childResult('bool'):
            self.__currentTurn = self.player if self.__currentTurn == self.target else self.target
            self.goto(1)
        else:
            self.__currentTurn.damage(1, self.player if self.__currentTurn == self.target else self.target, self.card)


class Guohe(Card):
    name = 'guohe'
    type = 'trick'
    active = True
    targetNum = 1

    def targetBan(self, player, target):
        return target == player or not target.countCards('he')

    # ai
    order = 12
    value = 3.5

    def targetResult(self, player, target):
        return -1


class GuoheEffect(CardEvent):
    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0]

    def step0(self):
        self.room.delay(200)
        self.player.discardTargetCard(self.target, 'hej')


class Shunshou(Card):
    name = 'shunshou'
    type = 'trick'
    active = True
    targetNum = 1
    range = 1

    def targetBan(self, player, target):
        return target == player or not target.countCards('he')

    #
    order = 11
    value = 4

    def playerResult(self, player, target):
        return 1

    def targetResult(self, player, target):
        return -1


class ShunshouEffect(CardEvent):
    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0]

    def step0(self):
        self.room.delay(200)
        self.player.gainTargetCard(self.target, 'hej')


class Wuzhong(Card):
    name = 'wuzhong'
    type = 'trick'
    active = True
    targetNum = 1
    targetBan = False

    def targetFilter(self, player, target):
        return player == target

    order = 8
    value = 3

    def targetResult(self, player, target):
        return 2


class WuzhongEffect(CardEvent):
    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0]

    def step0(self):
        self.target.draw(2)


class Nanman(Card):
    name = 'nanman'
    type = 'trick'
    active = True
    targetNum = -1

    def targetBan(self, player, target):
        return player == target
    targetFilter = True

    # ai
    order = 10

    def targetResult(self, player, target):
        return -1
    value = 1.6


class NanmanEffect(CardEvent):
    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0, self.step1, self.step2, self.step3]

    def step0(self):
        self.target.chooseToResponse('请打出一张【杀】响应【南蛮入侵】', 'sha')

    def step1(self):
        if self.childResult('bool'):
            self.goto(2)
        else:
            self.goto(3)

    def step2(self):
        self.trigger('Miss')
        self.finish()

    def step3(self):
        self.target.damage(self.damage, self.player, self.card, self.card.nature)


class Wanjian(Card):
    name = 'wanjian'
    type = 'trick'
    active = True
    targetNum = -1

    def targetBan(self, player, target):
        return player == target

    targetFilter=True

    order = 10

    def targetResult(self, player, target):
        return -1
    value = 1.5


class WanjianEffect(CardEvent):
    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0, self.step1, self.step2, self.step3]

    def step0(self):
        self.target.chooseToResponse('请打出一张【闪】响应【万箭齐发】', 'shan')

    def step1(self):
        if self.childResult('bool'):
            self.goto(2)
        else:
            self.goto(3)

    def step2(self):
        self.trigger('Miss')
        self.finish()

    def step3(self):
        self.target.damage(self.damage, self.player, self.card, self.card.nature)


class Tiesuo(Card):
    name = 'tiesuo'
    type = 'trick'
    active = True
    targetNum = [1, 2]
    targetBan = False
    targetFilter = True


class TiesuoEffect(CardEvent):
    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0]

    def step0(self):
        self.target.link()


class Zhuge(Card):
    name = 'zhuge'
    type = 'equip'
    subtype = 'weapon'

    def targetResult(self, player, target):
        armor = target.getEquip('weapon')
        if armor and armor.name == self.name:
            return 0
        return 1

    # ai
    order = 2.5
    equipValue = 6


class Guanshi(Card):
    name = 'guanshi'
    type = 'equip'
    subtype = 'weapon'
    skill = 'guanshiSkill'

    def targetResult(self, player, target):
        armor = target.getEquip('weapon')
        if armor and armor.name == self.name:
            return 0
        return 1

    # ai
    order = 9
    equipValue = 5


class GuanshiSkill(TriggerSkill):
    name = 'guanshiSkill'
    equipSkill = True
    locked = True
    forced = True
    trigger = {'player': 'cardEffectMiss'}

    def filter(self, event, player):
        return event.card.name == 'sha' and player.countCards('h') >= 2


class GuanshiSkillInvoke(SkillEvent):
    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0, self.step1]

    def step0(self):
        self.player.chooseToDiscard("是否发动【贯石斧】，弃置两张牌使【杀】强制命中", position='h', selectCardNum=2)

    def step1(self):
        if self.childResult('bool'):
            evt = self.triggerEvent  # self.getParent(4)
            evt.finished = False
            evt.goto(4)


class Bagua(Card):
    name = 'bagua'
    type = 'equip'
    subtype = 'armor'
    skill = 'baguaSkill'

    order = 1

    def targetResult(self, player, target):
        armor = target.getEquip('armor')
        if armor and armor.name == self.name:
            return 0
        return 1

    # ai
    equipValue = 7


class BaguaSkill(TriggerSkill):
    name = 'baguaSkill'
    equipSkill = True
    locked = True
    trigger = {'player': ['chooseToUseBefore', 'chooseToRespondBefore']}
    forced = True

    def filter(self, event, player):
        return event.filterCard(Shan(existence='virtual'))


class BaguaSkillInvoke(SkillEvent):
    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0, self.step1]

    def step0(self):
        self.player.getRoom().delay(300)
        self.player.judge()
    
    def step1(self):
        if self.childResult('color') == 'red':
            self.triggerEvent.responded = True


class Renwang(Card):
    name = 'renwang'
    type = 'equip'
    subtype = 'armor'
    skill = 'renwangSkill'

    order = 1

    def targetResult(self, player, target):
        armor = target.getEquip('armor')
        if armor and armor.name == self.name:
            return 0
        return 1

    # ai
    equipValue = 7


class RenwangSkill(TriggerSkill):
    name = 'renwangSkill'
    equipSkill = True
    locked = True
    trigger = {'target': 'cardEffectBefore'}
    forced = True

    def filter(self, event, player):
        card = event.card
        return card.name == 'sha' and card.getColor(event.player) == 'black'


class RenwangSkillInvoke(SkillEvent):
    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0]

    def step0(self):
        self.room.delay(200)
        self.triggerEvent.cancel()



