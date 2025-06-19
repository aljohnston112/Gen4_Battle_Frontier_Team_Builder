from dataclasses import dataclass
from itertools import combinations
from math import floor

from data_class.BaseStats import BaseStats
from data_class.CustomPokemon import CustomMove, CustomPokemon
from data_class.FrontierPokemon import convert_frontier_to_custom
from data_class.PokemonState import PokemonState, bad_moves, \
    convert_to_custom_move
from data_class.PokemonType import PokemonType
from data_class.SerebiiPokemon import SerebiiPokemon, get_all_moves, \
    get_stat_for_serebii_pokemon
from data_class.Stat import StatEnum
from data_source.FrontierPokemonDataSource import get_all_frontier_pokemon
from data_source.PokemonDataSource import get_legal_serebii_pokemon
from data_source.PokemonIndexDataSource import FULLY_EVOLVED_OBTAINABLE_POKEMON
from data_source.PokemonTypeDataSource import get_pokemon_to_types_map


@dataclass
class BattleResults:
    name: str
    win_results: dict[CustomMove, list[CustomPokemon]]
    loss_results: dict[CustomMove, list[CustomPokemon]]


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
        for move in get_all_moves(player_pokemon)
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
        special_attack=get_stat_for_serebii_pokemon(
            stats,
            special_attack_ev,
            StatEnum.SPECIAL_ATTACK
        ),
        defense=get_stat_for_serebii_pokemon(
            stats,
            defense_ev,
            StatEnum.DEFENSE
        ),
        special_defense=get_stat_for_serebii_pokemon(
            stats,
            special_defense_ev,
            StatEnum.SPECIAL_DEFENSE
        ),
        speed=get_stat_for_serebii_pokemon(stats, speed_ev, StatEnum.SPEED),
        item=item
    )


def heal(attacker_state, amount):
    attacker_state.current_health = min(
        attacker_state.current_health + amount,
        attacker_state.pokemon.hp
    )


