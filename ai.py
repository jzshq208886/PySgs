class AI:
    def __init__(self, me):
        self.__defaultUseValue = {"sha": 10, "tao": 12, "juedou": 8}
        self.__me = me
        self.__room = me.room
        self.__status = self.__room.status

        self.__info = {}

    @property
    def info(self):
        return self.__info

    def updateInfo(self):
        me, info = self.__me, self.__info
        for player in self.__room.players:
            if player not in info.keys():
                info[player] = {'identityKnown': False, 'attitude': 0}
            pass  # 确定已知身份

        info[me]['identityKnown'] = True
        info[me]['attitude'] = 5

    def singleChoose(self, event=None):
        player = self.__me
        if not player.choosing:
            return None
        if event is None:
            event = self.__status.currentEvent
        # if self.__me.name == 'xinxianying' and event.getParent(2).name == 'cardEffect':
        #     print("\033[0;31;40m"+"ai.chooseCardTarget"+"\033[0m")

        sc = event.selectCardNum
        st = event.selectTargetNum
        sableC = player.selectable('card')
        sableT = player.selectable('target')
        sedC = player.selected('card')
        sedT = player.selected('target')

        if not event.complexCardAI or not callable(event.complexCardAI):
            # 已选牌数未达上限，且仍有可选牌：继续尝试寻找有价值的牌
            if len(sedC) < sc[1] and len(sableC):
                # 获得最大价值牌
                # print("\033[0;31;40m" + "ai.chooseCardTarget-in4" + "\033[0m")
                # print('ai-chooseCardTarget-sableC', sableC)
                maxValue, mvi = event.checkCard(sableC[0]), 0
                # print('ai-chooseCardTarget-maxValue1', maxValue)
                for i in range(1, len(sableC)):
                    value = event.checkCard(sableC[i])
                    # print('ai-chooseCardTarget-currCard', sableC[i], 'value', value)
                    if value > maxValue:
                        maxValue = value
                        mvi = i
                # print('ai-chooseCardTarget-maxValue2', maxValue)
                if maxValue > 0 or event.forced and len(sedC) < sc[0]:
                    return sableC[mvi]

        # 最终选定牌数不足：选择取消
        if event.cardFilter and len(sedC) < sc[0]:
            if event.forced:
                print('\033[1;31m Warning: ai: No enough card choice for forced chooseEvent! Return cancel.\033[0m')
                print('selected(\'card\'):', sedC)
                print('selected(\'target\'):', sedT)
            return 'cancel'

        if not event.complexTargetAI or not callable(event.complexTargetAI):
            # 已选目标数未达上限，且仍有可选目标：继续尝试寻找有价值的目标
            if len(sedT) < st[1] and len(sableT):
                pass
                maxValue, mvi = event.checkTarget(sableT[0]), 0
                for i in range(1, len(sableT)):
                    value = event.checkTarget(sableT[i])
                    if value > maxValue:
                        maxValue = value
                        mvi = i
                # print('ai.chooseCardTarget()-maxValue:', maxValue)
                # print('ai.chooseCardTarget()-mvi:', mvi)
                if maxValue > 0 or event.forced and len(sedT) < st[0]:
                    return sableT[mvi]

        # 最终选定目标数不足：选择取消
        if event.targetFilter and len(sedT) < st[0]:
            if event.forced:
                print('\033[1;31m Warning: ai: No enough target choice for forced chooseEvent! Return cancel.\033[0m')
                print('selected(\'card\'):', sedC)
                print('selected(\'target\'):', sedT)
            return 'cancel'

        return 'determine'

    def getTargetValue(self, target):
        pass
        return 1

    def getCardUseValue(self, card):
        pass
        name = card.getName()
        return self.__defaultUseValue[name] if name in self.__defaultUseValue else 0

    def decideCardTarget(self, card):
        if card.targetFixed():
            return card.getFixedTarget()

        value = dict()
        targetNames, avaiTargets = [], self.__me.getAvailableTargets(card)
        # return [avaiTargets[0]]
        for target in avaiTargets:
            value[target.getName()] = self.getTargetValue(target)
        for name in value:
            if value[name] <= 0:
                del value[name]

        while value and len(targetNames) < card.getMaxTargetsNumber():
            mv, mvName = 0, None
            for name in value:
                if value[name] > mv:
                    mv = value[name]
                    mvName = name
            targetNames.append(mvName)
            del value[mvName]

        dTargers = []
        for name in targetNames:
            for target in avaiTargets:
                if target.getName() == name:
                    dTargers.append(target)
        return dTargers

    def decideUse(self, choices, phaseUse=False):
        mvIndex, mv, targets = [0, 0], -1000, [[], []]
        for choice in choices[0]:
            targets[0].append(self.decideCardTarget(choice))
        for choice in choices[1]:
            pass
        # for i in range(len(choices[0])):
        #     curMv = self.getCardUseValue(choices[0][i])
        #     if curMv > mv:
        #         mvIndex, mv = [0, 0], curMv
        # for i in range(len(choices[1])):
        #     pass
        #
        if choices[0]:
            return "UseCard", 0, targets[0][0]
        return "End", None, None

