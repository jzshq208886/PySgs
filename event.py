import lib.ai as libAI


class Event:
    __itemType = 'event'
    eventType = 'generalEvent'
    name = 'blankEvent'
    noTrigger = False
    triggerTimes = {'Before': 1, 'Begin': 1, 'End': 1, 'After': 1}

    def __init__(self, status):
        self.__status = status
        self.__room = status.room
        self.__content = []
        self.__player = None
        self.__target = None
        self.__targets = []
        self.__source = None
        self.__card = None
        self.__cards = []
        self.__num = 0
        self.__skill = None
        self.__pattern = 'defaultPattern'
        self.type = None
        self.__result = {'bool': False, 'card': None, 'cards': [], 'target': None, 'targets': [], 'index': 0,
                         'control': '', 'skill': None, 'responded': False}
        self.__parent = status.currentEvent
        # print('b:', self.__name, self.__parent)
        self.__next = []
        self.__nextIndex = 0
        self.__step = 0
        self.__finished = False
        self.__canceled = False
        self.__storage = {}

    @property
    def itemType(self):
        return self.__itemType

    @property
    def status(self):
        return self.__status

    @property
    def room(self):
        return self.__room

    @property
    def content(self):
        return self.__content

    @content.setter
    def content(self, value):
        self.__content = value

    @property
    def player(self):
        return self.__player

    @player.setter
    def player(self, value):
        self.__player = value

    @property
    def target(self):
        return self.__target

    @target.setter
    def target(self, player):
        self.__target = player

    # target = property(getTarget, setTarget)

    @property
    def source(self):
        return self.__source

    @source.setter
    def source(self, player):
        self.__source = player

    @property
    def targets(self):
        return self.__targets

    @targets.setter
    def targets(self, lst):
        if type(lst) is list:
            self.__targets = lst.copy()
        else:
            self.__targets = [lst]

    @property
    def card(self):
        return self.__card

    @card.setter
    def card(self, v):
        self.__card = v

    @property
    def cards(self):
        return self.__cards

    @cards.setter
    def cards(self, lst):
        if type(lst) is list:
            self.__cards = lst.copy()
        else:
            self.__cards = [lst]

    @property
    def skill(self):
        return self.__skill

    @skill.setter
    def skill(self, value):
        self.__skill = value

    @property
    def num(self):
        return self.__num

    @num.setter
    def num(self, v):
        self.__num = v

    @property
    def pattern(self):
        return self.__pattern

    @pattern.setter
    def pattern(self, v):
        self.__pattern = v

    @property
    def parent(self):
        return self.__parent

    @property
    def next(self):
        return self.__next

    @property
    def currentChild(self):
        if self.__nextIndex:
            return self.__next[self.__nextIndex - 1]
        return None

    @property
    def finished(self):
        return self.__finished

    @finished.setter
    def finished(self, value):
        self.__finished = value

    @property
    def storage(self):
        return self.__storage

    def addToNext(self):
        if self.__status.currentEvent:
            self.__status.currentEvent.pushNext(self)
        else:
            self.__status.next.append(self)

    def result(self, arg: str = None):
        if arg is None:
            return self.__result
        if arg not in self.__result:
            return None
        return self.__result[arg]

    def setResult(self, arg: str, element):
        if type(element) is list:
            self.__result[arg] = element.copy()
        else:
            self.__result[arg] = element

    def getParent(self, num=None):
        if num is None:
            num = 1

        parent = self.__parent
        if type(num) is str:
            while parent and parent.name != num:
                parent = parent.parent
        else:
            while parent and num > 1:
                parent = parent.parent
                num -= 1
        return parent

    def pushNext(self, event):
        self.__next.append(event)

    def childResult(self, arg: str = None):
        if self.currentChild:
            if arg:
                return self.currentChild.result(arg)
            return self.currentChild.result()

    def log_text(self):
        text = ''
        completetext = ''
        currentEvent = self.__status.currentEvent
        trans = self.room.translateTable
        if isinstance(currentEvent, Phase):
            text += "新回合开始：\n"
        if isinstance(currentEvent, Judge):
            if 'color' in currentEvent.result():
                text += "执行判定，判定颜色为：" + trans[currentEvent.result()['color']] + '\n'
        # if isinstance(currentEvent,Draw):
        #     text+=self.log_trans[self.__player.name]+"获得牌："
        #     for i in currentEvent.cards: text+=self.log_trans[i.name]+'，'
        #     text+='\n'
        if isinstance(currentEvent, Gain):
            text += trans[self.__player.name] + "获得牌："
            if len(currentEvent.cards) == 1:
                text += trans[currentEvent.cards[0].name]
            else:
                for i in range(len(currentEvent.cards) - 1):
                    text += trans[currentEvent.cards[i].name] + '，'
                text += trans[currentEvent.cards[-1].name]
            text += '\n'
        if isinstance(currentEvent, UseCard):
            text += trans[self.__player.name]
            if len(currentEvent.cards) != 0:
                text += "对"
                if len(currentEvent.cards) == 1:
                    text += trans[currentEvent.targets[0].name]
                else:
                    for i in range(len(currentEvent.targets) - 1):
                        text += trans[currentEvent.targets[i].name] + '，'
                    text += trans[currentEvent.targets[-1].name]
            text += '使用了' + '【' + trans[self.__card.name] + '】' + '\n'
        if isinstance(currentEvent, UseSkill):
            if self.__skill.isSkill:
                text += trans[self.__player.name] + '技能发动：〖' + trans[self.__skill.name] + '〗\n'

        if isinstance(currentEvent, Discard):
            text += trans[self.__player.name] + "丢弃牌："
            if len(currentEvent.cards) == 1:
                text += trans[currentEvent.cards[0].name]
            elif currentEvent.cards:
                for i in range(len(currentEvent.cards) - 1):
                    text += trans[currentEvent.cards[i].name] + '，'
                text += trans[currentEvent.cards[-1].name]
            text += '\n'
        if isinstance(currentEvent, Damage):
            text += trans[self.__player.name] + '受到' + str(currentEvent.num) + '点伤害,' + \
                    '剩余血量：' + str(currentEvent.player.hp - currentEvent.num) + '\n'
        if isinstance(currentEvent, Equip):
            text += trans[self.__player.name] + '装备' + trans[self.__card.name] + '\n'

        if isinstance(currentEvent, Die):
            text += trans[self.__player.name] + '死亡'

        if isinstance(currentEvent, Respond):
            text += '打出了' + '【' + trans[self.__card.name] + '】' + '\n'

        completetext += "player:" + self.__player.name + '\n'
        completetext += 'current:' + str(currentEvent) + '\n'
        if self.__card:
            completetext += 'card:' + self.__card.name + '\n'
        if self.__skill:
            completetext += 'skill:' + self.__skill.name + '\n'
        completetext += '\n'
        return text, completetext

    def process(self):
        # 设置参数
        self.__status.currentEvent = self

        result = self.__room.result
        # if self.name != 'trigger':
        #     text, completeText = self.log_text()
        #     with open('log.txt', mode='a+', encoding='utf-8') as f:
        #         f.write(text)
        #     with open('complete_log.txt', mode='a+', encoding='utf-8') as f:
        #         f.write(completeText)
        #     print('eventProcess:', self.__player.name if self.__player else '', self.name,
        #           self.__card.name if self.__card else '', self.__skill.name if self.__skill else '')
        #     print()

        # 触发技时机
        if not self.noTrigger:
            self.trigger('Before')
            self.processNext()
            if self.__canceled or result['gameOver'] or result['gameInterrupted']:
                self.__status.currentEvent = self.__parent
                return

            self.trigger('Begin')
            self.processNext()
            if self.__canceled or result['gameOver'] or result['gameInterrupted']:
                self.__status.currentEvent = self.__parent
                return

        # 事件内容执行
        while not self.__finished and self.__step < len(self.__content):
            # self.trigger(str(self.__step))
            self.__step += 1
            self.__content[self.__step - 1]()
            self.processNext()
            if self.__canceled or result['gameOver'] or result['gameInterrupted']:
                self.__status.currentEvent = self.__parent
                return

        # 触发技时机
        if not self.noTrigger:
            self.trigger('End')
            self.processNext()
            if self.__canceled or result['gameOver'] or result['gameInterrupted']:
                self.__status.currentEvent = self.__parent
                return
            self.trigger('After')
            self.processNext()
            if self.__canceled or result['gameOver'] or result['gameInterrupted']:
                self.__status.currentEvent = self.__parent
                return

        self.__status.currentEvent = self.__parent

    def processNext(self):
        while self.__nextIndex < len(self.__next):
            if self.__next[self.__nextIndex].name not in ['trigger', 'chooseToInvoke', 'updateAIInvoke']:
                # with open('log.txt', mode='a+', encoding='utf-8') as f:
                #     text1 = 'current:' + str(self.__status.currentEvent) + '\n'
                #     f.write(text1)
                #     text2 = 'next' + ' ' + str(self.__next[self.__nextIndex]) + '\n'
                #     f.write(text2)
                print('current:', self.__status.currentEvent)
                # print('nextIndex', self.__nextIndex)
                print('next', self.__next[self.__nextIndex])
                print()
            self.__next[self.__nextIndex].process()
            if self.__room.result['gameOver'] or self.__room.result['gameInterrupted']:
                return
            self.__nextIndex += 1

    def trigger(self, moment=''):
        next = self.__status.addEvent('trigger')
        next.triggerEvent = self
        next.triggerMoment = self.name + moment
        return next

    def isFinished(self):
        return self.__finished

    def finish(self):
        self.__finished = True

    def isCanceled(self):
        return self.__canceled

    def cancel(self):
        self.__canceled = True

    def setStorage(self, arg, element):
        self.__storage[arg] = element

    def addStorage(self, arg, num=1):
        if arg in self.__storage and type(self.__storage[arg]) is int:
            self.__storage[arg] += num

    def appendStorage(self, arg, element):
        if arg in self.__storage and type(self.__storage[arg]) is list:
            self.__storage[arg].append(element)

    def goto(self, step):
        self.__step = step

    def redo(self):
        self.__step -= 1


