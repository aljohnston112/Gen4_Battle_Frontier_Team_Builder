from typing import Dict, List, Optional

import attr
from attr import frozen

from data_class.AllStats import AllStats
from data_class.Attack import Attack
from data_class.PokemonInformation import PokemonInformation


@frozen
class Pokemon:
    pokemon_information: PokemonInformation
    all_stats: AllStats
    level_to_attacks: Dict[int, List[Attack]]
    tm_or_hm_to_attack: Optional[Dict[str, Attack]] = attr.field(default=None)

    egg_moves: Optional[List[Attack]] = attr.field(default=None)
    pre_evolution_index_to_level_to_moves: Optional[Dict[int, Dict[int, List[Attack]]]] = attr.field(default=None)
    move_tutor_attacks: Optional[List[Attack]] = attr.field(default=None)

    game_to_level_to_moves: Optional[Dict[str, Dict[int, List[Attack]]]] = attr.field(default=None)
    special_moves: Optional[List[Attack]] = attr.field(default=None)

    form_to_all_stats: Optional[Dict[str, AllStats]] = attr.field(default=None)
    form_to_level_up_attacks: Optional[Dict[str, Dict[int, List[Attack]]]] = attr.field(default=None)
    form_to_tm_or_hm_to_attack: Optional[Dict[str, Dict[str, Attack]]] = attr.field(default=None)
    form_to_move_tutor_attacks: Optional[Dict[str, List[Attack]]] = attr.field(default=None)
