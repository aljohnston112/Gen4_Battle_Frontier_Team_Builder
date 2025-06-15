import pprint
import typing
from collections import defaultdict

import attr

from Config import TRAINER_LIST, TRAINER_SET_LIST
from data_class.Move import Move
from data_class.PokemonType import PokemonType
from data_class.Stat import Stat, StatEnum
from data_source.PokemonTypeDataSource import get_pokemon_types
from data_source.move_data_source import get_moves


@attr.define
class FrontierPokemon:
    name: str
    nature: str
    types: list[PokemonType]
    item: str
    moves: list[Move]
    set_number: int
    effort_values: list[Stat]

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return self.name


def get_next_non_newline(file: typing.IO):
    """
    Gets the next line that is not a new line from a file.

    :param file: The file to get the line from.
    :return: The next line that is not a new line.
    """
    s = "\n"
    while s.isspace():
        s = file.readline()
    return s


def __parse_trainers__() -> dict[str, list[int]]:
    set_to_trainer = defaultdict(lambda: list())
    with open(TRAINER_LIST, "r", encoding='utf-8') as file:
        s = get_next_non_newline(file)
        while s != "":
            tokens = s.split("\t")
            name = tokens[2].strip()
            for i in range(3, 11):
                if tokens[i] == '✔ ' or tokens[i] == '✔\n':
                    set_to_trainer[i - 3].append(name)
            s = get_next_non_newline(file)
    return set_to_trainer


def __parse_effort_value__(stat_enum, stat_token):
    ev = int(stat_token) if stat_token != "-" else 0
    return Stat(stat_enum, ev)


def __parse_frontier_pokemon__() -> dict[int, set[FrontierPokemon]]:
    pokemon = defaultdict(lambda: set())
    set_to_trainers = __parse_trainers__()
    all_pokemon_types: dict[str, list[PokemonType]] = get_pokemon_types()
    pokemon_moves = get_moves()

    with open(TRAINER_SET_LIST, "r", encoding='utf-8') as file:
        s = file.read()
        trainer_sets = s.split("\n,,,,,,,,,,,,,,\n,,,,,,,,,,,,,,\n")
        for trainer_set in trainer_sets:
            tokens = trainer_set.split("\n")
            names = tokens[0].replace(" and ", ", ").split(", ")

            sets = set()

            names[0] = names[0].strip('"')
            names[len(names) - 1] = names[len(names) - 1][:-14].strip('"')

            for name in names:
                sets = sets.union(
                    set(
                        [
                            k for k, v, in set_to_trainers.items()
                            if name in v
                        ]
                    )
                )

            for i in range(4, len(tokens)):
                pokemon_tokens = tokens[i].split(",")
                name = pokemon_tokens[1]
                item = pokemon_tokens[3][:-int(len(pokemon_tokens[3]) / 2 + 1)]
                moves = [
                    pokemon_moves[pokemon_tokens[4]],
                    pokemon_moves[pokemon_tokens[5]],
                    pokemon_moves[pokemon_tokens[6]],
                    pokemon_moves[pokemon_tokens[7]]
                ]
                nature = pokemon_tokens[8]

                effort_values = [
                    __parse_effort_value__(StatEnum.HEALTH, pokemon_tokens[9]),
                    __parse_effort_value__(StatEnum.ATTACK, pokemon_tokens[10]),
                    __parse_effort_value__(StatEnum.DEFENSE,
                                           pokemon_tokens[11]),
                    __parse_effort_value__(StatEnum.SPECIAL_ATTACK,
                                           pokemon_tokens[12]),
                    __parse_effort_value__(StatEnum.SPECIAL_DEFENSE,
                                           pokemon_tokens[13]),
                    __parse_effort_value__(StatEnum.SPEED, pokemon_tokens[14]),
                ]
                for set_number in sets:
                    p = FrontierPokemon(
                        name=name,
                        nature=nature,
                        types=all_pokemon_types[name],
                        item=item,
                        moves=moves,
                        set_number=-1,
                        effort_values=effort_values
                    )
                    pokemon[set_number].add(p)

    return pokemon


if __name__ == '__main__':
    g_set_to_trainer = __parse_trainers__()
    pprint.pprint(g_set_to_trainer)

    g_set_pokemon__ = __parse_frontier_pokemon__()
    pprint.pprint(g_set_pokemon__)