class PhaseEvent(Event):
    eventType = 'phaseEvent'

    def __init__(self, status):
        super().__init__(status)
        self.__extra = False

    @property
    def extra(self):
        return self.__extra

    @extra.setter
    def extra(self, value):
        self.__extra = value


class ChooseEvent(Event):
    eventType = 'chooseEvent'

    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0]
        self.__prompt = '请选择'
        self.__cardFilter = False
        self.__selectCardNum = [1, 1]
        self.__position = 'he'
        self.__targetFilter = False
        self.__selectTargetNum = [1, 1]
        self.__multiTarget = False
        self.__complexSelect = False
        self.__forced = False
        self.__skill = None

        self.responded = False
        self.respondTo = {'player': None, 'card': []}

        self.__cardAI = 0
        self.__targetAI = 0
        self.__buttonAI = 0
        self.__complexCardAI = False
        self.__complexTargetAI = False
        self.__complexButtonAI = False
        self.__complexCardSet = []
        self.__complexTargetSet = []
        self.__complexButtonSet = []

    @property
    def prompt(self):
        return self.__prompt

    @prompt.setter
    def prompt(self, value):
        self.__prompt = value

    @property
    def cardFilter(self):
        return self.__cardFilter

    @cardFilter.setter
    def cardFilter(self, value):
        self.__cardFilter = value

    def filterCard(self, card):
        # print('chooseEvent-filterCard')
        if callable(self.__cardFilter):
            # print('chooseEvent-filterCard1')
            return self.__cardFilter(card)
        if type(self.__cardFilter) is str:
            # print('chooseEvent-filterCard2')
            return card.name == self.__cardFilter
        if type(self.__cardFilter) is list:
            # print('chooseEvent-filterCard3')
            return card.name in self.__cardFilter
        # print('chooseEvent-filterCard4')
        return self.__cardFilter

    @property
    def selectCardNum(self):
        if callable(self.__selectCardNum):
            return self.__selectCardNum()
        return self.__selectCardNum

    @selectCardNum.setter
    def selectCardNum(self, value):
        if type(value) is int:
            self.__selectCardNum = [value, value]
        else:
            self.__selectCardNum = value

    @property
    def position(self):
        if callable(self.__position):
            return self.__position()
        return self.__position

    @position.setter
    def position(self, value):
        self.__position = value

    def setPosition(self, position):
        self.__position = position

    @property
    def targetFilter(self):
        return self.__targetFilter

    @targetFilter.setter
    def targetFilter(self, value):
        self.__targetFilter = value

    def filterTarget(self, target):
        if callable(self.__targetFilter):
            return self.__targetFilter(target)
        if type(self.__targetFilter) is bool:
            return self.__targetFilter
        if type(self.__targetFilter) is list:
            return target in self.__targetFilter
        return target == self.__targetFilter

    @property
    def selectTargetNum(self):
        if callable(self.__selectTargetNum):
            return self.__selectTargetNum()
        return self.__selectTargetNum

    @selectTargetNum.setter
    def selectTargetNum(self, value):
        if type(value) is int:
            self.__selectTargetNum = [value, value]
        else:
            self.__selectTargetNum = value

    def multiTarget(self, player=None):
        if callable(self.__multiTarget):
            if player is None:
                player = self.player
            return self.__multiTarget(player)
        return self.__multiTarget

    def setMultiTarget(self, multiTarget=True):
        self.__multiTarget = multiTarget

    @property
    def complexSelect(self):
        if callable(self.__complexSelect):
            return self.__complexSelect()
        return self.__complexSelect

    @complexSelect.setter
    def complexSelect(self, value):
        self.__complexSelect = value

    @property
    def forced(self):
        return self.__forced

    @forced.setter
    def forced(self, v: bool):
        self.__forced = v

    @property
    def skill(self):
        return self.__skill

    @skill.setter
    def skill(self, value):
        self.__skill = value

    @property
    def cardAI(self):
        return self.__cardAI

    @cardAI.setter
    def cardAI(self, value):
        self.__cardAI = value

    @property
    def targetAI(self):
        return self.__targetAI

    @targetAI.setter
    def targetAI(self, value):
        self.__targetAI = value

    @property
    def buttonAI(self):
        return self.__buttonAI

    @buttonAI.setter
    def buttonAI(self, value):
        self.__buttonAI = value

    def checkCard(self, card):
        if callable(self.__cardAI):
            # print('ChooseEvent.checkCard,', 'cardAI callable,', self.__cardAI, self.__cardAI(card))
            return self.__cardAI(card)
        # print('ChooseEvent.checkCard,', 'cardAI uncallable,', self.__cardAI)
        return self.__cardAI

    def checkTarget(self, target):
        if callable(self.__targetAI):
            return self.__targetAI(target)
        return self.__targetAI

    def checkButton(self, button):
        if callable(self.__buttonAI):
            return self.__buttonAI(button)
        return self.__buttonAI

    @property
    def complexCardAI(self):
        return self.__complexCardAI

    @complexCardAI.setter
    def complexCardAI(self, value):
        self.__complexCardAI = value

    @property
    def complexTargetAI(self):
        return self.__complexTargetAI

    @complexTargetAI.setter
    def complexTargetAI(self, value):
        self.__complexTargetAI = value

    @property
    def complexButtonAI(self):
        return self.__complexButtonAI

    @complexButtonAI.setter
    def complexButtonAI(self, value):
        self.__complexButtonAI = value

    @property
    def complexCardSet(self):
        return self.__complexCardSet

    @complexCardSet.setter
    def complexCardSet(self, value):
        self.__complexCardSet = value

    @property
    def complexTargetSet(self):
        return self.__complexTargetSet

    @complexTargetSet.setter
    def complexTargetSet(self, value):
        self.__complexTargetSet = value

    @property
    def complexButtonSet(self):
        return self.__complexButtonSet

    @complexButtonSet.setter
    def complexButtonSet(self, value):
        self.__complexButtonSet = value

    def step0(self):
        self.player.makeChoice(self)


