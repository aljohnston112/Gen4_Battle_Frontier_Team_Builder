import pprint
from enum import unique, Enum

from attrs import frozen

from data_class.Stat import StatEnum


@unique
class NatureEnum(Enum):
    """
    Represents the Pokémon natures.
    """
    HARDY = "Hardy"
    LONELY = "Lonely"
    BRAVE = "Brave"
    ADAMANT = "Adamant"
    NAUGHTY = "Naughty"
    BOLD = "Bold"
    DOCILE = "Docile"
    RELAXED = "Relaxed"
    IMPISH = "Impish"
    LAX = "Lax"
    TIMID = "Timid"
    HASTY = "Hasty"
    SERIOUS = "Serious"
    JOLLY = "Jolly"
    NAIVE = "Naive"
    MODEST = "Modest"
    MILD = "Mild"
    QUIET = "Quiet"
    BASHFUL = "Bashful"
    RASH = "Rash"
    CALM = "Calm"
    GENTLE = "Gentle"
    SASSY = "Sassy"
    CAREFUL = "Careful"
    QUIRKY = "Quirky"


@frozen
class Nature:
    nature: NatureEnum
    up: StatEnum
    down: StatEnum


__NATURE_DICT__: dict[str, Nature] = {
    NatureEnum.HARDY.value: Nature(
        nature=NatureEnum.HARDY,
        up=StatEnum.NO_STAT,
        down=StatEnum.NO_STAT
    ),
    NatureEnum.LONELY.value: Nature(
        nature=NatureEnum.LONELY,
        up=StatEnum.ATTACK,
        down=StatEnum.DEFENSE
    ),
    NatureEnum.BRAVE.value: Nature(
        nature=NatureEnum.BRAVE,
        up=StatEnum.ATTACK,
        down=StatEnum.SPEED
    ),
    NatureEnum.ADAMANT.value: Nature(
        nature=NatureEnum.ADAMANT,
        up=StatEnum.ATTACK,
        down=StatEnum.SPECIAL_ATTACK
    ),
    NatureEnum.NAUGHTY.value: Nature(
        nature=NatureEnum.NAUGHTY,
        up=StatEnum.ATTACK,
        down=StatEnum.SPECIAL_DEFENSE
    ),
    NatureEnum.BOLD.value: Nature(
        nature=NatureEnum.BOLD,
        up=StatEnum.DEFENSE,
        down=StatEnum.ATTACK
    ),
    NatureEnum.DOCILE.value: Nature(
        nature=NatureEnum.DOCILE,
        up=StatEnum.NO_STAT,
        down=StatEnum.NO_STAT
    ),
    NatureEnum.RELAXED.value: Nature(
        nature=NatureEnum.RELAXED,
        up=StatEnum.DEFENSE,
        down=StatEnum.SPEED
    ),
    NatureEnum.IMPISH.value: Nature(
        nature=NatureEnum.IMPISH,
        up=StatEnum.DEFENSE,
        down=StatEnum.SPECIAL_ATTACK
    ),
    NatureEnum.LAX.value: Nature(
        nature=NatureEnum.LAX,
        up=StatEnum.DEFENSE,
        down=StatEnum.SPECIAL_DEFENSE
    ),
    NatureEnum.TIMID.value: Nature(
        nature=NatureEnum.TIMID,
        up=StatEnum.SPEED,
        down=StatEnum.ATTACK
    ),
    NatureEnum.HASTY.value: Nature(
        nature=NatureEnum.HASTY,
        up=StatEnum.SPEED,
        down=StatEnum.DEFENSE
    ),
    NatureEnum.SERIOUS.value: Nature(
        nature=NatureEnum.SERIOUS,
        up=StatEnum.NO_STAT,
        down=StatEnum.NO_STAT
    ),
    NatureEnum.JOLLY.value: Nature(
        nature=NatureEnum.JOLLY,
        up=StatEnum.SPEED,
        down=StatEnum.SPECIAL_ATTACK
    ),
    NatureEnum.NAIVE.value: Nature(
        nature=NatureEnum.NAIVE,
        up=StatEnum.SPEED,
        down=StatEnum.SPECIAL_DEFENSE
    ),
    NatureEnum.MODEST.value: Nature(
        nature=NatureEnum.MODEST,
        up=StatEnum.SPECIAL_ATTACK,
        down=StatEnum.ATTACK
    ),
    NatureEnum.MILD.value: Nature(
        nature=NatureEnum.MILD,
        up=StatEnum.SPECIAL_ATTACK,
        down=StatEnum.DEFENSE
    ),
    NatureEnum.QUIET.value: Nature(
        nature=NatureEnum.QUIET,
        up=StatEnum.SPECIAL_ATTACK,
        down=StatEnum.SPEED
    ),
    NatureEnum.BASHFUL.value: Nature(
        nature=NatureEnum.BASHFUL,
        up=StatEnum.NO_STAT,
        down=StatEnum.NO_STAT
    ),
    NatureEnum.RASH.value: Nature(
        nature=NatureEnum.RASH,
        up=StatEnum.SPECIAL_ATTACK,
        down=StatEnum.SPECIAL_DEFENSE
    ),
    NatureEnum.CALM.value: Nature(
        nature=NatureEnum.CALM,
        up=StatEnum.SPECIAL_DEFENSE,
        down=StatEnum.ATTACK
    ),
    NatureEnum.GENTLE.value: Nature(
        nature=NatureEnum.GENTLE,
        up=StatEnum.SPECIAL_DEFENSE,
        down=StatEnum.DEFENSE
    ),
    NatureEnum.SASSY.value: Nature(
        nature=NatureEnum.SASSY,
        up=StatEnum.SPECIAL_DEFENSE,
        down=StatEnum.SPEED
    ),
    NatureEnum.CAREFUL.value: Nature(
        nature=NatureEnum.CAREFUL,
        up=StatEnum.SPECIAL_DEFENSE,
        down=StatEnum.SPECIAL_ATTACK
    ),
    NatureEnum.QUIRKY.value: Nature(
        nature=NatureEnum.QUIRKY,
        up=StatEnum.NO_STAT,
        down=StatEnum.NO_STAT
    )
}

