def getMaxOrderItem(items, player):
    if not items:
        return []
    mo, moItems = player.getUseOrder(items[0]), [items[0]]
    for i in range(1, len(items)):
        order = player.getUseOrder(items[i])
        if order > mo:
            mo = order
            moItems = [items[i]]
        elif order == mo:
            moItems.append(items[i])
    return moItems


def getMaxUseValueItem(items, player):
    if not items:
        return []
    muv, muvItems = player.getUseValue(items[0]), [items[0]]
    for i in range(1, len(items)):
        useValue = player.getUseValue(items[i])
        if useValue > muv:
            muv = useValue
            muvItems = [items[i]]
        elif useValue == muv:
            muvItems.append(items[i])
    return muvItems


def getMaxUsefulItem():
    pass


def useCardAI(card):
    player = card.owner
    event = player.getStatus().currentEvent
    cards = list(filter(lambda cardx: event.filterCard(cardx), player.getCards('h')))
    # print('useCardAI-cards', cards)
    if not cards:
        print('\033[1;31m Warning: useCardAI中无可选牌！\033[0m')
        return 0

    uv = player.getUseValue(card, event)
    # print('useCardAI-useValue', uv)
    if uv > 0:
        uo = player.getUseOrder(card)
        # print('useCardAI-order', uo)
        return 100 * uo + uv
    return 0

    # moCards = getMaxOrderItem(cards, player)
    # if card in moCards:
    #     uv = player.getUseValue(card)
    #     print('useCardAI-result', uv)
    #     return uv  # player.getUseValue(card)
    # print('useCardAI-result', 0)
    # return 0


def respondAI(card):
    if card.getColor() == 'red':
        return 0.5
    return 1


def discardAI(card):
    if card.type == 'equip':
        return 8 - card.equipValue
    return 5.8 - card.value


def useCardTargetAI(target):
    if target.itemType != 'player':
        print('\033[1;31mWarning: lib.ai.useTargetAI(Target): Parameter \'target\' is not a player!\033[0m')
        return -100

    player = target.getStatus().currentEvent.player
    return player.getEffect(player.selected('card')[0], player, target)
