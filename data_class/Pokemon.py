import attr
from attr import frozen

from data_class.AllStats import AllStats
from data_class.Move import Move
from data_class.PokemonInformation import PokemonInformation


LevelToAttacks = dict[int, list[Move]]
TmOrHmToAttacks = dict[str, Move]
FormToAttacks = dict[str, list[Move]]


@frozen
class Pokemon:
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
