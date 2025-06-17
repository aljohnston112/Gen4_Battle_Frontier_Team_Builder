from enum import Enum, unique


@unique
class PokemonType(Enum):
    """
    Represents the Pokémon types.
    """
    NORMAL = "normal"
    FIGHTING = "fighting"
    FLYING = "flying"
    POISON = "poison"
    GROUND = "ground"
    ROCK = "rock"
    BUG = "bug"
    GHOST = "ghost"
    STEEL = "steel"
    FIRE = "fire"
    WATER = "water"
    GRASS = "grass"
    ELECTRIC = "electric"
    PSYCHIC = "psychic"
    ICE = "ice"
    DRAGON = "dragon"
    DARK = "dark"


all_pokemon_types: list[PokemonType] = \
    [pokemon_type for pokemon_type in PokemonType]

__TYPE_DICT__: dict[str, PokemonType] = {
    PokemonType.NORMAL.value: PokemonType.NORMAL,
    PokemonType.FIGHTING.value: PokemonType.FIGHTING,
    PokemonType.FLYING.value: PokemonType.FLYING,
    PokemonType.POISON.value: PokemonType.POISON,
    PokemonType.GROUND.value: PokemonType.GROUND,
    PokemonType.ROCK.value: PokemonType.ROCK,
    PokemonType.BUG.value: PokemonType.BUG,
    "curse": PokemonType.GHOST,
    PokemonType.GHOST.value: PokemonType.GHOST,
    PokemonType.STEEL.value: PokemonType.STEEL,
    PokemonType.FIRE.value: PokemonType.FIRE,
    PokemonType.WATER.value: PokemonType.WATER,
    PokemonType.GRASS.value: PokemonType.GRASS,
    PokemonType.ELECTRIC.value: PokemonType.ELECTRIC,
    PokemonType.PSYCHIC.value: PokemonType.PSYCHIC,
    PokemonType.ICE.value: PokemonType.ICE,
    PokemonType.DRAGON.value: PokemonType.DRAGON,
    PokemonType.DARK.value: PokemonType.DARK,
}


def convert_string_to_pokemon_type(pokemon_type: str) -> PokemonType:
    """
    Gets the enum representing a Pokémon type.
    :param pokemon_type: The string of the type.
    :return: The enum representing pokemon_type.
    """
    return __TYPE_DICT__[pokemon_type.lower()]


if __name__ == '__main__':
    print(__TYPE_DICT__)