def check_sitrus_berry(attacker_state):
    if not attacker_state.has_item:
        return
    hold_item: str = attacker_state.pokemon.item
    max_health: int = attacker_state.pokemon.hp
    if (
            hold_item == "Sitrus Berry" and
            attacker_state.current_health < max_health // 2
    ):
        heal(attacker_state, max_health // 4)
        attacker_state.has_item = False


def apply_health_changes(
        attacker_state: PokemonState,
        opponent_state: PokemonState,
        was_first: bool,
):
    if attacker_state.current_health <= 0:
        return

    player_used_sash = check_focus_sash(
        defender_state=attacker_state,
        attacker_state=opponent_state
    )

    attacker_move: str = attacker_state.move.name if attacker_state.move else None
    attack_damage: float = opponent_state.move_damage

    if not was_first:
        if player_used_sash:
            attacker_state.current_health = 1
        elif attack_damage >= attacker_state.current_health:
            attacker_state.current_health = 0
            return
        attacker_state.current_health -= attack_damage

    check_sitrus_berry(attacker_state)

    # Check recoil
    recoil: int = 0
    max_health: int = attacker_state.pokemon.hp
    hold_item: str = attacker_state.pokemon.item \
        if attacker_state.has_item else ""
    if attacker_move in {
        "Brave Bird", "Double-Edge", "Flare Blitz", "Volt Tackle", "Wood Hammer"
    }:
        recoil = floor(attack_damage / 3)
    elif attacker_move == "Head Smash":
        recoil = floor(attack_damage / 2)
    elif attacker_move in {"Submission", "Take Down"}:
        recoil = floor(attack_damage / 4)
    elif attacker_move in {"Explosion", "Selfdestruct"}:
        attacker_state.current_health = 0
        return
    if hold_item == "Life Orb":
        recoil = max_health // 10
    if recoil >= attacker_state.current_health:
        attacker_state.current_health = 0
        return
    attacker_state.current_health -= recoil

    check_sitrus_berry(attacker_state)

    if hold_item == "Shell Bell":
        heal(attacker_state, attack_damage // 8)

    # Draining moves and Big Root
    if attacker_move in {"Drain Punch", "Giga Drain", "Mega Drain"}:
        if hold_item == "Big Root":
            heal(attacker_state, floor((attack_damage * 1.3) // 2))
        else:
            heal(attacker_state, attack_damage // 2)

    if was_first:
        if player_used_sash:
            attacker_state.current_health = 1
        elif attack_damage >= attacker_state.current_health:
            attacker_state.current_health = 0
            return
        attacker_state.current_health -= attack_damage

    check_sitrus_berry(attacker_state)

    # Toxic damage
    has_magic_guard: bool = attacker_state.pokemon.name in {
        "Clefairy", "Clefable", "Kadabra", "Alakazam"
    }
    turns_badly_poisoned: int = attacker_state.turns_badly_poisoned
    if not has_magic_guard and turns_badly_poisoned > 0:
        poison_damage = turns_badly_poisoned * (max_health // 16)
        attacker_state.turns_badly_poisoned += 1
        if poison_damage >= attacker_state.current_health:
            attacker_state.current_health = 0
            return
        attacker_state.current_health -= poison_damage

    check_sitrus_berry(attacker_state)

    if hold_item == "Black Sludge":
        if not has_magic_guard:
            is_poison: bool = PokemonType.POISON in attacker_state.pokemon.types
            if is_poison:
                heal(attacker_state, max_health // 16)
            else:
                poison_damage = max_health // 8
                if poison_damage >= attacker_state.current_health:
                    attacker_state.current_health = 0
                    return
                attacker_state.current_health -= poison_damage
    elif hold_item == "Leftovers":
        heal(attacker_state, max_health // 16)


type_map: dict[str, list[PokemonType]] = get_pokemon_to_types_map()

pokemon_map: dict[int, SerebiiPokemon] = {
    k: v for k, v in get_legal_serebii_pokemon().items()
}

frontier_pokemon: set[CustomPokemon] = set([
    # max IVs
    convert_frontier_to_custom(pokemon_map, 100, p)
    for p in get_all_frontier_pokemon()
    # if 7 in p.set_numbers
])


def get_pokemon_to_pokemon_they_can_beat() -> dict[str, BattleResults]:
    winner_to_battle_results: dict[str, BattleResults] = dict()

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
        if k in FULLY_EVOLVED_OBTAINABLE_POKEMON
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
        player_pokemon: CustomPokemon
        player_state = PokemonState(
            is_player=True,
            pokemon=player_pokemon,
        )

        # Get the best 4 moves
        lose_results, win_results = perform_battle_simulation(player_state)
        # Sort by number of wins
        win_results: dict[CustomMove, list[CustomPokemon]] = \
            dict(
                sorted(
                    win_results.items(),
                    key=lambda x: len(x[1]),
                    reverse=True
                )[:4]
            )
        player_pokemon.moves = [move for move in win_results.keys()]

        # Get the battle results using the best 4 moves of each Pokémon
        lose_results, win_results = perform_battle_simulation(player_state)
        winner_to_battle_results[player_pokemon.name]: BattleResults = \
            BattleResults(
                name=player_pokemon.name,
                win_results=win_results,
                loss_results=lose_results,
            )
    winner_to_battle_results = dict(
        sorted(
            winner_to_battle_results.items(),
            key=lambda x: sum(len(v) for v in x[1].win_results.values()),
            reverse=True
        )
    )
    return winner_to_battle_results


def perform_battle_simulation(
        player_state: PokemonState
) -> tuple[
    dict[CustomMove, list[CustomPokemon]],
    dict[CustomMove, list[CustomPokemon]]
]:
    win_results: dict[CustomMove, list[CustomPokemon]] = dict()
    lose_results: dict[CustomMove, list[CustomPokemon]] = dict()

    for opponent_pokemon in frontier_pokemon:
        opponent_pokemon: CustomPokemon
        opponent_state = PokemonState(
            pokemon=opponent_pokemon,
            is_player=False,
        )

        player_first: bool = is_player_faster(
            player_state=player_state,
            opponent_state=opponent_state
        )
        player_state.find_best_attack_against_defender(defender=opponent_state)
        opponent_state.find_best_attack_against_defender(defender=player_state)

        # TODO pluck and bug bite will eat berries
        # TODO Knock off will make the holder lose their item
        #      Stats will need to be recalculated in this case
        if (
                opponent_state.move_damage == 0 and
                player_state.move_damage == 0 and
                not opponent_state.move and
                not player_state.move
        ):
            # No one could do damage; the player loses by default
            player_state.current_health = 0
        elif opponent_state.move is None and player_state.move is not None:
            # Opponent could not do damage
            opponent_state.current_health = 0
        else:
            while (player_state.current_health > 0 and
                   opponent_state.current_health > 0
            ):
                apply_health_changes_and_check_for_stall(
                    player_state=player_state,
                    opponent_state=opponent_state,
                    player_first=player_first,
                )

                player_state.check_post_attack_items(opponent_state)
                opponent_state.check_post_attack_items(player_state)
                # Speed may have changed
                player_first: bool = is_player_faster(
                    player_state=player_state,
                    opponent_state=opponent_state
                )
        if (player_state.current_health > 0 or (
                player_state.current_health <= 0 and
                opponent_state.current_health <= 0 and
                player_first)
        ):
            if player_state.move not in win_results:
                win_results[player_state.move] = []
            win_results[player_state.move].append(opponent_pokemon)
        else:
            if player_state.move not in lose_results:
                lose_results[player_state.move] = []
            lose_results[player_state.move].append(opponent_pokemon)
        player_state.reset()
    return lose_results, win_results


def check_focus_sash(
        defender_state: PokemonState,
        attacker_state: PokemonState
) -> bool:
    player_used_sash = False
    if (defender_state.get_item() == "Focus Sash" and
            attacker_state.move_damage > defender_state.max_health and
            defender_state.current_health == defender_state.max_health
    ):
        defender_state.current_health = 1
        player_used_sash = True
        defender_state.has_item = False
    return player_used_sash


def is_player_faster(opponent_state, player_state):
    return (player_state.get_speed() >
            opponent_state.get_speed() and
            opponent_state.get_item() != "Quick Claw")


def apply_health_changes_and_check_for_stall(
        player_state: PokemonState,
        opponent_state: PokemonState,
        player_first: bool,
):
    player_hp_before = player_state.current_health
    opponent_hp_before = opponent_state.current_health
    apply_health_changes(
        attacker_state=player_state,
        opponent_state=opponent_state,
        was_first=player_first,
    )
    apply_health_changes(
        attacker_state=opponent_state,
        opponent_state=player_state,
        was_first=not player_first,
    )
    # End the battle if no progress is being made
    player_health_gained = \
        player_state.current_health - player_hp_before
    opponent_health_gained = \
        opponent_state.current_health - opponent_hp_before
    if ((opponent_state.move_damage <= player_health_gained and
         player_state.move_damage <= opponent_health_gained) or
            player_state.move is None
    ):
        player_state.current_health = 0
    elif opponent_state.move is None:
        opponent_state.current_health = 0


if __name__ == '__main__':
    g_winners: dict[str, BattleResults] = get_pokemon_to_pokemon_they_can_beat()
    coverage: dict[str, set[CustomPokemon]] = {
        name: {
            opponent for pokemon_sets in result.win_results.values()
            for opponent in pokemon_sets
        }
        for name, result in g_winners.items()
    }

    # set 1
    # 250
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

    best_coverage_count = 10000

    # triples_to_check = [
    #     ('Snorlax', 'Starmie', 'Aerodactyl'),
    #     ('Snorlax', 'Azelf', 'Aerodactyl'),
    #     ('Azelf', 'Heatran', 'Ninjask'),
    #     ('Azelf', 'Aerodactyl', 'Gallade'),
    #     ('Azelf', 'Rhydon', 'Ninjask')
    # ]

    for triple in combinations(coverage.keys(), 6):
        # if not triple in triples_to_check:
        #     continue

        combined = \
            coverage[triple[0]] | coverage[triple[1]] | coverage[triple[2]] | \
            coverage[triple[3]] | coverage[triple[4]] | coverage[triple[5]]
        if len(combined) >= best_coverage_count:
            missing = frontier_pokemon - combined
            print(f"\nTriple: {triple}")
            print(f"Cannot beat {len(missing)}: {[m.name for m in missing]}")

            for name in triple:
                print(f"\n{name}'s best moves:")
                for g_move, defeated in g_winners[name].win_results.items():
                    print(f"  {g_move.name} - {len(defeated)}")
