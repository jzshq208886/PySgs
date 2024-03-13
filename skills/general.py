from skill import *
from event import SkillEvent


class Zuijiu(TriggerSkill):
    def __init__(self, owner):
        super().__init__(owner)

    name = 'zuijiu'
    isSkill = False
    firstDo = True
    trigger = {'player': 'useCard'}

    def filter(self, event, player):
        # player = self.owner
        return event.card.name == 'sha'
    locked = True
    forced = True

    def initialize(self):
        if not self.owner.drunk:
            self.owner.drunk = 0

    def onRemove(self):
        self.owner.drunk = 0


class ZuijiuInvoke(SkillEvent):
    def __init__(self, status):
        super().__init__(status)
        self.content.append(self.step0)

    def step0(self):
        player = self.player
        self.triggerEvent.baseDamage += player.drunk
        player.removeSkill('zuijiu')


class Huode(TriggerSkill):
    def __init__(self, owner):
        super().__init__(owner)

    name = "huode"
    isSkill = False
    trigger = {'player': 'phaseUseBefore'}
    forced = True


class HuodeInvoke(SkillEvent):
    def __init__(self, status):
        super().__init__(status)
        self.content.append(self.step0)
        self.content.append(self.step1)

    def step0(self):
        needed = []
        cards = []
        for card in self.room.drawPile.cards:
            if card.name in needed:
                cards.append(card)
                needed.remove(card.name)
                if not len(needed):
                    break
        if cards:
            self.player.gain(cards, 'gainAuto')
        # self.player.discard(self.player.handcard)
        # self.player.damage(2)
        # self.player.die()
        # self.player.next.damage(3)
        # self.player.next.discard(self.player.next.handcard)

    def step1(self):
        needed = []
        cards = []
        for card in self.room.drawPile.cards:
            if card.name in needed:
                cards.append(card)
                needed.remove(card.name)
                if not len(needed):
                    break
        # self.player.next.chooseToDiscard(selectCard=4, forced=True)
        if cards:
            self.player.next.gain(cards, 'gainAuto')


class OnPhaseUseAfter(Skill):
    def __init__(self, owner):
        super().__init__(owner)

    name = "onPhaseUseAfter"
    isSkill = False
    firstDo = True
    trigger = {'player': 'phaseUseAfter'}
    filter = True
    forced = True
    locked = True


class OnPhaseUseAfterInvoke(SkillEvent):
    def __init__(self, status):
        super().__init__(status)
        self.content.append(self.step0)

    def step0(self):
        player = self.player
        player.stat['card']['sha'] = 0


class OnPhaseAfter(Skill):
    def __init__(self, owner):
        super().__init__(owner)

    name = "onPhaseAfter"
    isSkill = False
    firstDo = True
    trigger = {'player': 'phaseAfter'}
    filter = True
    forced = True
    locked = True


class OnPhaseAfterInvoke(SkillEvent):
    def __init__(self, status):
        super().__init__(status)
        self.content.append(self.step0)

    def step0(self):
        player = self.player
        player.stat['card']['jiu'] = 0
        player.removeSkill('zuijiu')


class UpdateAI(TriggerSkill):
    name = 'updateAI'
    isSkill = False
    firstDo = True
    trigger = {'global': 'useCard'}

    def filter(self, event, player):
        return player != event.player and player.ai
    locked = True
    forced = True


class UpdateAIInvoke(SkillEvent):
    name = 'updateAIInvoke'

    def __init__(self, status):
        super().__init__(status)
        self.content.append(self.step0)

    def step0(self):
        player, trigger = self.player, self.triggerEvent
        effect = 0
        for target in trigger.targets:
            effect += player.getEffect(trigger.card, trigger.player, target)
        info = player.ai.info[trigger.player]
        if effect > 5:
            info['attitude'] += 2
        elif effect > 0:
            info['attitude'] += 1
        elif effect < 0:
            info['attitude'] += 1
        elif effect < -5:
            if info['attitude'] > 3:
                info['attitude'] = 3
            info['attitude'] -= 2

