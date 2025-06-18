import json
from collections import defaultdict
from copy import deepcopy
from pprint import pp
from types import MappingProxyType
from typing import Mapping

import cattr
from attrs import frozen

from Config import ATTACKER_TYPE_FILE, DEFENDER_TYPE_FILE
from data_class.PokemonType import PokemonType, convert_string_to_pokemon_type


@frozen
class TypeMatchups:
    type_to_super_effective: Mapping[PokemonType, list[PokemonType]]
    type_to_normal_effective: Mapping[PokemonType, list[PokemonType]]
    type_to_not_effective: Mapping[PokemonType, list[PokemonType]]
    type_to_no_effect: Mapping[PokemonType, list[PokemonType]]


def build_type_matchups(
        type_to_super_effective: defaultdict[PokemonType, list[PokemonType]],
        type_to_normal_effective: defaultdict[PokemonType, list[PokemonType]],
        type_to_not_effective: defaultdict[PokemonType, list[PokemonType]],
        type_to_no_effect: defaultdict[PokemonType, list[PokemonType]]
) -> TypeMatchups:
    return TypeMatchups(
        type_to_super_effective=MappingProxyType(type_to_super_effective),
        type_to_normal_effective=MappingProxyType(type_to_normal_effective),
        type_to_not_effective=MappingProxyType(type_to_not_effective),
        type_to_no_effect=MappingProxyType(type_to_no_effect)
    )


def get_attack_type_dict() -> TypeMatchups:
    with open(ATTACKER_TYPE_FILE, "r") as fo:
        return cattr.structure(json.loads(fo.read()), TypeMatchups)


def get_defender_type_matchups() -> TypeMatchups:
    with open(DEFENDER_TYPE_FILE, "r") as fo:
        return cattr.structure(json.loads(fo.read()), TypeMatchups)


__DEFENDER_TYPE_MATCHUPS__: TypeMatchups = get_defender_type_matchups()

__DEFENSE_MULTIPLIER_CACHE__: dict[PokemonType, dict[PokemonType, float]] = {}


def get_single_type_multiplier(
        pokemon_type: PokemonType
) -> dict[PokemonType, float]:
    if pokemon_type in __DEFENSE_MULTIPLIER_CACHE__:
        pokemon_type: PokemonType
        return deepcopy(__DEFENSE_MULTIPLIER_CACHE__[pokemon_type])

    multipliers: defaultdict[PokemonType, float] = defaultdict(lambda: 1.0)
    for t in __DEFENDER_TYPE_MATCHUPS__.type_to_no_effect.get(pokemon_type, []):
        t: PokemonType
        multipliers[t] *= 0.0
    for t in __DEFENDER_TYPE_MATCHUPS__.type_to_not_effective.get(pokemon_type,
                                                                  []):
        t: PokemonType
        multipliers[t] *= 0.5
    for t in __DEFENDER_TYPE_MATCHUPS__.type_to_super_effective.get(
            pokemon_type, []):
        t: PokemonType
        multipliers[t] *= 2.0

    __DEFENSE_MULTIPLIER_CACHE__[pokemon_type]: dict[PokemonType, float] = \
        multipliers
    return deepcopy(__DEFENSE_MULTIPLIER_CACHE__[pokemon_type])


__DEFENSE_MULTIPLIERS_CACHE__: \
    dict[frozenset[PokemonType], dict[PokemonType, float]] = {}


def get_defense_multipliers_for_types(
        defender_types: frozenset[PokemonType]
) -> dict[PokemonType, float]:
    if defender_types in __DEFENSE_MULTIPLIERS_CACHE__:
        defender_types: frozenset[PokemonType]
        return deepcopy(__DEFENSE_MULTIPLIERS_CACHE__[defender_types])

    result: defaultdict[PokemonType, float] = defaultdict(lambda: 1.0)
    for defender_type in defender_types:
        defender_type: PokemonType
        single_multipliers: dict[PokemonType, float] = \
            get_single_type_multiplier(defender_type)
        for attacker_type, multiplier in single_multipliers.items():
            result[attacker_type] *= multiplier

    __DEFENSE_MULTIPLIERS_CACHE__[defender_types] = result
    return deepcopy(__DEFENSE_MULTIPLIERS_CACHE__[defender_types])


if __name__ == '__main__':
    pp(get_attack_type_dict())
    pp(get_defender_type_matchups())
    print()
