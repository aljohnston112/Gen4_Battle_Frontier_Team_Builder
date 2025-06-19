from math import floor

from Config import LEVEL
from data_class.Category import Category
from data_class.CustomPokemon import CustomPokemon, CustomMove
from data_class.Move import Move
from data_class.PokemonType import PokemonType
from data_class.SerebiiPokemon import SerebiiPokemon, get_all_moves
from data_class.Stats import Stats
from data_source.TypeChartDataSource import get_defense_multipliers_for_types

# TODO Focus Band, King's Rock, Lansat Berry, Lax Incense, Light Clay,
#  Lucky Punch, Mental Herb, Razor Claw, Razor Fang, Scope Lens, Stick
#  are not implemented; not sure if there are good ways to implement
IMPLEMENTED_ITEMS: set[str] = {
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
}

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

charge_moves = {"Giga Impact", "Hyper Beam", "Rock Wrecker"}

bad_moves = {
    "Selfdestruct", "Gyro Ball", "Rock Slide", "Stone Edge", "Trump Card",
    "Outrage", "Iron Tail", "Focus Blast", "Dream Eater", "Spit Up",
    "Frustration", "Thunder", "Hydro Pump", "Blizzard", "Explosion",
    "Flail", "Reversal", "Solarbeam", "Hyper Beam", "Punishment",
    "Seismic Toss", "Dive",
    "Giga Impact", "Last Resort", "Focus Punch", "Fling", "Snore",
    "Grass Knot", "Magnitude", "Low Kick", "Dig", "Hidden Power", "Petal Dance"
}

player_random: float = 1.0
opponent_random: float = 1.0


