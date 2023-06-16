from typing import Dict, List

from attr import frozen

from data_class.AllStats import AllStats
from data_class.Attack import Attack
from data_class.PokemonInformation import PokemonInformation


@frozen
class Pokemon:
    pokemon_information: PokemonInformation

    all_stats: AllStats
    form_to_all_stats: Dict[str, AllStats]

    level_to_attacks: Dict[int, List[Attack]]
    form_to_level_up_attacks: Dict[str, Dict[int, List[Attack]]]

    tm_or_hm_to_attack: Dict[str, Attack]
    form_to_tm_or_hm_to_attack: Dict[str, Attack]

    move_tutor_attacks: List[Attack]
    form_to_move_tutor_attacks: Dict[str, List[Attack]]

    egg_moves: List[Attack]

    game_to_level_to_moves: Dict[str, Dict[int, List[Attack]]]