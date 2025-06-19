import math
from enum import unique, Enum

import attr

from Config import LEVEL


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


@attr.define(frozen=True, hash=False)
class Stat:
    stat_type: StatEnum
    value: int

    def __hash__(self):
        return hash((self.stat_type, self.value))

    def __eq__(self, other):
        return (
                other is Stat and
                self.stat_type == other.stat_type and
                self.value == other.value
        )


__STAT_DICT__: dict[str, StatEnum] = {
    StatEnum.HEALTH.value: StatEnum.HEALTH,
    StatEnum.ATTACK.value: StatEnum.ATTACK,
    StatEnum.DEFENSE.value: StatEnum.DEFENSE,
    StatEnum.SPECIAL_ATTACK.value: StatEnum.SPECIAL_ATTACK,
    StatEnum.SPECIAL_DEFENSE.value: StatEnum.SPECIAL_DEFENSE,
    StatEnum.SPEED.value: StatEnum.SPEED,
}


def get_stat_enum(stat: str) -> StatEnum:
    return __STAT_DICT__[stat]


def calculate_health_stat(
        base: int,
        iv: int,
        ev: int
) -> int:
    return (((2 * base + iv + (ev // 4)) * LEVEL) // 100) + LEVEL + 10


def calculate_non_health_stat(
        base: int,
        iv: int,
        ev: int,
        nature_multiplier: float
) -> int:
    stat: int = ((2 * base + iv + (ev // 4)) * LEVEL) // 100 + 5
    return math.floor(stat * nature_multiplier)