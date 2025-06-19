import json
import pprint
import typing

from Config import POKEMON_INDICES_FILE

FULLY_EVOLVED_OBTAINABLE_POKEMON: list[int] = [
    12, 15, 18, 20, 22, 24, 26, 28, 31, 34, 36, 38, 40, 45, 47, 49, 51, 53, 55,
    57, 59, 62, 71, 73, 78, 80, 83, 85, 87, 89, 91, 95, 97, 99, 101, 103, 105,
    106, 107, 110, 112, 115, 117, 119, 121, 122, 123, 124, 125, 126, 127, 128,
    130, 131, 132, 134, 135, 136, 137, 139, 141, 142, 143, 149, 162, 164, 166,
    168, 169, 171, 178, 181, 182, 184, 185, 189, 192, 195, 196, 197, 201, 202,
    203, 205, 206, 210, 211, 213, 214, 217, 219, 222, 224, 225, 226, 227, 229,
    232, 234, 235, 237, 241, 242, 248, 262, 264, 267, 269, 272, 275, 277, 279,
    282, 284, 286, 288, 291, 292, 295, 297, 301, 302, 303, 306, 308, 310, 311,
    312, 313, 314, 317, 319, 321, 323, 324, 326, 327, 330, 332, 334, 335, 336,
    337, 338, 340, 342, 344, 346, 348, 350, 351, 352, 354, 356, 357, 358, 359,
    362, 365, 366, 369, 370, 373, 376, 398, 400, 402, 405, 407, 409, 411, 414,
    416, 417, 419, 421, 423, 424, 426, 428, 429, 430, 432, 435, 437, 441, 442,
    445, 448, 450, 452, 454, 455, 457, 460, 461, 462, 463, 465, 468, 469, 470,
    471, 472, 473, 475, 476, 478, 479, 480, 481, 482, 485
]


def get_index_to_pokemon_name_map() -> dict[int, str]:
    with open(POKEMON_INDICES_FILE, "r") as fo:
        fo: typing.IO
        return json.loads(fo.read())


def get_pokemon_name_to_index() -> dict[str, int]:
    index_to_pokemon_name_map: dict[int, str] = get_index_to_pokemon_name_map()
    return {
        name: int(index)
        for index, name in index_to_pokemon_name_map.items()
    }


if __name__ == "__main__":
    index_to_pokemon: dict[int, str] = get_index_to_pokemon_name_map()
    pprint.pp(index_to_pokemon)
    print()
    pokemon_to_index: dict[str, int] = get_pokemon_name_to_index()
    pprint.pp(pokemon_to_index)