class PokemonState:

    def __init__(
            self,
            is_player: bool,
            pokemon: CustomPokemon
    ):
        self.metronome = 0
        self.move = None
        self.move_damage = 0.0
        self.current_health = pokemon.hp
        self.must_rest = False
        self.turns_badly_poisoned = 0
        self.has_item = True
        self.attack_stat_multiplier = 1.0
        self.special_attack_stat_multiplier = 1.0
        self.speed_stat_multiplier = 1.0

        self.item = pokemon.item
        self.is_player = is_player
        self.pokemon = pokemon
        self.defense_multipliers = \
            get_defense_multipliers_for_types(frozenset(pokemon.types))
        self.max_health = pokemon.hp
        if self.pokemon.item not in IMPLEMENTED_ITEMS:
            raise Exception(f"Item {self.pokemon.item} not implemented")

    def get_speed(self) -> int:
        speed: int = self.pokemon.speed
        if self.has_item and self.get_item() == "Choice Scarf":
            speed = floor(1.5 * speed)
        return floor(speed * self.speed_stat_multiplier)

    def get_item(self):
        return self.pokemon.item if self.has_item else ""

    def find_best_attack_against_defender(
            self,
            defender,
    ):
        if self.must_rest:
            self.must_rest = False
            self.move_damage = 0.0
            self.move = None
        else:
            self.move_damage, self.move = \
                get_max_damage_attacker_can_do_to_defender(
                    attacker=self,
                    defender=defender,
                    random=self.get_random_factor(),
                    is_poisoned=self.turns_badly_poisoned > 0,
                    defender_defense_multipliers=defender.defense_multipliers,
                    is_player=self.is_player
                )
            self.move_damage = apply_damage_modifiers(
                defender=defender,
                attacker_move=self.move,
                damage_taken=self.move_damage,
            )
            self.check_if_rest_needed()

    def check_if_rest_needed(self):
        if ((self.move and self.move.name in charge_moves) or
                self.pokemon.name == "Slaking"
        ):
            self.must_rest = True

    def reset(self):
        self.metronome = 0
        self.move = None
        self.move_damage = 0.0
        self.current_health = self.pokemon.hp
        self.must_rest = False
        self.turns_badly_poisoned = 0
        self.has_item = True
        self.attack_stat_multiplier = 1.0
        self.special_attack_stat_multiplier = 1.0
        self.speed_stat_multiplier = 1.0

    def check_post_attack_items(self, opponent):
        self.check_power_herb(opponent)
        self.check_stat_berries(opponent)
        self.check_toxic_orb()
        self.check_iron_ball(opponent)
        self.check_metronome()

    def check_power_herb(self, opponent):
        if (self.move and
                self.move.name in {"Sky Attack", "Solarbeam"} and
                self.get_item() == "Power Herb"
        ):
            self.has_item = False
            self.find_best_attack_against_defender(opponent)

    def check_stat_berries(self, opponent):
        has_gluttony = self.pokemon.name in {"Shuckle", "Zigzagoon", "Linoone"}
        if ((self.current_health <= self.max_health // 4) or
                (has_gluttony and
                 self.current_health <= self.max_health // 2)
        ):
            used_berry = False
            if self.get_item() == "Liechi Berry":
                self.attack_stat_multiplier *= 1.5
                used_berry = True
            elif self.get_item() == "Petaya Berry":
                self.special_attack_stat_multiplier *= 1.5
                used_berry = True
            elif self.get_item() == "Salac Berry":
                self.speed_stat_multiplier *= 1.5
                used_berry = True
            if used_berry:
                self.has_item = False
                self.find_best_attack_against_defender(opponent)

    def check_toxic_orb(self):
        if (self.get_item() == "Toxic Orb" and
                PokemonType.POISON not in self.pokemon.types
        ):
            self.turns_badly_poisoned += 1

    def check_iron_ball(self, opponent):
        # The Iron Ball needs to be cleared since fling was used
        if (self.move and self.has_item and
                self.get_item() == "Iron Ball" and
                self.move.name == "Fling"
        ):
            self.has_item = False
            self.find_best_attack_against_defender(opponent)

    def check_metronome(self):
        if self.get_item() == "Metronome":
            self.metronome += 1

    def get_random_factor(self):
        return player_random if self.is_player else opponent_random


def apply_damage_modifiers(
        defender: PokemonState,
        attacker_move: CustomMove | None,
        damage_taken: int
) -> int:
    if attacker_move is None or not defender.has_item:
        return damage_taken

    type_multiplier: float = \
        defender.defense_multipliers.get(attacker_move.move_type, 1.0)
    resist_berry: str = __berry_resistances__.get(attacker_move.move_type)
    if (type_multiplier >= 2.0) and (defender.has_item == resist_berry):
        damage_taken = damage_taken // 2
        defender.has_item = False
    return damage_taken


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


def get_max_damage_attacker_can_do_to_defender(
        attacker: PokemonState,
        defender: PokemonState,
        random: float,
        is_poisoned: bool,
        defender_defense_multipliers:
        dict[PokemonType, float],
        is_player: bool
) -> tuple[int, CustomMove | None]:
    power_multiplier: float = 1 + floor(attacker.metronome * 1.1)
    attack_stat_multiplier: float = attacker.attack_stat_multiplier
    special_attack_stat_multiplier: float = \
        attacker.special_attack_stat_multiplier

    move: CustomMove | None = None
    max_damage: int = 0

    charge_move: Move | None = None
    charge_move_damage: int = 0

    attack_stat: int = floor(attacker.pokemon.attack * attack_stat_multiplier)
    attacker_item = attacker.get_item()
    if attacker_item not in IMPLEMENTED_ITEMS:
        raise Exception(f"Item {attacker_item} not implemented")
    if attacker_item == "Choice Band":
        attack_stat: int = floor(1.5 * attack_stat)
    elif (attacker_item == "Thick Club" and
          attacker.pokemon.name in {"Cubone", "Marowak"}):
        attack_stat: int = floor(2 * attack_stat)
    special_attack_stat: int = \
        floor(attacker.pokemon.special_attack * special_attack_stat_multiplier)
    if attacker_item == "Choice Specs":
        special_attack_stat: int = floor(1.5 * special_attack_stat)
    defense_stat: int = defender.pokemon.defense
    special_defense_stat: int = defender.pokemon.special_defense
    defender_item = defender.get_item()
    if defender.pokemon.name == "Clamperl" and defender_item == "DeepSeaScale":
        special_defense_stat = floor(2 * special_defense_stat)
    for pokemon_move in attacker.pokemon.moves:
        if not pokemon_move:
            continue
        pokemon_move: CustomMove
        if is_player and pokemon_move.name in bad_moves:
            continue
        if (pokemon_move.name in ["Sky Attack", "Solarbeam"] and
                (attacker_item != "Power Herb")
        ):
            continue
        power: int = pokemon_move.power
        power = floor(power * power_multiplier)
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
            is_stab: bool = pokemon_move_type in attacker.pokemon.types
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

        for move in get_all_moves(pokemon):
            move: Move
            if move.name in bad_moves or move.accuracy != 100:
                continue

            if move.power == 0:
                continue

            move_type: PokemonType = move.move_type
            multiplier: float = o_type_multipliers[move_type]
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


def convert_to_custom_move(move: Move) -> CustomMove:
    return CustomMove(
        name=move.name,
        power=move.power,
        move_type=move.move_type,
        is_special=move.category == Category.SPECIAL,
    )
