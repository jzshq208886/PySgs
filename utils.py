import random


def chooseByWeight(weight: dict):
    total = sum(weight.values())
    num = random.randint(1, total)
    temp = 0
    for key in weight:
        temp += weight[key]
        if num <= temp:
            return key
