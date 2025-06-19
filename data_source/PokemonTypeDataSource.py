import json
import pprint
import typing

import cattr

from Config import POKEMON_TYPE_FILE
from data_class.PokemonType import PokemonType


def get_pokemon_to_types_map() -> dict[str, list[PokemonType]]:
    """
    Gets a name to Pokémon dict containing all possible battle frontier Pokémon.
    :return: The name to Pokémon dict containing all possible battle frontier Pokémon.
    """
    with open(POKEMON_TYPE_FILE, "r") as fo:
        fo: typing.IO
        pokemon_to_types: dict[str, list[PokemonType]] = cattr.structure(
            json.loads(fo.read()),
            dict[str, list[PokemonType]]
        )
    return pokemon_to_types


if __name__ == '__main__':
    g_pokemon_to_types: dict[str, list[PokemonType]] = \
        get_pokemon_to_types_map()
    pprint.pprint(g_pokemon_to_types)