all_natures: list[Nature] = \
    [nature for nature_name, nature in __NATURE_DICT__.items()]

__DETRIMENTAL_NATURE_MULTIPLIER__: float = 0.9
__BENEFICIAL_NATURE_MULTIPLIER__: float = 1.1
__STAT_TO_NATURE_MULTIPLIERS__: dict[StatEnum, dict[NatureEnum, float]] = {
    StatEnum.ATTACK: {
        NatureEnum.LONELY: __BENEFICIAL_NATURE_MULTIPLIER__,
        NatureEnum.BRAVE: __BENEFICIAL_NATURE_MULTIPLIER__,
        NatureEnum.ADAMANT: __BENEFICIAL_NATURE_MULTIPLIER__,
        NatureEnum.NAUGHTY: __BENEFICIAL_NATURE_MULTIPLIER__,

        NatureEnum.BOLD: __DETRIMENTAL_NATURE_MULTIPLIER__,
        NatureEnum.MODEST: __DETRIMENTAL_NATURE_MULTIPLIER__,
        NatureEnum.CALM: __DETRIMENTAL_NATURE_MULTIPLIER__,
        NatureEnum.TIMID: __DETRIMENTAL_NATURE_MULTIPLIER__
    },
    StatEnum.DEFENSE: {
        NatureEnum.BOLD: __BENEFICIAL_NATURE_MULTIPLIER__,
        NatureEnum.RELAXED: __BENEFICIAL_NATURE_MULTIPLIER__,
        NatureEnum.IMPISH: __BENEFICIAL_NATURE_MULTIPLIER__,
        NatureEnum.LAX: __BENEFICIAL_NATURE_MULTIPLIER__,

        NatureEnum.LONELY: __DETRIMENTAL_NATURE_MULTIPLIER__,
        NatureEnum.MILD: __DETRIMENTAL_NATURE_MULTIPLIER__,
        NatureEnum.GENTLE: __DETRIMENTAL_NATURE_MULTIPLIER__,
        NatureEnum.HASTY: __DETRIMENTAL_NATURE_MULTIPLIER__
    },
    StatEnum.SPECIAL_ATTACK: {
        NatureEnum.MODEST: __BENEFICIAL_NATURE_MULTIPLIER__,
        NatureEnum.MILD: __BENEFICIAL_NATURE_MULTIPLIER__,
        NatureEnum.QUIET: __BENEFICIAL_NATURE_MULTIPLIER__,
        NatureEnum.RASH: __BENEFICIAL_NATURE_MULTIPLIER__,

        NatureEnum.ADAMANT: __DETRIMENTAL_NATURE_MULTIPLIER__,
        NatureEnum.IMPISH: __DETRIMENTAL_NATURE_MULTIPLIER__,
        NatureEnum.CAREFUL: __DETRIMENTAL_NATURE_MULTIPLIER__,
        NatureEnum.JOLLY: __DETRIMENTAL_NATURE_MULTIPLIER__
    },
    StatEnum.SPECIAL_DEFENSE: {
        NatureEnum.CALM: __BENEFICIAL_NATURE_MULTIPLIER__,
        NatureEnum.GENTLE: __BENEFICIAL_NATURE_MULTIPLIER__,
        NatureEnum.SASSY: __BENEFICIAL_NATURE_MULTIPLIER__,
        NatureEnum.CAREFUL: __BENEFICIAL_NATURE_MULTIPLIER__,

        NatureEnum.NAUGHTY: __DETRIMENTAL_NATURE_MULTIPLIER__,
        NatureEnum.LAX: __DETRIMENTAL_NATURE_MULTIPLIER__,
        NatureEnum.NAIVE: __DETRIMENTAL_NATURE_MULTIPLIER__,
        NatureEnum.RASH: __DETRIMENTAL_NATURE_MULTIPLIER__
    },
    StatEnum.SPEED: {
        NatureEnum.TIMID: __BENEFICIAL_NATURE_MULTIPLIER__,
        NatureEnum.HASTY: __BENEFICIAL_NATURE_MULTIPLIER__,
        NatureEnum.JOLLY: __BENEFICIAL_NATURE_MULTIPLIER__,
        NatureEnum.NAIVE: __BENEFICIAL_NATURE_MULTIPLIER__,

        NatureEnum.BRAVE: __DETRIMENTAL_NATURE_MULTIPLIER__,
        NatureEnum.RELAXED: __DETRIMENTAL_NATURE_MULTIPLIER__,
        NatureEnum.QUIET: __DETRIMENTAL_NATURE_MULTIPLIER__,
        NatureEnum.SASSY: __DETRIMENTAL_NATURE_MULTIPLIER__
    }
}


def get_nature_enum(name: str) -> NatureEnum:
    try:
        return NatureEnum(name)
    except ValueError:
        raise ValueError(f"Unknown nature: {name}")


def get_nature_multiplier(stat_type: StatEnum, nature: NatureEnum) -> float:
    return __STAT_TO_NATURE_MULTIPLIERS__[stat_type].get(nature, 1.0)

if __name__ == '__main__':
    pprint.pp(__NATURE_DICT__)