import json
import pprint

import cattr

from Config import POKEMON_TYPE_FILE
from data_class.PokemonType import PokemonType


def get_pokemon_types() -> dict[str, list[PokemonType]]:
    """
    Gets a name to Pokémon dict containing all possible battle frontier Pokémon.
    :return: The name to Pokémon dict containing all possible battle frontier Pokémon.
    """
    with open(POKEMON_TYPE_FILE, "r") as fo:
        pokemon_to_types = cattr.structure(json.loads(fo.read()), dict[str, list[PokemonType]])
    return pokemon_to_types


if __name__ == '__main__':
    pokemon_to_types = get_pokemon_types()
    pprint.pprint(pokemon_to_types)