from math import floor

from attr import dataclass

from Config import LEVEL
from data_class.BaseStats import BaseStats
from data_class.Category import Category
from data_class.FrontierPokemon import FrontierPokemon
from data_class.Move import Move
from data_class.Nature import get_nature_multiplier, get_nature_enum, NatureEnum
from data_class.PokemonType import PokemonType
from data_class.SerebiiPokemon import SerebiiPokemon
from data_class.Stat import StatEnum, calculate_health_stat, \
    calculate_non_health_stat
from data_class.Stats import Stats
from data_source.PokemonIndexDataSource import get_pokemon_name_to_index
from data_source.PokemonTypeDataSource import get_pokemon_to_types_map
from data_source.TypeChartDataSource import get_defense_multipliers_for_types


@dataclass(frozen=True)
class CustomMove:
    name: str
    power: int
    move_type: PokemonType
    is_special: bool

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return (
                isinstance(other, CustomMove)
                and self.name == other.name
        )


@dataclass(hash=False)
class CustomPokemon:
    name: str
    hp: int
    attack: int
    special_attack: int
    defense: int
    special_defense: int
    speed: int
    types: list[PokemonType]
    moves: list[CustomMove]
    item: str

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


def get_base_stat(base_stats: BaseStats, stat_enum: StatEnum) -> int:
    stats = base_stats.stats
    if stat_enum == StatEnum.HEALTH:
        return stats.health
    elif stat_enum == StatEnum.ATTACK:
        return stats.attack
    elif stat_enum == StatEnum.DEFENSE:
        return stats.defense
    elif stat_enum == StatEnum.SPECIAL_ATTACK:
        return stats.special_attack
    elif stat_enum == StatEnum.SPECIAL_DEFENSE:
        return stats.special_defense
    elif stat_enum == StatEnum.SPEED:
        return stats.speed
    else:
        raise ValueError(" Bad stat enum: " + stat_enum.name)


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


def calculate_gen4_damage(
        power: int,
        attack: int,
        defense: int,
        is_stab: bool,
        type_multiplier: float,
        random: float
) -> int:
    stab: float = 1.5 if is_stab else 1.0
    step1: int = floor(2 * LEVEL / 5) + 2
    step2: int = floor(step1 * power * attack / defense)
    step3: int = floor(step2 / 50) + 2
    damage: int = floor(
        floor(
            floor(
                step3 * random
            ) * stab
        ) * type_multiplier
    )
    return damage


charge_moves = ["Giga Impact", "Hyper Beam", "Rock Wrecker"]

# TODO Focus Band, King's Rock, Lansat Berry, Lax Incense, Light Clay,
#  Lucky Punch, Mental Herb, Razor Claw, Razor Fang, Scope Lens, Stick
#  are not implemented; not sure if there are good ways to implement
IMPLEMENTED_ITEMS: list[str] = [
    "", "Aspear Berry", "Big Root", "Black Belt", "Black Sludge",
    "BlackGlasses", "BrightPowder", "Charcoal", "Charti Berry", "Cheri Berry",
    "Chesto Berry", "Choice Band", "Choice Scarf", "Choice Specs",
    "Chople Berry", "Coba Berry", "Colbur Berry", "Damp Rock", "DeepSeaScale",
    "Dragon Fang", "Expert Belt", "Focus Band", "Focus Sash", "Grip Claw",
    "Haban Berry", "Hard Stone", "Heat Rock", "Icy Rock", "Iron Ball",
    "Kasib Berry", "King's Rock", "Lansat Berry", "Lax Incense", "Leftovers",
    "Liechi Berry", "Life Orb", "Light Clay", "Lum Berry", "Lucky Punch",
    "Magnet", "Mental Herb", "Metal Coat", "Metronome", "Miracle Seed",
    "Muscle Band", "Mystic Water", "NeverMeltIce", "Occa Berry", "Odd Incense",
    "Passho Berry", "Payapa Berry", "Pecha Berry", "Persim Berry",
    "Petaya Berry", "Poison Barb", "Power Herb", "Quick Claw", "Rawst Berry",
    "Razor Claw", "Razor Fang", "Rindo Berry", "Rock Incense", "Rose Incense",
    "Salac Berry", "Scope Lens", "Sea Incense", "Sharp Beak", "Shell Bell",
    "Shuca Berry", "Silk Scarf", "SilverPowder", "Sitrus Berry", "Soft Sand",
    "Spell Tag", "Stick", "Thick Club", "Toxic Orb", "Twisted Spoon",
    "Wacan Berry", "Wave Incense", "Wide Lens", "Wise Glasses",
    "White Herb", "Yache Berry", "Zoom Lens"
]

