import json
import pprint
import typing

import cattrs

from Config import MOVES_FILE
from data_class.Move import Move


def get_move_map() -> dict[str, Move]:
    """
    Gets all the moves from Pokémon Platinum.
    :return: A dictionary of move names to detailed move data.
    """
    with open(MOVES_FILE, "r") as fo:
        fo: typing.IO
        moves = cattrs.structure(
            json.loads(fo.read()),
            dict[str, Move]
        )
        return moves


if __name__ == '__main__':
    g_moves: dict[str, Move] = get_move_map()
    pprint.pprint(g_moves)
