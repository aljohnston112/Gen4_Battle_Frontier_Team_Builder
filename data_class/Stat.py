from enum import unique, Enum

import attr
from attrs import frozen


@unique
class StatEnum(Enum):
    """
       Represents Pokemon stats.
    """

    HEALTH = "health"
    ATTACK = "attack"
    DEFENSE = "defense"
    SPECIAL_ATTACK = "special_attack"
    SPECIAL_DEFENSE = "special_defense"
    SPEED = "speed"
    NO_STAT = "no_stat"


@attr.define
class Stat:
    stat_type: StatEnum
    value: int


__STAT_DICT__ = {
    "health": StatEnum.HEALTH,
    "attack": StatEnum.ATTACK,
    "defense": StatEnum.DEFENSE,
    "special_attack": StatEnum.SPECIAL_ATTACK,
    "special_defense": StatEnum.SPECIAL_DEFENSE,
    "speed": StatEnum.SPEED,
}


def get_stat_enum(stat):
    return __STAT_DICT__[stat.lower()]

@unique
class NatureEnum(Enum):
    """
    Represents the Pokémon natures.
    """
    HARDY = "hardy"
    LONELY = "lonely"
    BRAVE = "brave"
    ADAMANT = "adamant"
    NAUGHTY = "naughty"
    BOLD = "bold"
    DOCILE = "docile"
    RELAXED = "relaxed"
    IMPISH = "impish"
    LAX = "lax"
    TIMID = "timid"
    HASTY = "hasty"
    SERIOUS = "serious"
    JOLLY = "jolly"
    NAIVE = "naive"
    MODEST = "modest"
    MILD = "mild"
    QUIET = "quiet"
    BASHFUL = "bashful"
    RASH = "rash"
    CALM = "calm"
    GENTLE = "gentle"
    SASSY = "sassy"
    CAREFUL = "careful"
    QUIRKY = "quirky"


def get_nature_enum(name: str) -> NatureEnum:
    try:
        return NatureEnum(name.lower())
    except ValueError:
        raise ValueError(f"Unknown nature: {name}")


@frozen
class Nature:
    nature: NatureEnum

    up: StatEnum
    down: StatEnum


__NATURE_DICT__ = {
    "hardy": Nature(
        nature=NatureEnum.HARDY,
        up=StatEnum.NO_STAT,
        down=StatEnum.NO_STAT
    ),
    "lonely": Nature(
        nature=NatureEnum.LONELY,
        up=StatEnum.ATTACK,
        down=StatEnum.DEFENSE
    ),
    "brave": Nature(
        nature=NatureEnum.BRAVE,
        up=StatEnum.ATTACK,
        down=StatEnum.SPEED
    ),
    "adamant": Nature(
        nature=NatureEnum.ADAMANT,
        up=StatEnum.ATTACK,
        down=StatEnum.SPECIAL_ATTACK
    ),
    "naughty": Nature(
        nature=NatureEnum.NAUGHTY,
        up=StatEnum.ATTACK,
        down=StatEnum.SPECIAL_DEFENSE
    ),
    "bold": Nature(
        nature=NatureEnum.BOLD,
        up=StatEnum.DEFENSE,
        down=StatEnum.ATTACK
    ),
    "docile": Nature(
        nature=NatureEnum.DOCILE,
        up=StatEnum.NO_STAT,
        down=StatEnum.NO_STAT
    ),
    "relaxed": Nature(
        nature=NatureEnum.RELAXED,
        up=StatEnum.DEFENSE,
        down=StatEnum.SPEED
    ),
    "impish": Nature(
        nature=NatureEnum.IMPISH,
        up=StatEnum.DEFENSE,
        down=StatEnum.SPECIAL_ATTACK
    ),
    "lax": Nature(
        nature=NatureEnum.LAX,
        up=StatEnum.DEFENSE,
        down=StatEnum.SPECIAL_DEFENSE
    ),
    "timid": Nature(
        nature=NatureEnum.TIMID,
        up=StatEnum.SPEED,
        down=StatEnum.ATTACK
    ),
    "hasty": Nature(
        nature=NatureEnum.HASTY,
        up=StatEnum.SPEED,
        down=StatEnum.DEFENSE
    ),
    "serious": Nature(
        nature=NatureEnum.SERIOUS,
        up=StatEnum.NO_STAT,
        down=StatEnum.NO_STAT
    ),
    "jolly": Nature(
        nature=NatureEnum.JOLLY,
        up=StatEnum.SPEED,
        down=StatEnum.SPECIAL_ATTACK
    ),
    "naive": Nature(
        nature=NatureEnum.NAIVE,
        up=StatEnum.SPEED,
        down=StatEnum.SPECIAL_DEFENSE
    ),
    "modest": Nature(
        nature=NatureEnum.MODEST,
        up=StatEnum.SPECIAL_ATTACK,
        down=StatEnum.ATTACK
    ),
    "mild": Nature(
        nature=NatureEnum.MILD,
        up=StatEnum.SPECIAL_ATTACK,
        down=StatEnum.DEFENSE
    ),
    "quiet": Nature(
        nature=NatureEnum.QUIET,
        up=StatEnum.SPECIAL_ATTACK,
        down=StatEnum.SPEED
    ),
    "bashful": Nature(
        nature=NatureEnum.BASHFUL,
        up=StatEnum.NO_STAT,
        down=StatEnum.NO_STAT
    ),
    "rash": Nature(
        nature=NatureEnum.RASH,
        up=StatEnum.SPECIAL_ATTACK,
        down=StatEnum.SPECIAL_DEFENSE
    ),
    "calm": Nature(
        nature=NatureEnum.CALM,
        up=StatEnum.SPECIAL_DEFENSE,
        down=StatEnum.ATTACK
    ),
    "gentle": Nature(
        nature=NatureEnum.GENTLE,
        up=StatEnum.SPECIAL_DEFENSE,
        down=StatEnum.DEFENSE
    ),
    "sassy": Nature(
        nature=NatureEnum.SASSY,
        up=StatEnum.SPECIAL_DEFENSE,
        down=StatEnum.SPEED
    ),
    "careful": Nature(
        nature=NatureEnum.CAREFUL,
        up=StatEnum.SPECIAL_DEFENSE,
        down=StatEnum.SPECIAL_ATTACK
    ),
    "quirky": Nature(
        nature=NatureEnum.QUIRKY,
        up=StatEnum.NO_STAT,
        down=StatEnum.NO_STAT
    )
}