class CardEvent(Event):
    eventType = 'cardEvent'
    name = 'cardEffect'

    def __init__(self, status):
        super().__init__(status)
        self.__addedTarget = {}
        self.__directHit = False
        # self.__responded = False
        self.__respondedCard = []
        self.__neededRespondNum = 1
        self.__damage = 1

    def addedTarget(self, target=None):
        if target is None:
            return self.__addedTarget
        if target in self.__addedTarget:
            return self.__addedTarget[target]
        return None

    def setAddedTarget(self, target, addedTarget):
        self.__addedTarget[target] = addedTarget

    @property
    def directHit(self):
        return self.__directHit

    @directHit.setter
    def directHit(self, value):
        self.__directHit = value

    @property
    def respondedCard(self):
        return self.__respondedCard

    @property
    def neededRespondNum(self):
        return self.__neededRespondNum

    @neededRespondNum.setter
    def neededRespondNum(self, value):
        self.__neededRespondNum = value

    @property
    def damage(self):
        return self.__damage

    @damage.setter
    def damage(self, value):
        self.__damage = value


class SkillEvent(Event):
    eventType = "skillEvent"
    name = "skillInvoke"

    def __init__(self, status):
        super().__init__(status)
        self.__triggerEvent = None

    @property
    def triggerEvent(self):
        return self.__triggerEvent

    @triggerEvent.setter
    def triggerEvent(self, value):
        self.__triggerEvent = value


