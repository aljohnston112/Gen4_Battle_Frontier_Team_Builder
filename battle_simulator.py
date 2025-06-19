from dataclasses import dataclass
from itertools import combinations
from math import floor, inf

from attrs import frozen

from damage_calculator import CustomPokemon, CustomMove, IMPLEMENTED_ITEMS, \
    convert_frontier_to_custom, get_max_damage_attacker_can_do_to_defender, \
    get_all_attacks, bad_moves, convert_to_custom_move, charge_moves, \
    get_stat_for_serebii_pokemon
from data_class.BaseStats import BaseStats
from data_class.PokemonType import PokemonType
from data_class.SerebiiPokemon import SerebiiPokemon
from data_class.Stat import StatEnum
from data_source.FrontierPokemonDataSource import get_all_frontier_pokemon
from data_source.PokemonDataSource import get_legal_serebii_pokemon
from data_source.PokemonIndexDataSource import fully_evolved_obtainable_pokemon, \
    get_pokemon_name_to_index
from data_source.PokemonTypeDataSource import get_pokemon_to_types_map
from data_source.TypeChartDataSource import get_defense_multipliers_for_types


@frozen
class Hits:
    hits_taken: float
    hits_given: float


@dataclass
class BattleResult:
    hits: Hits


@dataclass
class BattleResults:
    name: str
    win_results: dict[CustomMove, dict[CustomPokemon, BattleResult]]
    loss_results: dict[CustomMove, dict[CustomPokemon, BattleResult]]


