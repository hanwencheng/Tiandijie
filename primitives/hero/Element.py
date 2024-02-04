import enum


class Elements(enum.IntEnum):
    FIRE = 1  # 火
    WATER = 2  # 冰
    THUNDER = 3  # 雷
    LIGHT = 4  # 光
    DARK = 5  # 暗
    ETHEREAL = 6  # 幽


def get_elemental_multiplier(attacker_element: Elements, defender_element: Elements, is_attacker: bool) -> float:
    elemental_advantage = {
        Elements.FIRE: Elements.THUNDER,
        Elements.THUNDER: Elements.WATER,
        Elements.WATER: Elements.FIRE,
        Elements.LIGHT: Elements.DARK,
        Elements.DARK: Elements.ETHEREAL,
        Elements.ETHEREAL: Elements.LIGHT
    }

    elemental_disadvantage = {
        Elements.FIRE: Elements.WATER,
        Elements.THUNDER: Elements.FIRE,
        Elements.WATER: Elements.THUNDER,
        Elements.LIGHT: Elements.ETHEREAL,
        Elements.DARK: Elements.LIGHT,
        Elements.ETHEREAL: Elements.DARK
    }
    if is_attacker:
        if elemental_advantage[attacker_element] == defender_element:
            return 1.3
        else:
            return 1.0
    elif elemental_disadvantage[defender_element] == attacker_element:
        return 0.75
    else:
        return 1.0