class Trigger(Event):
    name = 'trigger'
    noTrigger = True

    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0, self.step1, self.step2]
        self.__triggerEvent = None
        self.__triggerMoment = 'none'
        # self.__skill = {}
        self.__playerToInvoke = self.room.targetSort()
        self.__playerIndex = 0
        self.__invoked = []

    @property
    def triggerEvent(self):
        return self.__triggerEvent

    @triggerEvent.setter
    def triggerEvent(self, value):
        self.__triggerEvent = value

    @property
    def triggerMoment(self):
        return self.__triggerMoment

    @triggerMoment.setter
    def triggerMoment(self, value):
        self.__triggerMoment = value

    def skillFilter(self, skill, player):
        if skill.trigger is None or skill in self.__invoked:
            return False

        event = self.__triggerEvent
        player = self.__playerToInvoke[self.__playerIndex]
        # 判断时机：
        # 1.技能时机中包含事件时机
        # 2.该时机的主体为global，或主体对应的事件属性为技能拥有者
        for key in skill.trigger.keys():
            # print('dict:', event.__dict__)
            skillTrigger = skill.trigger[key]
            if ((type(skillTrigger) is list and self.__triggerMoment in skill.trigger[key])
                or (type(skillTrigger) is str and skill.trigger[key] == self.__triggerMoment)) \
                    and (key == 'global' or event.__dict__['_Event__' + key] == player):
                if skill.canInvoke(event, player):
                    # self.room.delay(1000)
                    return True
        return False

    def step0(self):
        player = self.__playerToInvoke[self.__playerIndex]

        # 下一个角色条件: 无可发动技能/选择不发动技能/角色死亡
        if not player.isAlive():
            self.goto(2)

        skill = list(filter(lambda skl: skl.firstDo and self.skillFilter(skl, player),
                            player.getSkill('trigger') + self.room.globalSkill))
        if not skill:
            skill = list(
                filter(lambda skl: self.skillFilter(skl, player), player.getSkill('trigger') + self.room.globalSkill))

        if skill:
            player.chooseToInvoke(skill).triggerEvent = self.__triggerEvent
        else:
            self.goto(2)

    def step1(self):
        if self.childResult('bool'):
            self.__invoked.append(self.childResult('skill'))
            self.goto(0)

    # 下一人chooseToInvoke，或结束trigger
    def step2(self):
        self.__playerIndex += 1
        if self.__playerIndex < len(self.__playerToInvoke):
            self.goto(0)


class Phase(PhaseEvent):
    name = 'phase'

    def __init__(self, status):
        super().__init__(status)
        self.content.append(self.step0)
        self.__phases = ['phasePrepare', 'phaseJudge', 'phaseDraw', 'phaseUse', 'phaseDiscard', 'phaseFinish']
        self.__phaseIndex = 0

    def step0(self):
        if not self.player.isAlive():
            self.cancel()
            return
        self.room.currentPhase = self.player
        if self.__phaseIndex < len(self.__phases):
            self.player.phaseStage(self.__phases[self.__phaseIndex])
            self.redo()
        self.__phaseIndex += 1


class PhasePrepare(PhaseEvent):
    name = 'phasePrepare'

    def __init__(self, status):
        super().__init__(status)


class PhaseJudge(PhaseEvent):
    name = 'phaseJudge'

    def __init__(self, status):
        super().__init__(status)


class PhaseDraw(PhaseEvent):
    name = 'phaseDraw'

    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0]
        self.num = 2

    def step0(self):
        self.player.draw(self.num)

    # def step1(self):
    #     if self.room.allPlayers[1].isAlive():
    #         self.room.allPlayers[1].die()


class PhaseUse(PhaseEvent):
    name = 'phaseUse'

    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0, self.step1]

    def step0(self):
        self.player.chooseToUse(phaseUse=True)

    def step1(self):
        if self.player.isAlive() and self.childResult('bool'):
            self.goto(0)


class PhaseDiscard(PhaseEvent):
    name = 'phaseDiscard'

    def __init__(self, status):
        super().__init__(status)
        self.content.append(self.step0)

    def step0(self):
        num = self.player.countCards('h') - self.player.handcardLimit
        if num > 0:
            self.player.chooseToDiscard('弃牌阶段，请弃置' + str(num) + '张牌', 'h', num, forced=True)


class PhaseFinish(PhaseEvent):
    name = 'phaseFinish'

    def __init__(self, status):
        super().__init__(status)


class Draw(Event):
    name = 'draw'

    def __init__(self, status):
        super().__init__(status)
        self.content.append(self.step0)
        self.__visible = False
        self.__bottom = False

    @property
    def visible(self):
        return self.__visible

    @visible.setter
    def visible(self, v):
        self.__visible = v

    @property
    def bottom(self):
        return self.__bottom

    @bottom.setter
    def bottom(self, v):
        self.__bottom = v

    def step0(self):
        if self.num == 0:
            self.cancel()
            return
        self.cards = self.room.getCards(self.num)
        self.player.gain(self.cards, 'draw')


class Gain(Event):
    name = 'gain'

    def __init__(self, status):
        super().__init__(status)
        self.content.append(self.step0)
        self.__visible = None

    @property
    def visible(self):
        if self.__visible is None:
            if self.pattern in []:  # pass
                return True
            return False
        return self.__visible

    @visible.setter
    def visible(self, value):
        self.__visible = value

    def step0(self):
        room, cards, player = self.room, self.cards, self.player

        if not cards:
            print('Warning: Gain: length of event.cards is zero!')
            self.cancel()
            return

        origins = {}
        for ui in room.ui:
            origin = []
            for card in cards:
                origin.append(ui.getCoordinate(card))
            origins[ui] = origin

        forceVisible = False
        if cards:
            if not self.source:
                self.source = cards[0].owner
            if cards[0].position in ['t', 'e', 'd']:
                forceVisible = True

        if not self.source:
            for card in cards:
                if card.area:
                    card.area.removeCard(card)
                    if card.area.positionType == 't':
                        self.room.broadcastAll(lambda ui: ui.removeHandling(card))

        player.handcardArea.addCard(cards)
        for ui in room.ui:
            visible = (forceVisible or self.__visible or ui.me == player or ui.me == self.source)
            for i in range(len(cards)):
                ui.setMovement(cards[i], origins[ui][i], ui.getCoordinate(cards[i]), visible=visible)
        # print(len(self.player().getHandcardsArea().cards()))
        # self.room().getUI().display()
        if self.source:
            self.source.lose(self.cards)

        room.delay(100)
        # for ui in room.ui:
        #     ui.wait(100)


class Discard(Event):
    name = 'discard'

    def __init__(self, status):
        super().__init__(status)
        self.content.append(self.step0)

    def step0(self):
        if not len(self.cards):
            self.cancel()
            return
        self.player.loseCardTo(self.cards, self.room.discardPile, 'discard')


