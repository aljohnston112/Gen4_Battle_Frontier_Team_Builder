import attr
from attr import frozen

from Config import LEVEL
from data_class.AllStats import AllStats
from data_class.BaseStats import BaseStats, get_base_stat
from data_class.Move import Move
from data_class.PokemonInformation import PokemonInformation
from data_class.Stat import StatEnum, calculate_health_stat, \
    calculate_non_health_stat
from data_class.Stats import Stats

LevelToAttacks = dict[int, list[Move]]
TmOrHmToAttacks = dict[str, Move]
FormToAttacks = dict[str, list[Move]]


@frozen
class SerebiiPokemon:
    pokemon_information: PokemonInformation
    all_stats: AllStats
    level_to_attacks: LevelToAttacks
    tm_or_hm_to_attack: TmOrHmToAttacks | None = attr.field(default=None)

    egg_moves: list[Move] | None = attr.field(default=None)
    pre_evolution_index_to_level_to_moves: \
        dict[int, LevelToAttacks] | None = attr.field(default=None)
    move_tutor_attacks: list[Move] | None = attr.field(default=None)

    game_to_level_to_moves: dict[str, LevelToAttacks] | None = \
        attr.field(default=None)
    special_moves: list[Move] | None = attr.field(default=None)

    form_to_all_stats: dict[str, AllStats] | None = attr.field(default=None)
    form_to_level_up_attacks: dict[str, LevelToAttacks] | None = \
        attr.field(default=None)
    form_to_tm_or_hm_to_attack: dict[str, TmOrHmToAttacks] | None = \
        attr.field(default=None)
    form_to_move_tutor_attacks: FormToAttacks | None = attr.field(default=None)


def get_stat_for_serebii_pokemon(
        base_stats: BaseStats,
        ev: int,
        stat_enum: StatEnum,
) -> int:
    stats: Stats = base_stats.stats
    if stat_enum == StatEnum.HEALTH:
        stat: int = calculate_health_stat(
            base=stats.health,
            iv=0,
            ev=ev
        )
    else:
        stat: int = calculate_non_health_stat(
            base=get_base_stat(base_stats, stat_enum),
            iv=0,
            ev=ev,
            nature_multiplier=1.0
        )
    return stat


def get_all_moves(pokemon: SerebiiPokemon) -> list[Move]:
    moves = []

    for attack_level, move_list in pokemon.level_to_attacks.items():
        if attack_level <= LEVEL:
            moves.extend(move_list)

    if pokemon.tm_or_hm_to_attack is not None:
        moves.extend(pokemon.tm_or_hm_to_attack.values())

    if pokemon.egg_moves is not None:
        moves.extend(pokemon.egg_moves)

    if pokemon.pre_evolution_index_to_level_to_moves is not None:
        for level_to_moves in pokemon.pre_evolution_index_to_level_to_moves.values():
            for attack_level, moves in level_to_moves.items():
                if attack_level <= LEVEL:
                    moves.extend(moves)

    if pokemon.move_tutor_attacks is not None:
        moves.extend(pokemon.move_tutor_attacks)

    if pokemon.game_to_level_to_moves is not None:
        for level_to_moves in pokemon.game_to_level_to_moves.values():
            for attack_level, move_list in level_to_moves.items():
                if attack_level <= LEVEL:
                    moves.extend(move_list)

    if pokemon.special_moves is not None:
        moves.extend(pokemon.special_moves)

    if pokemon.form_to_level_up_attacks is not None:
        for level_to_attacks in pokemon.form_to_level_up_attacks.values():
            for attack_level, move_list in level_to_attacks.items():
                if attack_level <= LEVEL:
                    moves.extend(move_list)

    if pokemon.form_to_tm_or_hm_to_attack is not None:
        for moves_list in pokemon.form_to_tm_or_hm_to_attack.values():
            moves.extend(moves_list.values())

    if pokemon.form_to_move_tutor_attacks is not None:
        for moves_list in pokemon.form_to_move_tutor_attacks.values():
            moves.extend(moves_list)

    return moves