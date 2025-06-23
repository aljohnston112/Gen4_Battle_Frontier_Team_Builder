from attr import frozen

from data_class.Stat import StatEnum


@frozen
class Stats:
    """
    Represents the base stats of a Pokémon.
    """

    health: int
    """
    The base health of the pokemon
    """

    attack: int
    """
    The base attack of the pokemon
    """

    defense: int
    """
    The base defense of the pokemon
    """

    special_attack: int
    """
    The base special attack of the pokemon
    """

    special_defense: int
    """
    The base special defense of the pokemon
    """

    speed: int
    """
    The base speed of the pokemon    
    """


def get_stat(stats: Stats, stat_enum: StatEnum) -> int:
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