class Lose(Event):
    name = 'lose'

    def __init__(self, status):
        super().__init__(status)
        self.content.append(self.step0)
        self.__handcard = []
        self.__equip = []

    def step0(self):
        player = self.player
        for card in self.cards:
            if card in player.handcard:
                player.handcardArea.removeCard(card)
                self.num += 1
                self.__handcard.append(card)
            elif card in player.equipArea.cards:
                player.equipArea.removeCard(card)
                self.num += 1
                player.removeSkill(card.skill)
                self.__equip.append(card)


class Insert(Event):
    name = 'insert'

    def __init__(self, status):
        super().__init__(status)
        self.content.append(self.step0)
        self.pile = None

    def step0(self):
        pass


class UseCard(Event):
    name = 'useCard'

    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0, self.step1, self.step2, self.step3, self.step4, self.step5, self.step6]
        self.__targetIndex = 0
        self.__addedTarget = {}
        self.__baseDamage = 1

    @property
    def baseDamage(self):
        return self.__baseDamage

    @baseDamage.setter
    def baseDamage(self, value):
        self.__baseDamage = value

    @property
    def cards(self):
        return self.card.cards

    @property
    def targetIndex(self):
        return self.__targetIndex

    def addedTarget(self, target=None):
        if target is None:
            return self.__addedTarget
        if target in self.__addedTarget:
            return self.__addedTarget[target]
        return None

    def setAddedTarget(self, target, addedTarget):
        self.__addedTarget[target] = addedTarget

    def step0(self):
        card, player = self.card, self.player

        name = 'equip1'
        if card.type == 'equip':
            if card.subtype == 'armor':
                name = 'equip2'
            elif card.subtype == 'defendHorse' or card.subtype == 'attackHorse':
                name = 'equip3'
        else:
            name = card.name + (('_' + card.nature) if card.nature else '') + '_' + self.player.sex
        self.room.broadcastAll(lambda ui: ui.playAudio(name))

        if not card.multiTarget:
            self.room.targetSort(self.targets)

        if card.name in player.stat['card']:
            if card.name != 'jiu' or not player.isDying():
                player.stat['card'][card.name] += 1

        if card.isVirtual():
            return
        if card.cards[0].owner:
            if player.seat == 3:
                print()
            pass  # 忽略牌为不同出处的情况
            card.cards[0].owner.loseCardTo(card.cards, 'handleArea', 'use')
        else:
            self.room.moveCardTo(card.cards, 'handleArea', 'use')

    def step1(self):
        self.trigger()

    def step2(self):
        self.trigger('1')
        if self.card.active and not len(self.targets):
            self.finish()

    def step3(self):
        self.setResult('bool', True)
        if self.card.active:
            self.player.useCardToTarget(self.card, self.targets)
        else:
            self.card.effect(self.player)
            self.goto(6)

    def step4(self):
        self.targets = self.room.targetSort(self.childResult('targets'))

    def step5(self):
        targets = self.targets
        next = self.card.effect(self.player, targets[self.__targetIndex], self.__addedTarget)
        next.damage = self.baseDamage
        self.__targetIndex += 1
        if self.__targetIndex < len(targets):
            self.redo()

    def step6(self):
        # 这里应在全局技能里写
        pass
        self.room.broadcastAll(lambda ui: ui.setHandlingClock(self.card.cards, 500))
        self.room.moveCardTo(list(filter(lambda card: card in self.room.handleArea, self.cards)), 'd', 'useAfter', True)


class UseCardToTarget(Event):
    name = 'useCardToTarget'

    def __init__(self, status):
        super().__init__(status)
        self.content.extend([self.step0, self.step1])

    def step0(self):
        self.trigger()

    def step1(self):
        self.setResult('targets', self.targets)


class UseSkill(Event):
    name = 'useSkill'

    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0, self.step1]
        self.__triggerEvent = None

    @property
    def triggerEvent(self):
        return self.__triggerEvent

    @triggerEvent.setter
    def triggerEvent(self, value):
        self.__triggerEvent = value

    def step0(self):
        skill = self.skill
        skill.used += 1
        if skill.needCard and skill.discard:
            self.player.discard(self.childResult('card'))

    def step1(self):
        self.player.skillInvoke(self.skill, self.cards, self.targets).triggerEvent = self.triggerEvent


class Respond(Event):
    name = 'respond'

    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0, self.step1, self.step2]

    @property
    def cards(self):
        return self.card.cards

    def step0(self):
        card = self.card
        if card.isVirtual():
            return
        if card.cards[0].owner:
            pass  # 忽略牌为不同出处的情况
            card.cards[0].owner.loseCardTo(card.cards, 'handleArea', 'respond')
        else:
            self.room.moveCardTo(card.cards, 'handleArea')
        name = card.name + '_' + self.player.sex
        self.room.broadcastAll(lambda ui: ui.playAudio(name))

    def step1(self):
        self.trigger()

    def step2(self):
        self.setResult('bool', True)
        self.room.moveCardTo(list(filter(lambda card: card in self.room.handleArea, self.cards)), 'd', 'respondAfter', True)


class Damage(Event):
    name = 'damage'
    # triggerTimes = {'Before': 4, 'Begin': 1, 'End': 1, 'After': 1}

    def __init__(self, status):
        super().__init__(status)
        self.content.extend([self.step0, self.step1])
        self.__nature = 'none'

    @property
    def nature(self):
        return self.nature

    @nature.setter
    def nature(self, value):
        self.__nature = value

    def setUI(self, ui):
        ui.commonClock['damage'][self.player] = 100
        ui.commonClockContent['damage'][self.player] = str(-self.num)
        if self.num > 0:
            ui.playAudio('damage')

    def step0(self):
        self.trigger()

    def step1(self):
        self.player.changeHp(-self.num, self.source, self.card)
        self.setResult('num', self.num)
        self.room.broadcastAll(self.setUI)


class Recover(Event):
    name = 'recover'

    def __init__(self, status):
        super().__init__(status)
        self.content.append(self.step0)

    def setUI(self, ui):
        ui.commonClock['recover'][self.player] = 100
        ui.commonClockContent['recover'][self.player] = '+' + str(self.num)
        ui.playAudio('recover')

    def step0(self):
        self.player.changeHp(self.num, self.source)
        self.room.broadcastAll(self.setUI)

    def step1(self):
        self.trigger()


