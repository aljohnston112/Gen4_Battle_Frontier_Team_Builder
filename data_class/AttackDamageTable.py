from attr import frozen

from data_class.PokemonType import PokemonType


@frozen
class AttackDamageTable:
    attack_name: str
    category: str
    move_type: str
    defense_to_damage: dict[int, float]


@frozen
class AttackDamageTables:
    pokemon: str
    pokemon_types: list[PokemonType]
    hp: int
    speed: int
    defense: int
    special_defense: int
    attack_damage_tables: list[AttackDamageTable]
