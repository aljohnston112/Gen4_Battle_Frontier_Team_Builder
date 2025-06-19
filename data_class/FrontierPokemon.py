import attr

from data_class.BaseStats import BaseStats, get_base_stat
from data_class.Category import Category
from data_class.Move import Move
from data_class.Nature import NatureEnum, get_nature_enum, get_nature_multiplier
from data_class.PokemonState import CustomPokemon, CustomMove
from data_class.PokemonType import PokemonType
from data_class.SerebiiPokemon import SerebiiPokemon
from data_class.Stat import Stat, StatEnum, calculate_health_stat, \
    calculate_non_health_stat
from data_class.Stats import Stats
from data_source.PokemonIndexDataSource import get_pokemon_name_to_index


@attr.define(frozen=True, hash=False)
class FrontierPokemon:
    name: str
    nature: str
    types: list[PokemonType]
    item: str
    moves: list[Move]
    effort_values: list[Stat]
    set_numbers: list[int]

    def __hash__(self):
        return hash((
            self.name,
            tuple(sorted([m.name for m in self.moves])),
        ))

    def __eq__(self, other):
        return (
                isinstance(other, FrontierPokemon)
                and self.name == other.name
                and sorted(m.name for m in self.moves) == sorted(
            m.name for m in other.moves)
        )


def get_stat_for_frontier_pokemon(
        frontier_pokemon: FrontierPokemon,
        base_stats: BaseStats,
        iv: int,
        stat_enum: StatEnum,
) -> int:
    stats: Stats = base_stats.stats
    ev = next(
        (s.value for s in frontier_pokemon.effort_values
         if s.stat_type == stat_enum),
    )
    if stat_enum == StatEnum.HEALTH:
        stat: int = calculate_health_stat(
            base=stats.health,
            iv=iv,
            ev=ev
        )
    else:
        nature_enum: NatureEnum = get_nature_enum(frontier_pokemon.nature)
        stat: int = calculate_non_health_stat(
            base=get_base_stat(base_stats, stat_enum),
            iv=iv,
            ev=ev,
            nature_multiplier=
            get_nature_multiplier(stat_enum, nature_enum)
        )
    return stat

pokemon_to_index = get_pokemon_name_to_index()


def convert_frontier_to_custom(
        pokemon_map: dict[int, SerebiiPokemon],
        set_number: int,
        frontier_pokemon: FrontierPokemon,
) -> CustomPokemon:
    custom_moves = [
        CustomMove(
            name=move.name,
            power=move.power,
            move_type=move.move_type,
            is_special=(move.category == Category.SPECIAL),
        )
        for move in frontier_pokemon.moves
    ]

    pokemon: SerebiiPokemon = pokemon_map[
        pokemon_to_index[frontier_pokemon.name]]
    base_stats = pokemon.all_stats.base_stats
    if set_number == 7:
        iv = 31
    else:
        iv = (set_number + 1) * 3
        iv = min(iv, 31)
    hp = get_stat_for_frontier_pokemon(
        frontier_pokemon=frontier_pokemon,
        base_stats=base_stats,
        iv=iv,
        stat_enum=StatEnum.HEALTH,
    )

    attack: int = get_stat_for_frontier_pokemon(
        frontier_pokemon=frontier_pokemon,
        base_stats=base_stats,
        iv=iv,
        stat_enum=StatEnum.ATTACK,
    )

    special_attack: int = get_stat_for_frontier_pokemon(
        frontier_pokemon=frontier_pokemon,
        base_stats=base_stats,
        iv=iv,
        stat_enum=StatEnum.SPECIAL_ATTACK,
    )

    defense: int = get_stat_for_frontier_pokemon(
        frontier_pokemon=frontier_pokemon,
        base_stats=base_stats,
        iv=iv,
        stat_enum=StatEnum.DEFENSE,
    )

    special_defense: int = get_stat_for_frontier_pokemon(
        frontier_pokemon=frontier_pokemon,
        base_stats=base_stats,
        iv=iv,
        stat_enum=StatEnum.SPECIAL_DEFENSE,
    )

    speed: int = get_stat_for_frontier_pokemon(
        frontier_pokemon=frontier_pokemon,
        base_stats=base_stats,
        iv=iv,
        stat_enum=StatEnum.SPEED,
    )

    return CustomPokemon(
        name=pokemon.pokemon_information.name,
        hp=hp,
        attack=attack,
        special_attack=special_attack,
        defense=defense,
        special_defense=special_defense,
        speed=speed,
        types=frontier_pokemon.types,
        moves=custom_moves,
        item=frontier_pokemon.item
    )