import pprint
import typing
from collections import defaultdict

from attrs import frozen

from Config import TRAINER_LIST_FILE, TRAINER_SET_LIST_FILE
from data_class.FrontierPokemon import FrontierPokemon
from data_class.Move import Move
from data_class.PokemonType import PokemonType
from data_class.Stat import Stat, StatEnum
from data_source.PokemonTypeDataSource import get_pokemon_to_types_map
from data_source.move_data_source import get_move_map


@frozen
class TrainerSet:
    trainer_name: str
    set_numbers: set[int]
    pokemon: set[FrontierPokemon]


def get_next_non_newline(file: typing.IO) -> str:
    """
    Gets the next line that is not a new line from a file.

    :param file: The file to get the line from.
    :return: The next line that is not a new line.
    """
    line: str = "\n"
    while line.isspace():
        line: str = file.readline()
    return line


def __get_set_to_trainers__() -> dict[int, list[str]]:
    set_to_trainers: dict[int, list[str]] = defaultdict(lambda: list())
    with open(TRAINER_LIST_FILE, "r", encoding='utf-8') as file:
        line: str = get_next_non_newline(file)
        while line != "":
            tokens: list[str] = line.split("\t")
            trainer_names: str = tokens[2].strip()
            for i in range(3, 11):
                i: int
                if tokens[i] == '✔ ' or tokens[i] == '✔\n':
                    set_to_trainers[i - 3].append(trainer_names)
            line: str = get_next_non_newline(file)
    return set_to_trainers


def __parse_effort_value__(stat_enum: StatEnum, stat_token: str) -> Stat:
    ev: int = int(stat_token) if stat_token != "-" else 0
    return Stat(stat_enum, ev)


def get_frontier_pokemon() -> dict[str, TrainerSet]:
    trainer_to_trainer_set_map: dict[str, TrainerSet] = {}
    all_trainers: dict[int, list[str]] = __get_set_to_trainers__()
    all_pokemon_types: dict[str, list[PokemonType]] = get_pokemon_to_types_map()
    all_moves: dict[str, Move] = get_move_map()
    with open(TRAINER_SET_LIST_FILE, "r", encoding='utf-8') as file:
        file: typing.IO
        file_text: str = file.read()
        trainer_sets: list[str] = file_text.split(
            "\n,,,,,,,,,,,,,,\n,,,,,,,,,,,,,,\n")
        for trainer_set in trainer_sets:
            trainer_set: str
            tokens: list[str] = trainer_set.split("\n")
            names: list[str] = \
                tokens[0].replace(" and ", ", ").split(", ")
            names[0]: str = names[0].strip('"')
            names[len(names) - 1]: str = names[len(names) - 1][:-14].strip('"')

            set_numbers: set[int] = set()
            trainer_pokemon: set[FrontierPokemon] = set()
            for name in names:
                name: str
                set_numbers: set[int] = set_numbers.union(
                    set([
                        set_number
                        for set_number, trainer_name in all_trainers.items()
                        if name in trainer_name
                    ])
                )

            for i in range(4, len(tokens)):
                i: int
                pokemon_tokens: list[str] = tokens[i].split(",")
                name: str = pokemon_tokens[1]
                item: str = pokemon_tokens[3][
                            :-int(len(pokemon_tokens[3]) / 2 + 1)]
                moves: list[Move] = [
                    all_moves[pokemon_tokens[4]],
                    all_moves[pokemon_tokens[5]],
                    all_moves[pokemon_tokens[6]],
                    all_moves[pokemon_tokens[7]]
                ]
                nature: str = pokemon_tokens[8]
                effort_values: list[Stat] = [
                    __parse_effort_value__(StatEnum.HEALTH, pokemon_tokens[9]),
                    __parse_effort_value__(StatEnum.ATTACK, pokemon_tokens[10]),
                    __parse_effort_value__(
                        StatEnum.DEFENSE,
                        pokemon_tokens[11]
                    ),
                    __parse_effort_value__(
                        StatEnum.SPECIAL_ATTACK,
                        pokemon_tokens[12]
                    ),
                    __parse_effort_value__(
                        StatEnum.SPECIAL_DEFENSE,
                        pokemon_tokens[13]
                    ),
                    __parse_effort_value__(StatEnum.SPEED, pokemon_tokens[14]),
                ]
                frontier_pokemon: FrontierPokemon = FrontierPokemon(
                    name=name,
                    nature=nature,
                    types=all_pokemon_types[name],
                    item=item,
                    moves=moves,
                    effort_values=effort_values,
                    set_numbers=[s for s in set_numbers]
                )
                trainer_pokemon.add(frontier_pokemon)
            trainer_names: str = ",".join(names)
            trainer_to_trainer_set_map[trainer_names]: TrainerSet = TrainerSet(
                trainer_name=trainer_names,
                set_numbers=set_numbers,
                pokemon=trainer_pokemon
            )
    return trainer_to_trainer_set_map


if __name__ == '__main__':
    g_set_to_trainer: dict[int, list[str]] = __get_set_to_trainers__()
    pprint.pprint(g_set_to_trainer)

    g_set_pokemon: dict[str, TrainerSet] = get_frontier_pokemon()
    pprint.pprint(g_set_pokemon)
