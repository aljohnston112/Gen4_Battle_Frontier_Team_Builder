from attr import frozen

from data_class.Stat import StatEnum
from data_class.Stats import Stats


@frozen
class BaseStats:
    name: str
    stats: Stats


def get_base_stat(base_stats: BaseStats, stat_enum: StatEnum) -> int:
    stats = base_stats.stats
    if stat_enum == StatEnum.HEALTH:
        return stats.health
    elif stat_enum == StatEnum.ATTACK:
        return stats.attack
    elif stat_enum == StatEnum.DEFENSE:
        return stats.defense
    elif stat_enum == StatEnum.SPECIAL_ATTACK:
        return stats.special_attack
    elif stat_enum == StatEnum.SPECIAL_DEFENSE:
        return stats.special_defense
    elif stat_enum == StatEnum.SPEED:
        return stats.speed
    else:
        raise ValueError(" Bad stat enum: " + stat_enum.name)