def get_natures() -> list[Nature]:
    return [v for k, v in __NATURE_DICT__.items()]


__stat_to_nature_multipliers__ = {
    StatEnum.ATTACK: {
        NatureEnum.LONELY: 1.1, NatureEnum.BRAVE: 1.1,
        NatureEnum.ADAMANT: 1.1, NatureEnum.NAUGHTY: 1.1,
        NatureEnum.BOLD: 0.9, NatureEnum.MODEST: 0.9,
        NatureEnum.CALM: 0.9, NatureEnum.TIMID: 0.9
    },
    StatEnum.DEFENSE: {
        NatureEnum.BOLD: 1.1, NatureEnum.RELAXED: 1.1,
        NatureEnum.IMPISH: 1.1, NatureEnum.LAX: 1.1,
        NatureEnum.LONELY: 0.9, NatureEnum.MILD: 0.9,
        NatureEnum.GENTLE: 0.9, NatureEnum.HASTY: 0.9
    },
    StatEnum.SPECIAL_ATTACK: {
        NatureEnum.MODEST: 1.1, NatureEnum.MILD: 1.1,
        NatureEnum.QUIET: 1.1, NatureEnum.RASH: 1.1,
        NatureEnum.ADAMANT: 0.9, NatureEnum.IMPISH: 0.9,
        NatureEnum.CAREFUL: 0.9, NatureEnum.JOLLY: 0.9
    },
    StatEnum.SPECIAL_DEFENSE: {
        NatureEnum.CALM: 1.1, NatureEnum.GENTLE: 1.1,
        NatureEnum.SASSY: 1.1, NatureEnum.CAREFUL: 1.1,
        NatureEnum.NAUGHTY: 0.9, NatureEnum.LAX: 0.9,
        NatureEnum.NAIVE: 0.9, NatureEnum.RASH: 0.9
    },
    StatEnum.SPEED: {
        NatureEnum.TIMID: 1.1, NatureEnum.HASTY: 1.1,
        NatureEnum.JOLLY: 1.1, NatureEnum.NAIVE: 1.1,
        NatureEnum.BRAVE: 0.9, NatureEnum.RELAXED: 0.9,
        NatureEnum.QUIET: 0.9, NatureEnum.SASSY: 0.9
    }
}


def get_nature_multiplier(stat_type: StatEnum, nature: NatureEnum) -> float:
    return __stat_to_nature_multipliers__\
        .get(stat_type, {})\
        .get(nature, 1.0)