__boosting_items__: dict[str, PokemonType] = {
    "Black Belt": PokemonType.FIGHTING,
    "BlackGlasses": PokemonType.DARK,
    "Charcoal": PokemonType.FIRE,
    "Dragon Fang": PokemonType.DRAGON,
    "Hard Stone": PokemonType.ROCK,
    "Rock Incense": PokemonType.ROCK,
    "Magnet": PokemonType.ELECTRIC,
    "Metal Coat": PokemonType.STEEL,
    "Miracle Seed": PokemonType.GRASS,
    "Rose Incense": PokemonType.GRASS,
    "Mystic Water": PokemonType.WATER,
    "Sea Incense": PokemonType.WATER,
    "Wave Incense": PokemonType.WATER,
    "NeverMeltIce": PokemonType.ICE,
    "Odd Incense": PokemonType.PSYCHIC,
    "Twisted Spoon": PokemonType.PSYCHIC,
    "Poison Barb": PokemonType.POISON,
    "Sharp Beak": PokemonType.FLYING,
    "Silk Scarf": PokemonType.NORMAL,
    "SilverPowder": PokemonType.BUG,
    "Soft Sand": PokemonType.GROUND,
    "Spell Tag": PokemonType.GHOST,
}

type_map: dict[str, list[PokemonType]] = get_pokemon_to_types_map()


def get_max_damage_attacker_can_do_to_defender(
        attacker: CustomPokemon,
        defender: CustomPokemon,
        random: float,
        is_poisoned: bool,
        defender_defense_multipliers: dict[PokemonType, float]
) -> tuple[int, CustomMove | None]:
    move: CustomMove | None = None
    max_damage: int = 0

    charge_move: Move | None = None
    charge_move_damage: int = 0

    attack_stat: int = attacker.attack
    attacker_item = attacker.item
    if attacker_item not in IMPLEMENTED_ITEMS:
        raise Exception(f"Item {attacker_item} not implemented")
    if attacker_item == "Choice Band":
        attack_stat: int = floor(1.5 * attack_stat)
    elif (attacker_item == "Thick Club" and
          attacker.name in ["Cubone", "Marowak"]):
        attack_stat: int = floor(2 * attack_stat)
    special_attack_stat: int = attacker.special_attack
    if attacker_item == "Choice Specs":
        special_attack_stat: int = floor(1.5 * special_attack_stat)
    defense_stat: int = defender.defense
    special_defense_stat: int = defender.special_defense
    defender_item = defender.item
    if defender_item not in IMPLEMENTED_ITEMS:
        raise Exception(f"Item {defender_item} not implemented")
    if defender.name == "Clamperl" and defender_item == "DeepSeaScale":
        special_defense_stat = floor(2 * special_defense_stat)
    for pokemon_move in attacker.moves:
        pokemon_move: CustomMove
        if (pokemon_move.name in ["Sky Attack", "Solarbeam"] and
                (attacker_item != "Power Herb")
        ):
            continue
        power: int = pokemon_move.power
        if attacker_item == "Iron Ball" and pokemon_move.name == "Fling":
            power: int = 130
        if power == 0:
            damage: int = 0
        else:
            is_special: bool = pokemon_move.is_special
            attack_stat_used: int = \
                special_attack_stat if is_special else attack_stat
            defense_stat_used: int = \
                special_defense_stat if is_special else defense_stat
            pokemon_move_type = pokemon_move.move_type
            is_stab: bool = pokemon_move_type in attacker.types
            type_multiplier: float = \
                defender_defense_multipliers.get(pokemon_move_type, 1.0)
            if is_poisoned and pokemon_move.name == "Facade":
                power: int = floor(2 * power)
            if (attacker_item in __boosting_items__ and
                    pokemon_move_type == __boosting_items__[attacker_item]
            ):
                power: int = floor(1.2 * power)
            if ((not is_special and attacker_item == "Muscle Band") or
                    (is_special and attacker_item == "Wise Glasses")
            ):
                power: int = floor(1.1 * power)
            damage: int = calculate_gen4_damage(
                power=power,
                attack=attack_stat_used,
                defense=defense_stat_used,
                is_stab=is_stab,
                type_multiplier=type_multiplier,
                random=random
            )

            if type_multiplier >= 2.0 and attacker_item == "Expert Belt":
                damage: int = floor(1.2 * damage)
            if attacker_item == "Life Orb":
                damage: int = floor(1.3 * damage)
        if pokemon_move.name in charge_moves:
            if damage > charge_move_damage:
                charge_move: CustomMove = pokemon_move
            charge_move_damage: int = max(damage, charge_move_damage)
        else:
            if damage > max_damage:
                move: CustomMove = pokemon_move
            max_damage: int = max(damage, max_damage)
    if charge_move is not None and charge_move_damage > max_damage * 2:
        return charge_move_damage, charge_move
    return max_damage, move