class ChangeHp(Event):
    name = 'changeHp'

    def __init__(self, status):
        super().__init__(status)
        self.content.extend([self.step0, self.step1, self.step2])

    def step0(self):
        if self.num > self.player.lostHp:
            self.num = self.player.lostHp
        self.player.hp += self.num

    def step1(self):
        self.trigger()

    def step2(self):
        if self.player.hp <= 0 and not self.player.isDying():
            self.player.dying(self.source, self.card)


class Dying(Event):
    name = 'dying'

    def __init__(self, status):
        super().__init__(status)
        self.content.extend([self.step0, self.step1, self.step2, self.step3])
        self.saviorIndex = 0
        self.savior = self.room.targetSort()

    def step0(self):
        pass  # skill
        self.player.setDying(True)
        self.trigger()

    def step1(self):
        player = self.player
        room = player.getRoom()
        cards = ['tao', 'jiu'] if self.savior[self.saviorIndex] == player else ['tao']
        next = self.savior[self.saviorIndex].chooseToUse(
            room.translate(player.name) + f'濒死，是否帮助？（当前体力：{player.hp}）', cards, player)
        next.ignoreFilter = True

    def step2(self):
        if self.player.hp <= 0:
            if not self.childResult('bool'):
                self.saviorIndex += 1

            if self.saviorIndex < len(self.savior):
                self.goto(1)
            else:
                self.player.die(self.source, self.card)

    def step3(self):
        self.player.setDying(False)


class Die(Event):
    name = 'die'

    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0, self.step1, self.step2, self.step3]

    def setUI(self, ui):
        audio = self.player.name + '_die'
        if audio in ui.audio:
            ui.playAudio(audio)
        else:
            ui.playAudio('gameStart')

    def step0(self):
        player, room = self.player, self.room
        player.alive = False
        room.removeDeadPlayer(player)
        if player == room.currentPhase:
            evt = self.getParent('phase')
            evt.cancel()
            for stage in evt.next:
                stage.cancel()

        room.broadcastAll(self.setUI)

        room.judgeResult()
        if room.result['gameOver']:
            self.cancel()

    def step1(self):
        self.trigger()

    def step2(self):
        # 失去所有非forceDie技能
        player = self.player
        i = 0
        while i < len(player.skill):
            if player.skill[i].forceDie:
                i += 1
            else:
                player.removeSkill(player.skill[i])

    def step3(self):
        self.player.discard('he')
        if self.player.identity == 'fan' and self.source:
            pass
            # self.source.draw(3)
        elif self.player.identity == 'zhong' and self.source and self.source.identity == 'zhu':
            self.source.discard('he')


class Judge(Event):
    name = 'judge'

    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0, self.step1, self.step2]

    def step0(self):
        card = self.room.getCards()[0]
        self.card = card
        self.room.moveCardTo(card, 't', 'judge', True)

    def step1(self):
        self.room.delay(100)
        self.trigger()

    def step2(self):
        card = self.card
        self.setResult('card', card)
        self.setResult('name', card.name)
        self.setResult('suit', card.suit)
        self.setResult('number', card.number)
        self.setResult('color', card.getColor(self.player))

        # 这里应在全局技能里写
        pass
        self.room.broadcastAll(lambda ui: ui.setHandlingClock(card, 500))
        self.room.moveCardTo(card, 'd', 'judgeAfter', True)


class ChooseToUse(ChooseEvent):
    name = 'chooseToUse'

    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0, self.step1, self.step2]
        self.prompt = '请选择要使用的牌'
        self.phaseUse = False
        self.active = False  # active模式下只能使用可主动使用的牌
        self.ignoreFilter = False
        self.cardAI = libAI.useCardAI
        self.targetAI = libAI.useCardTargetAI

        def st(player=None):
            if player is None:
                player = self.player
            if len(player.selected('card')):
                return player.selected('card')[0].selectTarget(player)
            return [0, 0]
        self.selectTargetNum = st

    def filterCard(self, card):
        # print('chooseToUse-filterCard', card, self.cardFilter)
        if (self.phaseUse or self.active) and not card.active:
            return False
        if card.active and not self.player.hasAvailableTarget(card, ignoreFilter=self.ignoreFilter):
            return False
        # print('chooseToUse-filterCard2')
        return super().filterCard(card)

    def filterTarget(self, target):
        player = self.player
        if not len(player.selected('card')):
            return False

        card = player.selected('card')[0]
        # print('chooseToUse-filterTarget-card', card)
        if not player.canUse(card, target, ignoreFilter=self.ignoreFilter):
            return False
        return super().filterTarget(target)

    def step0(self):
        if self.responded:
            self.setResult('bool', True)

            pass  # 未写虚拟牌，以此代替
            self.setResult('shanned', True)

            self.finish()

    def step1(self):
        self.player.makeChoice(self)
        # next = self.player.chooseCardTarget(self.prompt, 'h', 1, self.evtSelectTarget, self.evtFilterCard,
        #                                     self.evtFilterTarget)
        # next.complexSelect = True
        # next.forced = self.forced
        # # print('chooseToUse-step0: self.cardAI:', self.cardAI)
        # next.cardAI = self.cardAI
        # next.targetAI = self.targetAI

    def step2(self):
        result = self.result()
        if result['bool']:
            if result['card']:
                card = result['card']
                if card.active:
                    self.player.useCard(card, self.result('targets'))
                else:
                    self.player.useCard(card)
            else:
                self.player.useSkill(self.result('skill'))
        else:
            self.finish()

    # def step2(self):
    #     if self.childResult('bool'):
    #         self.setResult('bool', True)
    #         if self.childResult('cards'):
    #             card = self.childResult('cards')[0]
    #             self.setResult('card', card)
    #             if card.active:
    #                 targets = self.childResult('targets').copy()
    #                 self.setResult('targets', targets)
    #                 self.player.useCard(card, targets)
    #             else:
    #                 self.player.useCard(card)
    #         else:
    #             skill = self.childResult('skill')
    #             self.setResult('skill', skill.name)
    #             self.player.useSkill(skill)
    #     else:
    #         self.finish()


