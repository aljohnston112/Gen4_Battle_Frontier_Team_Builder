from collections import defaultdict

from data_source.TypeChartDataSource import get_defender_type_dict

level = 50
defender_type_chart = get_defender_type_dict()

defense_multiplier_cache = {}

def get_single_type_multiplier(pokemon_type: str) -> dict[str, float]:
    if pokemon_type in defense_multiplier_cache:
        return defense_multiplier_cache[pokemon_type].copy()

    multipliers = defaultdict(lambda: 1.0)
    for t in defender_type_chart[0].get(pokemon_type, []):
        multipliers[t] *= 0.0
    for t in defender_type_chart[1].get(pokemon_type, []):
        multipliers[t] *= 0.5
    for t in defender_type_chart[2].get(pokemon_type, []):
        multipliers[t] *= 1.0
    for t in defender_type_chart[3].get(pokemon_type, []):
        multipliers[t] *= 2.0

    defense_multiplier_cache[pokemon_type] = multipliers.copy()
    return multipliers

defense_multipliers_cache = {}

def get_defense_multipliers_for_types(defender_types: frozenset[str]) -> dict[str, float]:
    if defender_types in defense_multipliers_cache:
        return defense_multipliers_cache[defender_types].copy()

    result = defaultdict(lambda: 1.0)
    for t in sorted(defender_types):  # sort for deterministic order
        single = get_single_type_multiplier(t)
        for atk_type, mult in single.items():
            result[atk_type] *= mult

    defense_multipliers_cache[defender_types] = result.copy()
    return result

if __name__ == "__main__":
    pass