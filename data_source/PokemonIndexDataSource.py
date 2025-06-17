import json
import pprint

from Config import POKEMON_INDICES_FILE


def get_index_to_pokemon_name_map() -> dict[int, str]:
    with open(POKEMON_INDICES_FILE, "r") as fo:
        return json.loads(fo.read())


def get_pokemon_name_to_index() -> dict[str, int]:
    index_to_pokemon_name_map: dict[int, str] = get_index_to_pokemon_name_map()
    return {name: index for index, name in index_to_pokemon_name_map.items()}


if __name__ == "__main__":
    index_to_pokemon = get_index_to_pokemon_name_map()
    pprint.pp(index_to_pokemon)
    print()
    pokemon_to_index = get_pokemon_name_to_index()
    pprint.pp(pokemon_to_index)