class ChooseToRespond(ChooseEvent):
    name = 'chooseToRespond'

    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0, self.step1, self.step2]
        self.prompt = '请选择要打出的牌'
        self.cardAI = libAI.respondAI

    def step0(self):
        if self.responded:
            pass  # setResult, useResult
            self.setResult('bool', True)
            self.finish()

    def step1(self):
        next = self.player.chooseCard(self.prompt, 'h', 1, self.cardFilter)
        next.cardAI = self.cardAI

    def step2(self):
        if self.childResult('bool'):
            self.setResult('bool', True)
            if self.childResult('cards'):
                self.player.respond(self.childResult('cards')[0])


class ChooseToDiscard(ChooseEvent):
    name = 'chooseToDiscard'

    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0, self.step1]
        self.prompt = '请选择要弃置的牌'
        self.cardAI = libAI.discardAI

    @property
    def targetFilter(self):
        return False

    def filterCard(self, card):
        if not self.player.canDiscard(card):
            return False
        return super().filterCard(card)

    def step1(self):
        result = self.result()
        if result['bool']:
            cards = result['cards']
            self.player.discard(cards)


class ChooseToInvoke(ChooseEvent):
    name = 'chooseToInvoke'

    def __init__(self, status):
        super().__init__(status)
        self.content = [self.step0, self.step1, self.step2, self.step3, self.step4]
        self.prompt = '请选择要使用的技能'
        self.__triggerEvent = None
        self.__invokableSkill = []
        self.__currentSkill = None

    @property
    def triggerEvent(self):
        return self.__triggerEvent

    @triggerEvent.setter
    def triggerEvent(self, value):
        self.__triggerEvent = value

    @property
    def invokableSkill(self):
        return self.__invokableSkill

    @invokableSkill.setter
    def invokableSkill(self, value):
        self.__invokableSkill = value

    def step0(self):
        if not self.__invokableSkill:
            self.finish()
            return

        if len(self.__invokableSkill) == 1 or self.__invokableSkill[0].firstDo:
            self.__currentSkill = self.__invokableSkill[0]
            self.goto(2)
        else:
            controls = [skill.name for skill in self.__invokableSkill]
            for i in range(len(controls)):
                if not self.__invokableSkill[i].forced:
                    controls.append('cancel')
                    break
            self.player.chooseControl('请选择要先发动的技能', *controls)

    def step1(self):
        if self.childResult('control') == 'cancel':
            self.setResult('bool', False)
            self.finish()
        else:
            self.__currentSkill = self.__invokableSkill[self.childResult('index')]
            self.setResult('bool', True)

    def step2(self):
        skill = self.__currentSkill
        if not skill or skill.itemType != 'skill':
            print('Warning: chooseToInvoke: currentSkill error! currentSkill:', skill)
            return
        nc, nt = skill.needCard, skill.needTarget
        if nc and nt:
            self.player.chooseCardTarget(skill.prompt, skill.position, nc, nt, skill.cardFilter, skill.targetFilter,
                                         skill.forced)
        elif nc:
            self.player.chooseCard(skill.prompt, skill.position, nc, skill.cardFilter, skill.forced)
        elif nt:
            self.player.chooseTarget(skill.prompt, nt, skill.targetFilter, skill.forced)
        elif skill.forced:
            self.goto(4)
        else:
            self.player.chooseBool(skill.prompt)

    def step3(self):
        if not self.childResult('bool'):
            self.goto(0)

    def step4(self):
        self.setResult('bool', True)
        self.setResult('skill', self.__currentSkill)
        self.player.useSkill(self.__currentSkill).triggerEvent = self.triggerEvent


class ChooseControl(ChooseEvent):
    pass


class ChooseBool(ChooseEvent):
    name = 'chooseBool'

    def __init__(self, status):
        super().__init__(status)
        # self.content.extend([self.step0, self.step1])
        self.prompt = '请选择确定或取消'

    @property
    def cardFilter(self):
        return False

    @property
    def targetFilter(self):
        return False


class ChooseCard(ChooseEvent):
    name = 'chooseCard'

    def __init__(self, status):
        super().__init__(status)
        # self.content.extend([self.step0, self.step1])
        self.prompt = '请选择牌'

    @property
    def targetFilter(self):
        return False

    # def step0(self):
    #     if not self.player.isUnderControl():
    #         self.room.wait(250)
    #
    # def step1(self):
    #     player = self.player
    #     player.choosing = True
    #     sc = self.selectCard
    #     cards = []
    #
    #     if self.filterCard:
    #         cards = list(filter(lambda card: card not in player.selected('card'), player.getCards(self.position)))
    #         if callable(self.filterCard):
    #             cards = list(filter(self.filterCard, cards))
    #     player.setSelectable('card', cards)
    #
    #     if player.isUnderControl():
    #         player.ui.setClickable('determine', len(player.selected('card')) >= sc[0])
    #         player.ui.setClickable('cancel', not self.forced)
    #         result = player.ui.waitForChoosing()
    #     else:
    #         result = player.ai.chooseCardTarget()
    #
    #     if result == 'gameInterrupted':
    #         return
    #
    #     if result in ['determine', 'cancel']:
    #         if result == 'determine':
    #             self.setResult('bool', True)
    #             self.setResult('cards', player.selected('card').copy())
    #         player.endChoosing()
    #     elif result:
    #         if result in player.selected('card'):
    #             if sc[0] != -1:
    #                 player.selected('card').remove(result)
    #         else:
    #             player.selected('card').append(result)
    #             if len(player.selected('card')) > sc[1]:
    #                 player.selected('card').pop(0)
    #         self.redo()


class ChooseCardTarget(ChooseEvent):
    name = 'chooseCardTarget'

    def __init__(self, status):
        super().__init__(status)
        self.prompt = '请选择牌和目标'

    # @property
    # def selectTarget(self):
    #     if self.player.selected('card'):
    #         targetRange = self.player.selected('card')[0].targetRange
    #         if type(targetRange) is list:
    #             return targetRange
    #         return [targetRange, targetRange]
    #     return [0, 0]
    #
    # @selectTarget.setter
    # def selectTarget(self, value):
    #     pass


