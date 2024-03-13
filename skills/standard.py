import random

from skill import *
from event import SkillEvent


# 黄月英〖集智〗：当你使用非延时锦囊牌时，可以摸一张牌。
class Jizhi(TriggerSkill):
    name = 'jizhi'
    trigger = {'player': 'useCard'}

    def filter(self, event, player):  # trigger和filter共同实现“当你使用非延时锦囊牌时”
        # filter里的event为触发事件，这里即useCard事件。
        return event.card.type == 'trick' and event.card.subtype != 'delay'
        # 使用的牌类型为锦囊牌，且 使用的牌的子类型不是延时锦囊牌。

    forced = True


class JizhiInvoke(SkillEvent):
    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0]

    def step0(self):
        self.player.draw()


# 曹操〖奸雄〗：当你受到伤害后，你可以获得对你造成伤害的牌。
class Jianxiong(TriggerSkill):
    name = 'jianxiong'
    trigger = {'player': 'damageAfter'}

    def filter(self, event, player):
        pass
        return event.card.cards
    forced = True


class JianxiongInvoke(SkillEvent):
    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0]

    def step0(self):
        self.room.delay(200)
        self.player.room.broadcastAll(lambda ui: ui.playAudio('jianxiong' + str(random.randint(1, 2))))
        self.player.gain(self.triggerEvent.card.cards)


# 贾亚晖〖师友〗：转换技，阴：当你使用【杀】造成伤害时，你可以弃2张手牌，令此伤害+1；阳：当你受到【杀】的伤害时，你可以弃2张手牌，令此伤害-1。
class Shiyou(TriggerSkill):
    name = 'shiyou'

    def initialize(self):
        self.owner.setStorage('shiyou', 0)

    trigger = {
        'source': 'damage',
        'player': 'damage',
    }

    def filter(self, event, player):
        if player.countCards('h') < 2 or event.card.name != 'sha':
            return False
        if self.owner.storage['shiyou']:
            return event.player == player
        return event.source == player

    forced = True


class ShiyouInvoke(SkillEvent):
    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0, self.step1]

    def step0(self):
        player = self.player
        prompt = '是否发动【师友】，弃2张手牌，令【杀】的伤害' + ('+' if self.triggerEvent.source == player else '-') + '1?'
        player.chooseToDiscard(prompt, 'h', 2)

    def step1(self):
        if self.childResult('bool'):
            player = self.player
            player.setStorage('shiyou', (player.storage['shiyou'] + 1) % 2)
            if self.triggerEvent.source == player:
                self.triggerEvent.num += 1
            else:
                self.triggerEvent.num -= 1


# 贾亚晖〖诲人〗：当其他角色对你使用的【杀】未对你造成伤害时，你可以弃置其一张牌。
class Huiren(TriggerSkill):
    name = 'huiren'

    trigger = {'target': 'cardEffectUndamage'}

    def filter(self, event, player):
        return event.card.name == 'sha' and event.player.countCards('he')

    forced = True


class HuirenInvoke(SkillEvent):
    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0]

    def step0(self):
        self.room.delay(50)
        self.player.discardTargetCard(self.triggerEvent.player)


# 贾亚晖〖才傲〗：一名角色的回合结束时，若你的手牌数为全场最多（或之一），你摸一张牌。
class Caiao(TriggerSkill):
    name = 'caiao'

    trigger = {'global': 'phaseEnd'}

    def filter(self, event, player):
        for current in player.room.players:
            if current.handcardNum > player.handcardNum:
                return False
        return True

    forced = True


class CaiaoInvoke(SkillEvent):
    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0]

    def step0(self):
        self.player.draw()
