class Skill:
    __itemType = 'skill'

    name = 'blankSkill'  # 技能名，规定将类名首字母小写作为技能名，方便统一化创建技能
    skillType = 'general'  # 技能分为触发技'trigger'，主动技'enable'，mod技'mod'
    isSkill = True  # 是否为技能，若为False则说明是以技能形式实现的效果，不会显示
    equipSkill = False  # 是否为装备技能

    # 玩家获得技能时进行的操作
    def initialize(self):
        pass

    # 玩家失去技能时进行的操作
    def onRemove(self):
        pass

    firstDo = False  # 是否优先发动
    locked = False  # 是否为锁定技
    filter = True  # 判断是否可发动用的过滤器，可为bool值或函数
    usable = 999  # 每回合可使用次数
    forced = False  # 是否强制发动
    forceDie = False  # 死亡后是否仍然有效

    prompt = '请选择'  # 发动提示语
    selectCard = False  # 发动需要的牌数
    cardFilter = False  # 发动需要的牌的种类过滤器，可为bool值或函数
    position = 'he'  # 发动需要的牌的位置
    discard = True  # 是否弃置发动技能用的牌
    selectTarget = False  # 技能的目标范围
    targetFilter = False  # 技能可指定目标的过滤器，可为bool值或函数
    multiTarget = False  # 暂未实装

    complexSelect = False  # 暂未实装

    def __init__(self, owner=None):
        self.__content = []
        self.__temp = False
        self.__used = 0
        self.__owner = owner

    @property
    def itemType(self):
        return self.__itemType

    @property
    def temp(self):
        return self.__temp

    @temp.setter
    def temp(self, value):
        if value == 'temp':
            self.__temp = True
        self.__temp = value

    @property
    def owner(self):
        return self.__owner

    @owner.setter
    def owner(self, value):
        self.__owner = value

    @property
    def used(self):
        return self.__used

    @used.setter
    def used(self, value):
        self.__used = value

    def canInvoke(self, event, player):
        if type(self.usable) is int and self.__used >= self.usable:
            return False

        if type(self.filter) is bool:
            return self.filter
        if callable(self.filter):
            return self.filter(event, player)
        print('Warning: Skill filter is neither bool nor method!')
        return True

    @property
    def needCard(self):
        if callable(self.selectCard):
            return self.selectCard()
        if type(self.selectCard) is bool or list:
            return self.selectCard
        return [self.selectCard, self.selectCard]

    def filterCard(self, card):
        if callable(self.cardFilter):
            return self.cardFilter(card)
        if type(self.cardFilter) is str:
            return card.name == self.cardFilter
        if type(self.cardFilter) is list:
            return card.name in self.cardFilter
        return self.cardFilter

    @property
    def needTarget(self):
        if callable(self.selectTarget):
            return self.selectTarget()
        if type(self.selectTarget) is bool or list:
            return self.selectTarget
        return [self.selectTarget, self.selectTarget]

    # enable
    def filterTarget(self, target):
        if callable(self.targetFilter):
            return self.targetFilter(target)
        if type(self.targetFilter) is bool:
            return self.targetFilter
        if type(self.targetFilter) is list:
            return target in self.targetFilter
        return target == self.targetFilter


class TriggerSkill(Skill):
    name = 'generalTriggerSkill'
    skillType = 'trigger'
    trigger = {}  # 触发技的触发时机。字典的键为玩家在事件中的身份地位，值为事件名（+时机后缀）。
    # 如：{'player': 'useCard'}，意为玩家使用牌时，'useCard'为事件名，无后缀；
    # {'player': 'damegeAfter'}，意为玩家 受到 伤害后，'damage'为事件名，'After'为时机后缀；
    # {'source': 'damageAfter'}，意为玩家 造成 伤害后，
    #                           'source'意为玩家在'damage'事件中作为变量source（伤害来源）的值；
    # {'player': 'useCardToTargetBefore'}，玩家使用牌指定目标前；
    # {'target': 'useCardToTargetAfter'}，玩家被指定为目标后，玩家在'useCardToTarget'事件中作为target；
    # {'player': 'phaseEnd'}，玩家回合结束时。常用时机后缀：'Before'，'Begin'，'End'和'After'
    # {'global': 'phaseJieshuBegin'}，任意角色结束阶段开始时。若键为'global'，表示场上任意角色的该事件；
    # {'global': 'loseAfter'}，任意角色失去牌后。
    # 触发技一般用trigger和父类成员filter共同决定技能在什么时机、什么情况下可以发动。

    def __init__(self, owner):
        super().__init__(owner)