# class ChooseCardTarget(ChooseEvent):
#     name = 'chooseCardTarget'
#
#     def __init__(self, status):
#         super().__init__(status)
#         self.content.extend([self.step0, self.step1])
#         self.prompt = '请选择牌和目标'
#
#     def step0(self):
#         self.player.choosing = True
#         if not self.player.isUnderControl():
#             self.room.wait(250)
#
#     def step1(self):
#         player = self.player
#         if player.ui:
#             player.ui.setControls('phaseUse' if self.getParent(2).name == 'phaseUse' else 'choose')
#
#         sc = self.selectCard
#         st = self.selectTarget
#         cards = []
#         # 确定可选牌
#         if self.filterCard:
#             cards = list(filter(lambda card: card not in player.selected('card'), player.getCards(self.position)))
#             if callable(self.filterCard):
#                 cards = list(filter(self.filterCard, cards))
#         player.setSelectable('card', cards)
#         # if not player.isUnderControl() and self.complexCardAI and callable(self.complexCardAI):
#         #     player.selected('card').extend(self.complexCardAI(player.selectable('card')))
#         # print('selectable(card):', player.selectable('card'))
#
#         # 确定可选目标
#         targets = []
#         if len(player.selected('card')) >= sc[0]:
#             player.choosingTarget = True
#             if self.filterTarget:
#                 targets = list(filter(lambda current: current not in player.selected('target'), self.room.players))
#         else:
#             player.choosingTarget = False
#         if callable(self.filterTarget):
#             targets = list(filter(self.filterTarget, targets))
#         player.setSelectable('target', targets)
#         # print('selectable(target):', player.selectable('target'))
#
#         # 复杂ai
#         if self.complexTargetAI and callable(self.complexTargetAI):
#             player.selected('target').extend(self.complexTargetAI(player.selectable('target')))
#
#         # 全选
#         elif st[0] == -1:
#             player.selected('target').extend(player.selectable('target'))
#             player.selectable('target').clear()
#
#         # 唯一可选目标时，自动选择
#         elif not len(player.selected('target')) and len(player.selectable('target')) == 1 \
#                 and st[0] == 1 and st[1] == 1:
#             player.selected('target').append(player.selectable('target')[0])
#             player.selectable('target').remove(player.selected('target')[0])
#
#         # 进行选择
#         if player.isUnderControl():
#             # 设置confirm选项
#             player.ui.setClickable('determine', len(player.selected('card')) >= sc[0]
#                                    and len(player.selected('target')) >= st[0])
#             player.ui.setClickable('cancel', not self.forced)
#             result = player.ui.waitForChoosing()
#         else:
#             result = player.ai.chooseCardTarget()
#
#         if result == 'gameInterrupted':
#             return
#
#         # print('chooseCardTarget-singleChoose_result:', result)
#         if result in ['determine', 'cancel']:
#             if result == 'determine':
#                 self.setResult('bool', True)
#                 self.setResult('cards', player.selected('card').copy())
#                 targets = player.selected('target').copy()
#                 if not self.multiTarget:
#                     self.room.targetSort(targets)
#                 self.setResult('targets', targets)
#                 # self.setResult('skill', )
#             player.endChoosing()
#         elif result:
#             resultType = result.itemType
#             if resultType == 'card':
#                 if result in player.selected('card'):
#                     if sc[0] != -1:
#                         player.selected('card').remove(result)
#                         player.selected('target').clear()
#                 else:
#                     player.selected('card').append(result)
#                     if len(player.selected('card')) > sc[1]:
#                         player.selected('card').pop(0)
#                     if self.complexSelect:
#                         player.selected('target').clear()
#             elif resultType == 'player':
#                 if result in player.selected('target'):
#                     if sc[0] != -1:
#                         player.selected('target').remove(result)
#                 else:
#                     player.selected('target').append(result)
#                     if len(player.selected('target')) > st[1]:
#                         player.selected('target').pop(0)
#             self.redo()


#### pzh更改部分
class Equip(Event):
    name = 'equip'

    def __init__(self, status, card):
        super().__init__(status)
        self.card = card
        self.content.extend([self.step0, self.step1, self.step2])
        self.equipments = dict()

    def step0(self):
        player, card = self.player, self.card
        if card.type != 'equip':
            self.finish()
            return
        origin = player.getEquip(card.subtype)
        if origin:
            player.loseCardTo(origin, self.room.discardPile, 'changeEquip')

    def step1(self):
        room, card = self.room, self.card
        origins = {}
        for ui in room.ui:
            origins[ui] = ui.getCoordinate(card)

        # print(card.area, card.area.owner)
        if card.area and not card.area.owner:
            card.area.removeCard(card)
            if card.area.positionType == 't':
                self.room.broadcastAll(lambda ui: ui.removeHandling(card))

        self.player.equipArea.addCard(card)
        self.player.addSkill(card.skill)
        for ui in room.ui:
            ui.setMovement(card, origins[ui], ui.getCoordinate(card), 100)
        # print(len(self.player().getHandcardsArea().cards()))
        # self.room().getUI().display()
        if self.source:
            self.source.lose(card, 'gain')

    def step2(self):
        self.player.equipArea.addCard(self.equipments)

    # def step3(self):
    #     self.room.moveCardTo(self.card.cards, 'handleArea')

# class Phase(Event):
#     def __init__(self, status):
#         super().__init__(status, '')
#         self.content.append(self.step0)


# class CardEffect(Event):
#     def __init__(self, status):
#         super().__init__(status, 'cardEffect')
#         self.content.append(self.step0)
#         self.__cardContentStep = 0
#         self.__addedTarget = {}
#
#     def addedTarget(self, target=None):
#         if target is None:
#             return self.__addedTarget
#         return self.__addedTarget[target]
#
#     def setAddedTarget(self, target, addedTarget):
#         self.__addedTarget[target] = addedTarget
#
#     def step0(self):
#         self.card.
#         if self.__cardContentStep < len(self.card.content):
#             if self.card.multiTarget:
#                 self.card.content[self.__cardContentStep](self.player, self.target, self.__addedTarget)
#             else:
#                 self.card.content[self.__cardContentStep](self.player, self.target)
#             self.__cardContentStep += 1
#             self.redo()