def convert_to_custom_move(move: Move) -> CustomMove:
    return CustomMove(
        name=move.name,
        power=move.power,
        move_type=move.move_type,
        is_special=move.category == Category.SPECIAL,
    )


def get_all_attacks(pokemon: SerebiiPokemon) -> list[Move]:
    attacks = []

    for attack_level, attack_list in pokemon.level_to_attacks.items():
        if attack_level <= LEVEL:
            attacks.extend(attack_list)

    if pokemon.tm_or_hm_to_attack is not None:
        attacks.extend(pokemon.tm_or_hm_to_attack.values())

    if pokemon.egg_moves is not None:
        attacks.extend(pokemon.egg_moves)

    if pokemon.pre_evolution_index_to_level_to_moves is not None:
        for level_to_moves in pokemon.pre_evolution_index_to_level_to_moves.values():
            for attack_level, moves in level_to_moves.items():
                if attack_level <= LEVEL:
                    attacks.extend(moves)

    if pokemon.move_tutor_attacks is not None:
        attacks.extend(pokemon.move_tutor_attacks)

    if pokemon.game_to_level_to_moves is not None:
        for level_to_moves in pokemon.game_to_level_to_moves.values():
            for attack_level, move_list in level_to_moves.items():
                if attack_level <= LEVEL:
                    attacks.extend(move_list)

    if pokemon.special_moves is not None:
        attacks.extend(pokemon.special_moves)

    if pokemon.form_to_level_up_attacks is not None:
        for level_to_attacks in pokemon.form_to_level_up_attacks.values():
            for attack_level, attack_list in level_to_attacks.items():
                if attack_level <= LEVEL:
                    attacks.extend(attack_list)

    if pokemon.form_to_tm_or_hm_to_attack is not None:
        for moves_list in pokemon.form_to_tm_or_hm_to_attack.values():
            attacks.extend(moves_list.values())

    if pokemon.form_to_move_tutor_attacks is not None:
        for moves_list in pokemon.form_to_move_tutor_attacks.values():
            attacks.extend(moves_list)

    return attacks


bad_moves = {
    "Selfdestruct", "Gyro Ball", "Rock Slide", "Stone Edge",
    "Outrage", "Iron Tail", "Focus Blast", "Dream Eater", "Spit Up",
    "Frustration", "Thunder", "Hydro Pump", "Blizzard", "Explosion",
    "Flail", "Reversal", "Solarbeam", "Hyper Beam",
    "Giga Impact", "Last Resort", "Focus Punch", "Fling", "Snore",
    "Grass Knot", "Magnitude", "Low Kick", "Dig", "Hidden Power", "Petal Dance"
}


def find_best_attack_against_target(
        all_pokemon: dict,
        opponent: CustomPokemon
) -> dict[str, tuple[CustomMove, float]]:
    from math import inf

    o_hp: int = opponent.hp
    o_defense: int = opponent.defense
    o_special_defense: int = opponent.special_defense
    o_types: frozenset[PokemonType] = frozenset(opponent.types)
    o_type_multipliers: dict[PokemonType, float] = \
        get_defense_multipliers_for_types(o_types)

    results: dict[str, tuple[CustomMove, float]] = {}
    for pokemon in all_pokemon.values():
        pokemon: SerebiiPokemon
        min_stats: Stats = pokemon.all_stats.level_50_min_stats
        attack: int = min_stats.attack
        special_attack: int = min_stats.special_attack

        best_hits: float = inf
        best_move: CustomMove | None = None

        pokemon_types: list[PokemonType] = \
            pokemon.pokemon_information.pokemon_types

        for move in get_all_attacks(pokemon):
            move: Move
            if move.name in bad_moves or move.accuracy != 100:
                continue

            if move.power == 0:
                continue

            move_type: PokemonType = move.move_type
            multiplier: float = \
                o_type_multipliers[move_type]
            power: int = move.power
            is_special: bool = move.category.name == "special"
            attack_stat: int = special_attack if is_special else attack
            defense_stat: int = o_special_defense if is_special else o_defense
            is_stab: bool = move_type in pokemon_types

            damage: int = calculate_gen4_damage(
                power=power,
                attack=attack_stat,
                defense=defense_stat,
                is_stab=is_stab,
                type_multiplier=multiplier,
                random=0.85
            )
            hits: float = o_hp / damage if damage > 0 else inf

            if hits < best_hits:
                best_hits: float = hits
                best_move: CustomMove = convert_to_custom_move(move)

        if best_move:
            results[pokemon.pokemon_information.name] = (best_move, best_hits)

    return dict(sorted(results.items(), key=lambda x: x[1][1]))