def get_health_gained(
        attacking_pokemon: CustomPokemon,
        move: str,
        attack_damage: float,
        was_first: bool,
        max_health: int,
        current_health: int,
        hold_item: str,
        is_player: bool,
        player_turns_badly_poisoned: int
) -> int:
    health_gain_before_loss: int = 0
    health_gained: int = 0
    health_lost: int = 0

    if move in ["Explosion", "Selfdestruct"]:
        return -current_health

    recoil: int = 0
    if move in [
        "Brave Bird", "Double-Edge", "Flare Blitz", "Volt Tackle", "Wood Hammer"
    ]:
        recoil = floor(attack_damage / 3)
    elif move in ["Head Smash"]:
        recoil = floor(attack_damage / 2)
    elif move in ["Submission", "Take Down"]:
        recoil = floor(attack_damage / 4)

    health_lost += recoil

    # Toxic
    if player_turns_badly_poisoned > 0:
        health_lost += player_turns_badly_poisoned * (max_health // 16)

    # Draining moves and Big Root
    if move in ["Drain Punch", "Giga Drain", "Mega Drain"]:
        if current_health != 0 or was_first:
            health_gain_before_loss += attack_damage // 2
            if hold_item == "Big Root":
                health_gain_before_loss = floor(health_gain_before_loss * 1.3)
        else:
            health_gained += attack_damage // 2
            if hold_item == "Big Root":
                health_gained = floor(health_gained * 1.3)

    # Sitrus Berry
    if hold_item == "Sitrus Berry" and current_health < max_health // 2:
        health_gained += max_health // 4
        attacking_pokemon.item = ""

    # Black Sludge
    elif hold_item == "Black Sludge":
        has_magic_guard: bool = attacking_pokemon.name in [
            "Clefairy", "Clefable", "Kadabra", "Alakazam"
        ]
        if not has_magic_guard:
            is_poison: bool = PokemonType.POISON in attacking_pokemon.types
            if is_poison and not is_player:
                health_gained += max_health // 16
            elif is_player:
                health_lost += max_health // 8
    # Leftovers
    elif hold_item == "Leftovers":
        health_gained += max_health // 16

    # Life Orb
    elif hold_item == "Life Orb":
        health_lost += max_health // 10

    # Shell Bell
    elif hold_item == "Shell Bell":
        if current_health != 0 or was_first:
            health_gain_before_loss += attack_damage // 8
        else:
            health_gained += attack_damage // 8

    if current_health + health_gain_before_loss < health_lost:
        return -current_health

    return health_gain_before_loss + health_gained - health_lost


__berry_resistances__: dict[PokemonType, str] = {
    PokemonType.FIGHTING: "Chople Berry",
    PokemonType.FLYING: "Coba Berry",
    PokemonType.DARK: "Colbur Berry",
    PokemonType.DRAGON: "Haban Berry",
    PokemonType.GHOST: "Kasib Berry",
    PokemonType.FIRE: "Occa Berry",
    PokemonType.WATER: "Passho Berry",
    PokemonType.PSYCHIC: "Payapa Berry",
    PokemonType.GRASS: "Rindo Berry",
    PokemonType.GROUND: "Shuca Berry",
    PokemonType.ELECTRIC: "Wacan Berry",
    PokemonType.ICE: "Yache Berry",
    PokemonType.ROCK: "Charti Berry"
}

type_map: dict[str, list[PokemonType]] = get_pokemon_to_types_map()


def apply_damage_modifiers(
        defender: CustomPokemon,
        defender_item: str,
        attacker_attack: CustomMove | None,
        damage_taken: int,
        defender_defense_multipliers: dict[PokemonType, float]
) -> int:
    if attacker_attack is None:
        return damage_taken
    type_multiplier: float = \
        defender_defense_multipliers.get(attacker_attack.move_type, 1.0)
    resist_berry: str = __berry_resistances__.get(attacker_attack.move_type)
    if (type_multiplier >= 2.0) and (defender_item == resist_berry):
        damage_taken = damage_taken // 2
        defender.item = ""
    return damage_taken


def convert_serebii_to_custom(
        player_pokemon: SerebiiPokemon,
        hp_ev: int,
        attack_ev: int,
        defense_ev: int,
        special_attack_ev: int,
        special_defense_ev: int,
        speed_ev: int,
        item: str
) -> CustomPokemon:
    all_moves = [
        convert_to_custom_move(move)
        for move in get_all_attacks(player_pokemon)
        if
        move.accuracy == 100 and move.name not in bad_moves and move.power != 0
    ]
    best_moves = {}
    for move in all_moves:
        key = (move.move_type, move.is_special)
        if key not in best_moves or move.power > best_moves[key].power:
            best_moves[key] = move
    filtered_moves = list(best_moves.values())
    stats: BaseStats = player_pokemon.all_stats.base_stats
    return CustomPokemon(
        name=player_pokemon.pokemon_information.name,
        types=player_pokemon.pokemon_information.pokemon_types,
        moves=filtered_moves,
        hp=get_stat_for_serebii_pokemon(stats, hp_ev, StatEnum.HEALTH),
        attack=get_stat_for_serebii_pokemon(stats, attack_ev, StatEnum.ATTACK),
        special_attack=get_stat_for_serebii_pokemon(stats, special_attack_ev, StatEnum.SPECIAL_ATTACK),
        defense=get_stat_for_serebii_pokemon(stats, defense_ev, StatEnum.DEFENSE),
        special_defense=get_stat_for_serebii_pokemon(stats, special_defense_ev, StatEnum.SPECIAL_DEFENSE),
        speed=get_stat_for_serebii_pokemon(stats, speed_ev, StatEnum.SPEED),
        item=item
    )

pokemon_map: dict[int, SerebiiPokemon] = {
    k: v for k, v in get_legal_serebii_pokemon().items()
}

frontier_pokemon: set[CustomPokemon] = set([
    # max IVs
    convert_frontier_to_custom(pokemon_map, 100, p)
    for p in get_all_frontier_pokemon()
    if 1 in p.set_numbers
])

player_random = 1.0
opponent_random = 1.0

def get_pokemon_to_pokemon_they_can_beat() -> dict[str, BattleResults]:
    winner_to_defeated: dict[str, BattleResults] = dict()

    all_player_pokemon = [
        convert_serebii_to_custom(
            pokemon,
            hp_ev=0,
            attack_ev=0,
            defense_ev=0,
            special_attack_ev=0,
            special_defense_ev=0,
            speed_ev=0,
            item=""
        )
        for k, pokemon in pokemon_map.items()
        if k in fully_evolved_obtainable_pokemon
    ]

    # pokemon_to_index = get_pokemon_name_to_index()
    # all_player_pokemon = [
    #     convert_serebii_to_custom(
    #         pokemon_map[pokemon_to_index["Heatran"]],
    #         hp_ev=0,
    #         attack_ev=0,
    #         defense_ev=0,
    #         special_attack_ev=252,
    #         special_defense_ev=0,
    #         speed_ev=252,
    #         item=""
    #     ),
    #     convert_serebii_to_custom(
    #         pokemon_map[pokemon_to_index["Garchomp"]],
    #         hp_ev=252,
    #         attack_ev=252,
    #         defense_ev=0,
    #         special_attack_ev=0,
    #         special_defense_ev=0,
    #         speed_ev=0,
    #         item=""
    #     ),
    #     convert_serebii_to_custom(
    #         pokemon_map[pokemon_to_index["Mesprit"]],
    #         hp_ev=252,
    #         attack_ev=0,
    #         defense_ev=0,
    #         special_attack_ev=252,
    #         special_defense_ev=0,
    #         speed_ev=0,
    #         item="Choice Specs"
    #     )
    # ]

    for player_pokemon in all_player_pokemon:
        # Get the best 4 moves
        player_defense_multipliers: dict[PokemonType, float] = \
            get_defense_multipliers_for_types(
                frozenset(player_pokemon.types))

        player_item_backup: str = str(player_pokemon.item)
        if player_pokemon.item not in IMPLEMENTED_ITEMS:
            raise Exception(f"Item {player_pokemon.item} not implemented")
        player_max_health: int = player_pokemon.hp
        player_speed_stat: int = player_pokemon.speed
        if player_pokemon.item == "Choice Scarf":
            player_speed_stat: int = floor(1.5 * player_speed_stat)

        lose_results, win_results = perform_battle_simulation(
            player_pokemon=player_pokemon,
            player_defense_multipliers=player_defense_multipliers,
            player_max_health=player_max_health,
            player_speed_stat=player_speed_stat,
        )
        player_pokemon.item = player_item_backup

        win_results = dict(sorted(
            win_results.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:4])
        player_pokemon.moves = [k for k in win_results.keys()]

        # Get the battle results using the best 4 moves of each Pokémon
        lose_results, win_results = perform_battle_simulation(
            player_pokemon=player_pokemon,
            player_defense_multipliers=player_defense_multipliers,
            player_max_health=player_max_health,
            player_speed_stat=player_speed_stat,
        )
        player_pokemon.item = player_item_backup
        winner_to_defeated[player_pokemon.name]: BattleResults = \
            BattleResults(
                name=player_pokemon.name,
                win_results=win_results,
                loss_results=lose_results,
            )
    return dict(sorted(
        winner_to_defeated.items(),
        key=lambda x: sum(len(v) for v in x[1].win_results.values()),
        reverse=True
    ))

def perform_battle_simulation(
        player_pokemon: CustomPokemon,
        player_defense_multipliers: dict[PokemonType, float],
        player_max_health: int,
        player_speed_stat: int,
):
    win_results: dict[
        CustomMove, dict[CustomPokemon, BattleResult]] = dict()
    lose_results: dict[
        CustomMove, dict[CustomPokemon, BattleResult]] = dict()

    for i, opponent_pokemon in enumerate(frontier_pokemon):
        opponent_defense_multipliers: dict[PokemonType, float] = \
            get_defense_multipliers_for_types(
                frozenset(opponent_pokemon.types)
            )
        opponent_item_backup: str = str(opponent_pokemon.item)
        if opponent_pokemon.item not in IMPLEMENTED_ITEMS:
            raise Exception(f"{opponent_pokemon.item} not implemented")
        opponent_max_health: int = opponent_pokemon.hp
        # Who is faster?
        opponent_speed_stat: int = opponent_pokemon.speed
        if opponent_pokemon.item == "Choice Scarf":
            opponent_speed_stat: int = floor(1.5 * opponent_speed_stat)
        player_first: bool = player_speed_stat > opponent_speed_stat
        if opponent_pokemon.item == "Quick Claw":
            player_first = False

        opponent_attack_damage, opponent_attack = \
            get_max_damage_attacker_can_do_to_defender(
                attacker=opponent_pokemon,
                defender=player_pokemon,
                random=opponent_random,
                is_poisoned=False,
                defender_defense_multipliers=player_defense_multipliers
            )
        player_attack_damage, player_attack = \
            get_max_damage_attacker_can_do_to_defender(
                attacker=player_pokemon,
                defender=opponent_pokemon,
                random=player_random,
                is_poisoned=False,
                defender_defense_multipliers=opponent_defense_multipliers
            )
        hits_taken: float = inf
        if opponent_attack_damage != 0:
            hits_taken: float = player_max_health / opponent_attack_damage
        hits_given: float = inf
        if player_attack_damage != 0:
            hits_given: float = opponent_max_health / player_attack_damage
        hits: Hits = Hits(hits_taken=hits_taken, hits_given=hits_given)

        player_health: int = player_max_health
        opponent_health: int = opponent_max_health
        is_first_turn = True
        # TODO pluck and bug bite will eat berries
        if ((opponent_attack_damage != 0 or player_attack_damage != 0)
                and opponent_attack and player_attack
        ):
            opponent_turns_poisoned: int = -1
            player_turns_poisoned: int = -1
            opponent_must_charge = False
            while player_health > 0 and opponent_health > 0:
                actual_player_damage: int = player_attack_damage
                actual_opponent_damage: int = opponent_attack_damage
                if not player_pokemon.item == "":
                    actual_opponent_damage = apply_damage_modifiers(
                        defender=player_pokemon,
                        defender_item=player_pokemon.item,
                        attacker_attack=opponent_attack,
                        damage_taken=opponent_attack_damage,
                        defender_defense_multipliers=player_defense_multipliers
                    )

                    # Stat boosting berries
                    if ((player_health <= player_max_health // 4) or
                            (player_health <= player_health // 2 and
                             (player_pokemon.name in
                              ["Shuckle", "Zigzagoon", "Linoone"]))
                    ):
                        if player_attack:
                            player_move_is_special: bool = \
                                player_attack.is_special
                            if ((player_pokemon.item == "Liechi Berry" and
                                 not player_move_is_special
                            ) or (player_pokemon.item == "Petaya Berry" and
                                  player_move_is_special
                            )):
                                # kind of a hack, as attack is multiplied, not damage
                                actual_player_damage: int = \
                                    floor(1.5 * actual_player_damage)
                                player_pokemon.item = ""
                        if player_pokemon.item == "Salac Berry":
                            player_speed_stat: int = \
                                floor(1.5 * player_speed_stat)
                            player_first: bool = \
                                (player_speed_stat > opponent_speed_stat and
                                 opponent_pokemon.item != "Quick Claw")
                            player_pokemon.item = ""

                    if (player_attack and
                            player_attack.name in [
                                "Sky Attack", "Solarbeam"
                            ]
                    ):
                        player_attack_damage, player_attack = \
                            get_max_damage_attacker_can_do_to_defender(
                                attacker=player_pokemon,
                                defender=opponent_pokemon,
                                random=player_random,
                                is_poisoned=player_turns_poisoned > -1,
                                defender_defense_multipliers=opponent_defense_multipliers
                            )
                        player_pokemon.item = ""

                if not opponent_pokemon.item == "":
                    actual_player_damage = apply_damage_modifiers(
                        defender=opponent_pokemon,
                        defender_item=opponent_pokemon.item,
                        attacker_attack=player_attack,
                        damage_taken=player_attack_damage,
                        defender_defense_multipliers=opponent_defense_multipliers
                    )

                    # Stat boosting berries
                    if (((opponent_health <= opponent_max_health // 4) or
                         (opponent_health <= opponent_health // 2 and
                          (opponent_pokemon.name in
                           ["Shuckle", "Zigzagoon", "Linoone"])))
                    ):
                        if opponent_attack:
                            opponent_move_is_special = \
                                opponent_attack.is_special
                            if ((opponent_pokemon.item == "Liechi Berry" and
                                 not opponent_move_is_special) or (
                                    opponent_pokemon.item == "Petaya Berry" and
                                    opponent_move_is_special
                            )):
                                actual_opponent_damage: int = \
                                    floor(1.5 * actual_opponent_damage)
                                opponent_pokemon.item = ""
                        if opponent_pokemon.item == "Salac Berry":
                            opponent_speed_stat: int = \
                                floor(1.5 * opponent_speed_stat)
                            player_first: bool = \
                                (player_speed_stat > opponent_speed_stat and
                                 opponent_pokemon.item != "Quick Claw")
                            opponent_pokemon.item = ""
                    if (opponent_attack and
                            opponent_attack.name in [
                                "Sky Attack", "Solarbeam"
                            ]
                    ):
                        opponent_attack_damage, opponent_attack = \
                            get_max_damage_attacker_can_do_to_defender(
                                attacker=opponent_pokemon,
                                defender=player_pokemon,
                                random=opponent_random,
                                is_poisoned=opponent_turns_poisoned > -1,
                                defender_defense_multipliers=player_defense_multipliers
                            )
                        opponent_pokemon.item = ""

                opponent_health: int = opponent_health - actual_player_damage

                # Handle charge moves from the opponent
                # Player does not use charge moves
                opponent_attacked = False
                if opponent_must_charge:
                    opponent_must_charge = False
                else:
                    player_health: int = player_health - actual_opponent_damage
                    opponent_attacked = True

                if ((opponent_attack.name in charge_moves and
                        opponent_attacked) or opponent_pokemon.name == "Slaking"
                ):
                    opponent_must_charge = True

                # Focus Sash
                if is_first_turn:
                    if (player_pokemon.item == "Focus Sash" and
                            opponent_attack_damage > player_max_health and
                            player_health == player_max_health
                    ):
                        player_health: int = 1
                    if (opponent_pokemon.item == "Focus Sash" and
                            player_attack_damage > opponent_max_health and
                            opponent_health == opponent_max_health
                    ):
                        opponent_health: int = 1

                # TODO Metronome is a hack since is boost power, not damage
                if player_pokemon.item == "Metronome":
                    actual_player_damage: int = \
                        floor(1.1 * actual_player_damage)
                if opponent_pokemon.item == "Metronome":
                    actual_opponent_damage: int = \
                        floor(1.1 * actual_opponent_damage)

                # Toxic Orb
                if (player_pokemon.item == "Toxic Orb" and
                        PokemonType.POISON not in player_pokemon.types
                ):
                    player_turns_poisoned += 1

                if (opponent_pokemon.item == "Toxic Orb" and
                        PokemonType.POISON not in opponent_pokemon.types
                ):
                    opponent_turns_poisoned += 1

                player_health_gained: int = get_health_gained(
                    attacking_pokemon=player_pokemon,
                    move="" if player_attack is None else player_attack.name,
                    attack_damage=player_attack_damage,
                    was_first=player_first,
                    max_health=player_max_health,
                    current_health=player_health,
                    hold_item=player_pokemon.item,
                    is_player=True,
                    player_turns_badly_poisoned=player_turns_poisoned
                )
                player_health += player_health_gained
                if player_health > player_max_health:
                    player_health = player_max_health
                opponent_health_gained: int = get_health_gained(
                    attacking_pokemon=opponent_pokemon,
                    move="" if not opponent_attack else opponent_attack.name,
                    attack_damage=opponent_attack_damage,
                    max_health=opponent_max_health,
                    was_first=not player_first,
                    current_health=opponent_health,
                    hold_item=opponent_pokemon.item,
                    is_player=False,
                    player_turns_badly_poisoned=player_turns_poisoned
                )
                opponent_health += opponent_health_gained
                if opponent_health > opponent_max_health:
                    opponent_health = opponent_max_health
                # End the battle if no progress is being made
                if ((actual_opponent_damage <= player_health_gained and
                     actual_player_damage <= opponent_health_gained) or
                        player_attack is None
                ):
                    player_health = 0
                elif opponent_attack is None:
                    opponent_health = 0

                # The Iron Ball needs to be cleared since fling was used
                if (player_attack and player_pokemon.item == "Iron Ball" and
                        player_attack.name == "Fling"
                ):
                    player_pokemon.item = ""
                    player_attack_damage, player_attack = \
                        get_max_damage_attacker_can_do_to_defender(
                            attacker=player_pokemon,
                            defender=opponent_pokemon,
                            random=player_random,
                            is_poisoned=player_turns_poisoned > -1,
                            defender_defense_multipliers=opponent_defense_multipliers
                        )
                if (
                        opponent_attack and opponent_pokemon.item == "Iron Ball" and
                        opponent_attack.name == "Fling"):
                    opponent_pokemon.item = ""
                    opponent_attack_damage, opponent_attack = \
                        get_max_damage_attacker_can_do_to_defender(
                            attacker=opponent_pokemon,
                            defender=player_pokemon,
                            random=opponent_random,
                            is_poisoned=opponent_turns_poisoned > -1,
                            defender_defense_multipliers=player_defense_multipliers
                        )
                is_first_turn = False
        # No one could do damage; player loss by default
        elif opponent_attack is None and player_attack is not None:
            opponent_health = 0
        else:
            player_health: int = 0
        if player_health > 0 or \
                (
                        player_health <= 0 and
                        opponent_health <= 0 and
                        player_first
                ):
            if player_attack not in win_results:
                win_results[player_attack] = {}
            win_results[player_attack][opponent_pokemon] = (
                BattleResult(
                    hits=hits
                ))
        else:
            if player_attack not in lose_results:
                lose_results[player_attack] = {}
            lose_results[player_attack][opponent_pokemon] = (
                BattleResult(
                    hits=hits
                ))
        opponent_pokemon.item = opponent_item_backup
    return lose_results, win_results

if __name__ == '__main__':
    g_winners: dict[
        str, BattleResults] = get_pokemon_to_pokemon_they_can_beat()
    coverage: dict[str, set[CustomPokemon]] = {
        name: {
            opponent for pokemon_sets in result.win_results.values()
            for opponent in pokemon_sets.keys()
        }
        for name, result in g_winners.items()
    }

    # set 1
    # 250

    # Set 2
    # 131 for min
    # 131

    # Set 3
    # 180 for min
    # 199

    # Set 3
    # 134 for min
    # 163

    # Set 4
    # 156 for min
    # 196

    # Set 5
    # 95 if using min stats
    # 118 if using max stats

    # Set 6
    # 397 for min stats
    # 536 if using max stats

    # Set 7
    # 376 if using min stats
    # 504 if using max stats

    # All sets
    # 749 for min stats

    best_coverage_count = 131

    # triples_to_check = [
    #     ('Snorlax', 'Starmie', 'Aerodactyl'),
    #     ('Snorlax', 'Azelf', 'Aerodactyl'),
    #     ('Azelf', 'Heatran', 'Ninjask'),
    #     ('Azelf', 'Aerodactyl', 'Gallade'),
    #     ('Azelf', 'Rhydon', 'Ninjask')
    # ]

    for triple in combinations(coverage.keys(), 3):
        # if not triple in triples_to_check:
        #     continue

        combined = \
            coverage[triple[0]] | coverage[triple[1]] | coverage[triple[2]]
        if len(combined) >= best_coverage_count:
            missing = frontier_pokemon - combined
            print(f"\nTriple: {triple}")
            print(f"Cannot beat {len(missing)}: {[m.name for m in missing]}")

            for name in triple:
                print(f"\n{name}'s best moves:")
                for move, defeated in g_winners[name].win_results.items():
                    print(f"  {move.name} - {len(defeated)}")
