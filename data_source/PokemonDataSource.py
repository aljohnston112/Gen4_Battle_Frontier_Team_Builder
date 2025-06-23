import json
import pprint
import random
import time
import typing
import urllib.request
from collections import defaultdict
from os.path import exists

import cattr
from attrs import frozen
from bs4 import BeautifulSoup

from Config import SEREBII_POKEMON_FILE
from data_class.Category import convert_to_attack_category
from data_class.Move import Move
from data_class.PokemonType import convert_string_to_pokemon_type, PokemonType
from data_class.SerebiiPokemon import SerebiiPokemon
from data_class.Stats import Stats


@frozen
class PokemonInformation:
    name: str
    pokemon_types: list[PokemonType]
    id: int
    ability: str
    pounds: float


__BASE_URL__: str = "https://www.serebii.net/pokedex-dp/"
__NUM_POKEMON__: int = 493


def get_url(index: int) -> str:
    return __BASE_URL__ + str(index).zfill(3) + ".shtml"


def get_general_information(dextable):
    rows = [row for row in dextable.find_all("tr")]
    assert rows[0].text == "\nName\nJp. Name\nNo.\nGender Ratio\nType\n"
    columns = rows[1].text.strip().split("\n")
    name = columns[0].strip()
    national_id = int(
        columns[2].strip().split("Johto")[0].split("Sinnoh")[0].split("#")[1]
    )
    pokemon_types = []
    type_image_links = rows[1].find_all("a")
    for type_image_link in type_image_links:
        type_name = type_image_link['href'].strip().split('/')[2].split('.')[0]
        pokemon_types.append(convert_string_to_pokemon_type(type_name))
    if (rows[5].text ==
            "\nClassification\nHeight\nWeight\nCapture Rate\nBase Egg Steps\n"
    ):
        ability_index = 3
        weight_index = 6
    elif (rows[6].text ==
          "\nClassification\nHeight\nWeight\nCapture Rate\nBase Egg Steps\n"
    ):
        ability_index = 4
        weight_index = 7
    elif (rows[7].text ==
          "\nClassification\nHeight\nWeight\nCapture Rate\nBase Egg Steps\n"
    ):
        ability_index = 6
        weight_index = 9
    elif (rows[8].text ==
          "\nClassification\nHeight\nWeight\nCapture Rate\nBase Egg Steps\n"
    ):
        ability_index = 7
        weight_index = 10
    elif (rows[9].text ==
          "\nClassification\nHeight\nWeight\nCapture Rate\nBase Egg Steps\n"
    ):
        ability_index = 7
        weight_index = 10
    else:
        assert (
                rows[11].text ==
                "\nClassification\nHeight\nWeight\nCapture Rate\nBase Egg Steps\n"
        )
        ability_index = 9
        weight_index = 12
    if "Ability" not in rows[ability_index].text:
        ability_index -= 1
        assert "Ability" in rows[ability_index].text

    ability = rows[ability_index].text.strip().split(":")[1].strip()
    if "lbs" not in rows[weight_index].text:
        weight_index -= 1
        assert "Ability" in rows[ability_index].text
    pounds = float(
        rows[weight_index].text \
            .strip() \
            .split("\n")[2] \
            .split("lbs")[0] \
            .replace(",", "")
    )
    return PokemonInformation(
        name=name,
        pokemon_types=pokemon_types,
        id=national_id,
        ability=ability,
        pounds=pounds
    )


def get_level_up_attacks(dextable):
    level_to_attacks = defaultdict(lambda: [])
    rows = [row for row in dextable.find_all("tr")]
    level_up_strings = [
        'Sky Forme Level Up',
        'Diamond/Pearl/Platinum/HeartGold/SoulSilver Level Up (All  Forms)',
        "Diamond/Pearl Level Up (Trash Cloak)",
        "Diamond/Pearl Level Up (Sandy Cloak)",
        "Diamond/Pearl Level Up (Speed Form)",
        "Diamond/Pearl Level Up (Defense Form)",
        'Diamond/Pearl Level Up (Attack Form)',
        'Diamond/Pearl/Platinum Level Up',
        'Platinum/HeartGold/SoulSilver Level Up',
        'Diamond/Pearl/Platinum/HeartGold/SoulSilver Level Up'
    ]
    assert rows[0].text in level_up_strings
    assert rows[1].text == 'LevelAttack NameTypeCat.Att.Acc.PPEffect %'
    current_index = 2
    while current_index < len(rows):
        columns = rows[current_index].find_all("td")
        level = columns[0].text
        if level == '—':
            level = 0
        level = int(level)
        name = columns[1].text
        type_images = columns[2].find_all("img")
        assert len(type_images) == 1
        pokemon_type = type_images[0]['src'] \
            .split("/")[-1] \
            .split(".")[0] \
            .strip()
        if pokemon_type == "curse":
            pokemon_type = "ghost"
        category_images = columns[3].find_all("img")
        assert len(category_images) == 1
        category = category_images[0]['src'] \
            .split("/")[-1] \
            .split(".")[0] \
            .strip()
        if category == "other":
            category = "status"
        power = columns[4].text
        if power == "--" or \
                name == "Endeavor" or \
                name == "Dragon Rage" or \
                name == "Super Fang" or \
                name == "Sonicboom" or \
                name == "Mirror Coat" or \
                name == "Counter" or \
                name == "Bide" or \
                name == "Metal Burst":
            power = -1
        elif name == "Gyro Ball" or name == "Magnitude":
            power = -1
        elif name == "Horn Drill" or \
                name == "Fissure" or \
                name == "Sheer Cold" or \
                name == "Guillotine":
            power = -1
        elif name == "Natural Gift":
            power = -1
        elif name == "Low Kick" or name == "Present":
            power = -1
        elif name == "Seismic Toss" or name == "Night Shade":
            power = -1
        elif name == "Punishment" or \
                name == "Reversal" or \
                name == "Flail" or \
                name == "Trump Card":
            power = -1
        elif name == "Fling":
            power = -1
        elif name == "Wring Out":
            power = -1
        elif name == "Frustration" or name == "Return":
            power = 102
        elif name == "Spit Up":
            power = -1
        elif name == "Hidden Power":
            power = -1
        elif name == "Psywave":
            power = -1
        elif name == "Crush Grip":
            power = -1
        power = int(power)
        accuracy = columns[5].text
        if accuracy == "--":
            accuracy = 100
        accuracy = int(accuracy)
        effect_chance = columns[7].text
        if effect_chance == "--":
            effect_chance = 0
        effect_chance = int(effect_chance)
        level_to_attacks[level].append(
            Move(
                name=name,
                move_type=convert_string_to_pokemon_type(pokemon_type),
                category=convert_to_attack_category(category),
                power=power,
                accuracy=accuracy,
                effect_percent=effect_chance
            )
        )
        current_index += 2
    return level_to_attacks


def get_tm_and_hm_attacks(dextable):
    tm_or_hm_to_attack = dict()
    rows = [row for row in dextable.find_all("tr")]
    assert rows[0].text == "TM & HM Attacks"
    assert rows[1].text == 'TM/HM #Attack NameTypeCat.Att.Acc.PPEffect %'
    current_index = 2
    while current_index < len(rows):
        columns = rows[current_index].find_all("td")
        tm_or_hm = columns[0].text.strip()
        name = columns[1].text.strip()
        type_images = columns[2].find_all("img")
        assert len(type_images) == 1
        pokemon_type = type_images[0]['src'] \
            .split("/")[-1] \
            .split(".")[0] \
            .strip()
        category_images = columns[3].find_all("img")
        assert len(category_images) == 1
        category = category_images[0]['src'] \
            .split("/")[-1] \
            .split(".")[0] \
            .strip()
        if category == "other":
            category = "status"
        power = columns[4].text
        if power == "--":
            power = 0
        elif name == "Hidden Power":
            power = -1
        elif name == "Frustration" or name == "Return":
            power = 102
        elif name == "Natural Gift":
            power = -1
        elif name == "Grass Knot":
            power = -1
        elif name == "Fling":
            power = -1
        elif name == "Gyro Ball":
            power = -1
        power = int(power)
        accuracy = columns[5].text
        if accuracy == "--":
            accuracy = 100
        accuracy = int(accuracy)
        effect_chance = columns[7].text
        if effect_chance == "--":
            effect_chance = 0
        effect_chance = int(effect_chance)
        tm_or_hm_to_attack[tm_or_hm] = Move(
            name=name,
            move_type=convert_string_to_pokemon_type(pokemon_type),
            category=convert_to_attack_category(category),
            power=power,
            accuracy=accuracy,
            effect_percent=effect_chance
        )
        current_index += 2
    return tm_or_hm_to_attack


def get_attacks(dextable):
    attacks = list()
    rows = [row for row in dextable.find_all("tr")]
    assert (
            rows[0].text ==
            "Platinum/HeartGold/SoulSilver Move Tutor Attacks" or
            rows[0].text == "Egg Moves (Details)" or
            rows[0].text == 'Move Tutor Attacks' or
            rows[0].text == "Special Moves"
    )
    assert rows[1].text.strip() == 'Attack NameTypeCat.Att.Acc.PPEffect %'
    current_index = 2
    while current_index < len(rows):
        columns = rows[current_index].find_all("td")
        name = columns[0].text.strip()
        if "HGSS Only" in name:
            return None
        type_images = columns[1].find_all("img")
        assert len(type_images) == 1
        pokemon_type = type_images[0]['src'] \
            .split("/")[-1] \
            .split(".")[0] \
            .strip()
        if pokemon_type == "curse":
            pokemon_type = "ghost"
        category_images = columns[2].find_all("img")
        assert len(category_images) == 1
        category = category_images[0]['src'] \
            .split("/")[-1] \
            .split(".")[0] \
            .strip()
        if category == "other":
            category = "status"
        power = columns[3].text
        if power == "--" or \
                name == "Belly Drum" or \
                name == "Mirror Coat" or \
                name == "Bide" or \
                name == "Counter" or \
                name == "Endeavor" or \
                name == "Dragon Rage" or \
                name == "Sonicboom":
            power = 0
        if name == "Hidden Power":
            power = -1
        elif name == "Frustration" or name == "Return":
            power = 102
        elif name == "Natural Gift":
            power = -1
        elif name == "Grass Knot" or name == "Present":
            power = -1
        elif (name == "Flail" or
              name == "Reversal" or
              name == "Punishment" or
              name == "Trump Card"
        ):
            power = -1
        elif name == "Horn Drill" or name == "Fissure" or name == "Sheer Cold":
            power = -1
        elif name == "Spit Up":
            power = -1
        elif name == "Psywave" or name == "Magnitude":
            power = -1
        elif name == "Wring Out":
            power = -1
        elif name == "Night Shade" or name == "Seismic Toss":
            power = -1
        elif name == "Low Kick":
            power = -1
        power = int(power)

        accuracy = columns[4].text
        if accuracy == "--":
            accuracy = 100
        accuracy = int(accuracy)
        effect_chance = columns[6].text
        if effect_chance == "--":
            effect_chance = 0
        effect_chance = int(effect_chance)
        attacks.append(
            Move(
                name=name,
                move_type=convert_string_to_pokemon_type(pokemon_type),
                category=convert_to_attack_category(category),
                power=power,
                accuracy=accuracy,
                effect_percent=effect_chance
            )
        )
        current_index += 2
    return attacks


def get_third_gen_moves(dextable):
    game_to_level_to_attacks = defaultdict(lambda: defaultdict(lambda: list()))
    rows = [row for row in dextable.find_all("tr")]
    assert rows[0].text == "3rd Gen Only  Moves"
    assert rows[1].text.strip() == 'Attack NameTypeCat.Att.Acc.PPEffect % Means'
    current_index = 2
    while current_index < len(rows):
        columns = rows[current_index].find_all("td")
        name = columns[0].text.strip()
        type_images = columns[1].find_all("img")
        assert len(type_images) == 1
        pokemon_type = type_images[0]['src'] \
            .split("/")[-1] \
            .split(".")[0] \
            .strip()
        category_images = columns[2].find_all("img")
        assert len(category_images) == 1
        category = category_images[0]['src'] \
            .split("/")[-1] \
            .split(".")[0] \
            .strip()
        if category == "other":
            category = "status"
        power = columns[3].text
        if power == "--":
            power = 0
        if name == "Hidden Power":
            power = -1
        elif name == "Frustration" or name == "Return":
            power = 102
        elif name == "Natural Gift":
            power = -1
        elif name == "Grass Knot":
            power = -1
        power = int(power)
        accuracy = columns[4].text
        if accuracy == "--":
            accuracy = 100
        accuracy = int(accuracy)
        effect_chance = columns[6].text
        if effect_chance == "--":
            effect_chance = 0
        effect_chance = int(effect_chance)
        if (name == "" and
                pokemon_type == "" and
                power == 0 and
                accuracy == 100 and
                effect_chance == 0
        ):
            current_index += 1
        else:
            attack = (
                Move(
                    name=name,
                    move_type=convert_string_to_pokemon_type(pokemon_type),
                    category=convert_to_attack_category(category),
                    power=power,
                    accuracy=accuracy,
                    effect_percent=effect_chance
                )
            )
            current_index += 1
            columns = rows[current_index].find_all("td")
            games = [c for c in columns[0].children if isinstance(c, str)]
            levels = [c for c in columns[1].children if isinstance(c, str)]
            assert len(games) == len(levels)
            for i in range(0, len(levels)):
                level = int(levels[i].split("Lv")[1].strip())
                game_to_level_to_attacks[games[i]][level].append(attack)
        current_index += 2
    return game_to_level_to_attacks


def get_forms_move_tutor_attacks(dextable):
    form_to_attacks = defaultdict(lambda: list())
    rows = [row for row in dextable.find_all("tr")]
    assert rows[0].text == "Platinum/HeartGold/SoulSilver Move Tutor Attacks"
    assert rows[1].text.strip() == 'Attack NameTypeCat.Att.Acc.PPEffect %Form'
    current_index = 2
    while current_index < len(rows):
        columns = rows[current_index].find_all("td")
        name = columns[0].text.strip()
        type_images = columns[1].find_all("img")
        assert len(type_images) == 1
        pokemon_type = type_images[0]['src'] \
            .split("/")[-1] \
            .split(".")[0] \
            .strip()
        category_images = columns[2].find_all("img")
        assert len(category_images) == 1
        category = category_images[0]['src'] \
            .split("/")[-1] \
            .split(".")[0] \
            .strip()
        if category == "other":
            category = "status"
        power = columns[3].text
        if power == "--" or name == "Endeavor":
            power = 0
        if name == "Hidden Power":
            power = -1
        elif name == "Frustration" or name == "Return":
            power = 102
        elif name == "Natural Gift":
            power = -1
        elif name == "Grass Knot":
            power = -1
        power = int(power)
        accuracy = columns[4].text
        if accuracy == "--":
            accuracy = 100
        accuracy = int(accuracy)
        effect_chance = columns[6].text
        if effect_chance == "--":
            effect_chance = 0
        effect_chance = int(effect_chance)
        if (name == "" and
                pokemon_type == "" and
                power == 0 and
                accuracy == 100 and
                effect_chance == 0
        ):
            current_index += 1
        else:
            attack = (
                Move(
                    name=name,
                    move_type=convert_string_to_pokemon_type(pokemon_type),
                    category=convert_to_attack_category(category),
                    power=power,
                    accuracy=accuracy,
                    effect_percent=effect_chance
                )
            )
            current_index += 1
            columns = rows[current_index].find_all("td")
            for column in columns:
                form = column.find("img")["title"]
                form_to_attacks[form].append(attack)
        current_index += 2
    return form_to_attacks


def get_stats(dextable, name):
    rows = [row for row in dextable.find_all("tr")]
    assert rows[0].text == "\nStats" or \
           rows[0].text == "\nStats - Attack Forme" or \
           rows[0].text == "\nStats - Defense Forme" or \
           rows[0].text == "\nStats - Speed Forme" or \
           rows[0].text == "\nStats - Sandy Cloak" or \
           rows[0].text == "\nStats - Trash Cloak" or \
           rows[0].text == '\nStats - Alternate Forms' or \
           rows[0].text == '\nStats - Origin Forme' or \
           rows[0].text == '\nStats - Sky Forme'
    assert (
            rows[1].text.strip() ==
            'HP\nAttack\nDefense\nSp. Attack\nSp. Defense\nSpeed'
    )
    base_stat_tokens = rows[2].text.split("\n")
    assert len(base_stat_tokens) == 7
    base_hp = int(base_stat_tokens[1])
    base_attack = int(base_stat_tokens[2])
    base_defense = int(base_stat_tokens[3])
    base_special_attack = int(base_stat_tokens[4])
    base_special_defense = int(base_stat_tokens[5])
    base_speed = int(base_stat_tokens[6])
    base_stats = Stats(
        health=base_hp,
        attack=base_attack,
        defense=base_defense,
        special_attack=base_special_attack,
        special_defense=base_special_defense,
        speed=base_speed
    )
    return base_stats


def get_pre_evolution_moves(dextable):
    pre_evolution_index_to_level_to_moves = defaultdict(
        lambda: defaultdict(lambda: list()))
    rows = [row for row in dextable.find_all("tr")]
    assert rows[0].text == 'Pre-Evolution Moves'
    assert rows[1].text.strip() == 'Attack NameTypeCat.Att.Acc.PPEffect % Means'
    current_index = 2
    while current_index < len(rows):
        columns = rows[current_index].find_all("td")
        if (columns[0].text == 'Base/Max Pokéathlon Stats' or
                columns[0].text == 'Base/Max Pok�athlon Stats'
        ):
            current_index = len(rows)
        else:
            move_name = columns[0].text.strip()
            type_images = columns[1].find_all("img")
            assert len(type_images) == 1
            pokemon_type = type_images[0]['src'].split("/")[-1].split(".")[
                0].strip()
            category_images = columns[2].find_all("img")
            assert len(category_images) == 1
            category = category_images[0]['src'] \
                .split("/")[-1] \
                .split(".")[0] \
                .strip()
            if category == 'other':
                category = "status"
            power = columns[3].text
            if (power == "--" or
                    move_name == "Endeavor" or
                    move_name == "Bide" or
                    move_name == 'Night Shade'
            ):
                power = 0
            if move_name == "Hidden Power":
                power = -1
            elif (move_name == "Frustration" or
                  move_name == "Return"

            ):
                power = 102
            elif move_name == "Wring Out":
                power = -1
            elif move_name == "Natural Gift":
                power = -1
            elif move_name == "Grass Knot":
                power = -1
            elif move_name == "Horn Drill" or move_name == "Fissure":
                power = -1
            elif move_name == "Reversal" or move_name == "Flail" or move_name == "Trump Card":
                power = -1
            power = int(power)
            accuracy = columns[4].text
            if accuracy == "--":
                accuracy = 100
            accuracy = int(accuracy)
            effect_chance = columns[6].text
            if effect_chance == "--":
                effect_chance = 0
            effect_chance = int(effect_chance)
            attack = (
                Move(
                    name=move_name,
                    move_type=convert_string_to_pokemon_type(pokemon_type),
                    category=convert_to_attack_category(category),
                    power=power,
                    accuracy=accuracy,
                    effect_percent=effect_chance
                )
            )
            current_index += 1
            columns = rows[current_index].find_all("td")
            pokemon_images = columns[0].find_all("img")
            assert len(pokemon_images) == 1
            pokemon_index = int(
                pokemon_images[0]['src'].split("/")[-1].split(".")[0])
            possible_level = columns[1].text.split(".")
            if len(possible_level) > 1:
                level = int(possible_level[1].strip())
            else:
                level = 0
            pre_evolution_index_to_level_to_moves[pokemon_index][level].append(
                attack
            )
            current_index += 2
    return pre_evolution_index_to_level_to_moves


def get_tm_and_hm_attacks_for_forms(dextable):
    form_to_tm_or_hm_to_attacks = defaultdict(lambda: dict())
    rows = [row for row in dextable.find_all("tr")]
    assert rows[0].text == "TM & HM Attacks"
    assert rows[1].text == 'TM/HM #Attack NameTypeCat.Att.Acc.PPEffect %Form'
    current_index = 2
    while current_index < len(rows):
        columns = rows[current_index].find_all("td")
        tm_or_hm = columns[0].text.strip()
        move_name = columns[1].text.strip()
        type_images = columns[2].find_all("img")
        assert len(type_images) == 1
        pokemon_type = type_images[0]['src'].split("/")[-1].split(".")[
            0].strip()
        category_images = columns[3].find_all("img")
        assert len(category_images) == 1
        category = category_images[0]['src'].split("/")[-1].split(".")[
            0].strip()
        if category == 'other':
            category = "status"
        power = columns[4].text
        if power == "--":
            power = 0
        if move_name == "Hidden Power":
            power = -1
        elif move_name == "Frustration" or move_name == "Return":
            power = 102
        elif move_name == "Natural Gift":
            power = -1
        elif move_name == "Grass Knot":
            power = -1
        elif move_name == "Gyro Ball":
            power = -1
        power = int(power)
        accuracy = columns[5].text
        if accuracy == "--":
            accuracy = 100
        accuracy = int(accuracy)
        effect_chance = columns[6].text
        if effect_chance == "--":
            effect_chance = 0
        effect_chance = int(effect_chance)
        if (move_name == "" and
                pokemon_type == "" and
                power == 0 and
                accuracy == 100 and
                effect_chance == 0
        ):
            current_index += 1
        else:
            attack = (
                Move(
                    name=move_name,
                    move_type=convert_string_to_pokemon_type(pokemon_type),
                    category=convert_to_attack_category(category),
                    power=power,
                    accuracy=accuracy,
                    effect_percent=effect_chance
                )
            )
            current_index += 1
            columns = rows[current_index].find_all("td")
            for column in columns:
                form = column.find("img")["title"]
                form_to_tm_or_hm_to_attacks[form][tm_or_hm] = attack
        current_index += 2
    return form_to_tm_or_hm_to_attacks


__first_row_text_of_skippable_table__ = [
    "\nImages\n",
    "\n\n\t\tDamage Taken\n\t\t\n",
    "\nWild Hold Item\nEgg Groups\n",
    "\nEvolutionary Chain\n",
    "\n\nFlavour Text\n\n",
    "\n\nLocation\n\n",
    "\n\nLocation(In - Depth Details)\n\n",
    "\n\nLocation (In-Depth Details)\n\n",
    "HeartGold/SoulSilver Move Tutor Attacks",
    "Base/Max Pokéathlon Stats",
    'Diamond/Pearl Level Up',
    'Base/Max Pok�athlon Stats',
    'HeartGold/SoulSilver Level Up',
    '\nAlternate Forms\n',
    'Base/Max Pokéthlon Stats',
    'Base/Max Pokéthlon Stats - (A-Z)',
    'Base/Max Pokéthlon Stats - Normal Forme',
    'Base/Max Pokéthlon Stats - Attack Forme',
    'Base/Max Pokéthlon Stats - Defense Forme',
    'Base/Max Pokéthlon Stats - Speed Forme',
    'HGSS TM & HM Attacks',
    'Base/Max Pokéthlon Stats - Plant Cloak',
    'Base/Max Pokéthlon Stats - Sandy Cloak',
    'Base/Max Pokéthlon Stats - Trash Cloak',
    'HeartGold/SoulSilver Level Up (Altered Forme & Origin Forme)',
    'Base/Max Pokéthlon Stats - Altered Forme',
    'Base/Max Pokéthlon Stats - Origin Forme',
    'Base/Max Pokéthlon Stats - Land Forme',
    'Base/Max Pokéthlon Stats - Sky Forme',
    'Base/Max Pokéthlon Stats - Normal, Fire, Ground, Rock',
    'Base/Max Pokéthlon Stats - Water, Electric, Psychic',
    'Base/Max Pokéthlon Stats - Poison, Steel',
    'Base/Max Pokéthlon Stats - Fighting, Dark',
    'Base/Max Pokéthlon Stats - Flying, Bug',
    'Base/Max Pokéthlon Stats - Grass',
    'Base/Max Pokéthlon Stats - Ice',
    'Base/Max Pokéthlon Stats - Ghost',
    'Base/Max Pokéthlon Stats - Dragon',

    'Base/Max Pokķathlon Stats',
    'Base/Max Pokķathlon Stats - (A-Z)',
    'Base/Max Pokķathlon Stats - Normal Forme',
    'Base/Max Pokķathlon Stats - Attack Forme',
    'Base/Max Pokķathlon Stats - Defense Forme',
    'Base/Max Pokķathlon Stats - Speed Forme',
    'Base/Max Pokķathlon Stats - Plant Cloak',
    'Base/Max Pokķathlon Stats - Sandy Cloak',
    'Base/Max Pokķathlon Stats - Trash Cloak',
    'Base/Max Pokķathlon Stats - Altered Forme',
    'Base/Max Pokķathlon Stats - Origin Forme',
    'Base/Max Pokķathlon Stats - Land Forme',
    'Base/Max Pokķathlon Stats - Sky Forme',
    'Base/Max Pokķathlon Stats - Normal, Fire, Ground, Rock',
    'Base/Max Pokķathlon Stats - Water, Electric, Psychic',
    'Base/Max Pokķathlon Stats - Poison, Steel',
    'Base/Max Pokķathlon Stats - Fighting, Dark',
    'Base/Max Pokķathlon Stats - Flying, Bug',
    'Base/Max Pokķathlon Stats - Grass',
    'Base/Max Pokķathlon Stats - Ice',
    'Base/Max Pokķathlon Stats - Ghost',
    'Base/Max Pokķathlon Stats - Dragon',

    'Base/Max Pokťathlon Stats',
    'Base/Max Pokťathlon Stats - (A-Z)',
    'Base/Max Pokťathlon Stats - Normal Forme',
    'Base/Max Pokťathlon Stats - Attack Forme',
    'Base/Max Pokťathlon Stats - Defense Forme',
    'Base/Max Pokťathlon Stats - Speed Forme',
    'Base/Max Pokťathlon Stats - Plant Cloak',
    'Base/Max Pokťathlon Stats - Sandy Cloak',
    'Base/Max Pokťathlon Stats - Trash Cloak',
    'Base/Max Pokťathlon Stats - Altered Forme',
    'Base/Max Pokťathlon Stats - Origin Forme',
    'Base/Max Pokťathlon Stats - Land Forme',
    'Base/Max Pokťathlon Stats - Sky Forme',
    'Base/Max Pokťathlon Stats - Normal, Fire, Ground, Rock',
    'Base/Max Pokťathlon Stats - Water, Electric, Psychic',
    'Base/Max Pokťathlon Stats - Poison, Steel',
    'Base/Max Pokťathlon Stats - Fighting, Dark',
    'Base/Max Pokťathlon Stats - Flying, Bug',
    'Base/Max Pokťathlon Stats - Grass',
    'Base/Max Pokťathlon Stats - Ice',
    'Base/Max Pokťathlon Stats - Ghost',
    'Base/Max Pokťathlon Stats - Dragon',

    'Base/Max Pokťthlon Stats - (A-Z)'
    
    'Base/Max Pokťthlon Stats',
    'Base/Max Pokťthlon Stats - (A-Z)',
    'Base/Max Pokťthlon Stats - Normal Forme',
    'Base/Max Pokťthlon Stats - Attack Forme',
    'Base/Max Pokťthlon Stats - Defense Forme',
    'Base/Max Pokťthlon Stats - Speed Forme',
    'Base/Max Pokťthlon Stats - Plant Cloak',
    'Base/Max Pokťthlon Stats - Sandy Cloak',
    'Base/Max Pokťthlon Stats - Trash Cloak',
    'Base/Max Pokťthlon Stats - Altered Forme',
    'Base/Max Pokťthlon Stats - Origin Forme',
    'Base/Max Pokťthlon Stats - Land Forme',
    'Base/Max Pokťthlon Stats - Sky Forme',
    'Base/Max Pokťthlon Stats - Normal, Fire, Ground, Rock',
    'Base/Max Pokťthlon Stats - Water, Electric, Psychic',
    'Base/Max Pokťthlon Stats - Poison, Steel',
    'Base/Max Pokťthlon Stats - Fighting, Dark',
    'Base/Max Pokťthlon Stats - Flying, Bug',
    'Base/Max Pokťthlon Stats - Grass',
    'Base/Max Pokťthlon Stats - Ice',
    'Base/Max Pokťthlon Stats - Ghost',
    'Base/Max Pokťthlon Stats - Dragon',

]
__first_row_text_for_level_up_moves__: list[str] = [
    'Diamond/Pearl/Platinum/HeartGold/SoulSilver Level Up',
    'Platinum/HeartGold/SoulSilver Level Up',
    'Diamond/Pearl/Platinum Level Up',
    'Diamond/Pearl/Platinum/HeartGold/SoulSilver Level Up (All  Forms)'
]


def __scrape_serebii_for_pokemon_data__():
    pokemon_index_to_pokemon: dict[int, SerebiiPokemon] = {}
    last_url_index_downloaded: int = 0
    for pokemon_index in range(
            last_url_index_downloaded + 1,
            __NUM_POKEMON__ + 1
    ):
        url: str = get_url(pokemon_index)
        with (urllib.request.urlopen(url) as fp):
            soup: BeautifulSoup = BeautifulSoup(fp, 'html.parser')
            children = [c for c in soup.children]
            assert len(children) == 4
            html = children[3]
            assert html.name == "html"
            html_children = [c for c in html.children]
            assert len(html_children) == 5
            body = html_children[3]
            assert body.name == "body"
            body_children = [c for c in body.children]
            assert len(body_children) == 12
            wrapper = body_children[5]
            assert wrapper.name == "div"
            assert wrapper.attrs['id'] == "wrapper"
            wrapper_children = [c for c in wrapper.children]
            assert len(wrapper_children) == 13
            content = wrapper_children[9]
            assert content.name == "div"
            assert content.attrs['id'] == "content"
            content_children = [c for c in content.children]
            assert len(content_children) == 4
            main = content_children[3]
            assert main.name == "main"
            main_children = [c for c in main.children]
            assert len(main_children) == 2
            center = main_children[1]
            assert center['align'] == 'center'
            center_dextables = center.find_all("table", class_="dextable")
            attack_form_attacks = None
            trash_form_attacks = None
            all_rotom_alternative_form_stats = None
            all_origin_form_stats = None
            all_sandy_form_stats = None
            all_sky_form_stats = None
            all_attack_form_stats = None
            sky_form_attacks = None
            form_to_attacks = None
            pokemon_information = None
            all_stats = None
            form_to_all_stats = None
            pre_evolution_index_to_level_to_moves = None
            level_to_attacks = None
            tm_or_hm_to_attack = None
            form_to_tm_or_hm_to_attack = None
            move_tutor_attacks = None
            form_to_move_tutor_attacks = None
            egg_moves = None
            game_to_level_to_moves = None
            special_moves = None
            for dextable in center_dextables:
                first_row_text = dextable.find("tr").text
                if first_row_text in __first_row_text_of_skippable_table__:
                    continue
                if (first_row_text ==
                        "\nName\nJp. Name\nNo.\nGender Ratio\nType\n"
                ):
                    pokemon_information = get_general_information(dextable)
                elif (first_row_text ==
                      "Platinum/HeartGold/SoulSilver Move Tutor Attacks" and
                      (pokemon_index == 386 or
                       pokemon_index == 413 or
                       pokemon_index == 487 or
                       pokemon_index == 492
                      )
                ):
                    form_to_move_tutor_attacks = \
                        get_forms_move_tutor_attacks(dextable)
                elif (first_row_text == "TM & HM Attacks" and
                      pokemon_index == 413
                ):
                    form_to_tm_or_hm_to_attack = \
                        get_tm_and_hm_attacks_for_forms(dextable)
                elif first_row_text in __first_row_text_for_level_up_moves__:
                    level_to_attacks = get_level_up_attacks(dextable)
                elif first_row_text == "TM & HM Attacks":
                    tm_or_hm_to_attack = get_tm_and_hm_attacks(dextable)
                elif (first_row_text ==
                      "Platinum/HeartGold/SoulSilver Move Tutor Attacks"
                ):
                    move_tutor_attacks = get_attacks(dextable)
                elif first_row_text == 'Move Tutor Attacks':
                    move_tutor_attacks = get_attacks(dextable)
                elif first_row_text == "Egg Moves (Details)":
                    egg_moves = get_attacks(dextable)
                elif first_row_text == "3rd Gen Only  Moves":
                    game_to_level_to_moves = get_third_gen_moves(dextable)
                elif first_row_text == "\nStats":
                    all_stats = get_stats(
                        dextable,
                        pokemon_information.name
                    )
                elif first_row_text == "\nStats - Attack Forme":
                    all_attack_form_stats = get_stats(
                        dextable,
                        pokemon_information.name
                    )
                elif first_row_text == "\nStats - Defense Forme":
                    all_defense_form_stats = get_stats(
                        dextable,
                        pokemon_information.name
                    )
                elif first_row_text == "\nStats - Speed Forme":
                    all_speed_form_stats = get_stats(
                        dextable,
                        pokemon_information.name
                    )
                elif first_row_text == "\nStats - Sandy Cloak":
                    all_sandy_form_stats = get_stats(
                        dextable,
                        pokemon_information.name
                    )
                elif first_row_text == "\nStats - Trash Cloak":
                    all_trash_form_stats = get_stats(
                        dextable,
                        pokemon_information.name
                    )
                elif first_row_text == '\nStats - Alternate Forms':
                    all_rotom_alternative_form_stats = get_stats(
                        dextable,
                        pokemon_information.name
                    )
                elif first_row_text == '\nStats - Origin Forme':
                    all_origin_form_stats = get_stats(
                        dextable,
                        pokemon_information.name
                    )
                elif first_row_text == '\nStats - Sky Forme':
                    all_sky_form_stats = get_stats(
                        dextable,
                        pokemon_information.name
                    )
                elif first_row_text == 'Pre-Evolution Moves':
                    pre_evolution_index_to_level_to_moves = \
                        get_pre_evolution_moves(dextable)
                elif first_row_text == "Special Moves":
                    special_moves = get_attacks(dextable)
                elif first_row_text == 'Diamond/Pearl Level Up (Attack Form)':
                    attack_form_attacks = get_level_up_attacks(dextable)
                elif first_row_text == "Diamond/Pearl Level Up (Defense Form)":
                    defense_form_attacks = get_level_up_attacks(dextable)
                elif first_row_text == "Diamond/Pearl Level Up (Speed Form)":
                    speed_form_attacks = get_level_up_attacks(dextable)
                elif first_row_text == "Diamond/Pearl Level Up (Sandy Cloak)":
                    sandy_form_attacks = get_level_up_attacks(dextable)
                elif first_row_text == "Diamond/Pearl Level Up (Trash Cloak)":
                    trash_form_attacks = get_level_up_attacks(dextable)
                elif first_row_text == 'Sky Forme Level Up':
                    sky_form_attacks = get_level_up_attacks(dextable)
                else:
                    assert False
            if attack_form_attacks is not None:
                form_to_attacks = dict()
                form_to_attacks["Attack Forme"] = attack_form_attacks
                form_to_attacks["Defense Forme"] = defense_form_attacks
                form_to_attacks["Speed Forme"] = speed_form_attacks
            if trash_form_attacks is not None:
                form_to_attacks = dict()
                form_to_attacks["Sandy Cloak"] = sandy_form_attacks
                form_to_attacks["Trash Cloak"] = trash_form_attacks
            if sky_form_attacks is not None:
                form_to_attacks = {"Sky Forme": sky_form_attacks}
            if all_attack_form_stats is not None:
                form_to_all_stats = dict()
                form_to_all_stats["Attack Forme"] = all_attack_form_stats
                form_to_all_stats["Defense Forme"] = all_defense_form_stats
                form_to_all_stats["Speed Forme"] = all_speed_form_stats
            if all_sandy_form_stats is not None:
                form_to_all_stats = dict()
                form_to_all_stats["Sandy Cloak"] = all_sandy_form_stats
                form_to_all_stats["Trash Cloak"] = all_trash_form_stats
            if all_rotom_alternative_form_stats is not None:
                form_to_all_stats = dict()
                form_to_all_stats[
                    "Alternate Forms"] = all_rotom_alternative_form_stats
            if all_origin_form_stats is not None:
                form_to_all_stats = dict()
                form_to_all_stats["Origin Forme"] = all_origin_form_stats
            if all_sky_form_stats is not None:
                form_to_all_stats = dict()
                form_to_all_stats["Sky Forme"] = all_sky_form_stats

            assert pokemon_information is not None
            assert all_stats is not None
            assert level_to_attacks is not None
            pokemon = SerebiiPokemon(
                name=pokemon_information.name,
                id=pokemon_information.id,
                ability=pokemon_information.ability,
                pounds=pokemon_information.pounds,
                pokemon_types=pokemon_information.pokemon_types,
                base_stats=all_stats,
                form_to_base_stats=form_to_all_stats,
                pre_evolution_index_to_level_to_moves=
                pre_evolution_index_to_level_to_moves,
                level_to_attacks=level_to_attacks,
                form_to_level_up_attacks=form_to_attacks,
                tm_or_hm_to_attack=tm_or_hm_to_attack,
                form_to_tm_or_hm_to_attack=form_to_tm_or_hm_to_attack,
                move_tutor_attacks=move_tutor_attacks,
                form_to_move_tutor_attacks=form_to_move_tutor_attacks,
                egg_moves=egg_moves,
                game_to_level_to_moves=game_to_level_to_moves,
                special_moves=special_moves,
            )
            pokemon_index_to_pokemon[pokemon_index] = pokemon
        time.sleep(0.5 + (random.random() / 2.0))
    return pokemon_index_to_pokemon


BANNED_POKEMON_NAMES = {
    "Mewtwo", "Mew", "Lugia", "Ho-Oh", "Celebi", "Kyogre", "Groudon",
    "Rayquaza", "Jirachi", "Deoxys", "Dialga", "Palkia", "Giratina", "Phione",
    "Manaphy", "Darkrai", "Shaymin", "Arceus"
}


def filter_banned_pokemon(pokemon_map) -> dict[int, SerebiiPokemon]:
    return {
        idx: p for idx, p in pokemon_map.items()
        if p.pokemon_information.name not in BANNED_POKEMON_NAMES
    }


def get_legal_serebii_pokemon() -> dict[int, SerebiiPokemon]:
    return filter_banned_pokemon(get_all_serebii_pokemon())


def get_all_serebii_pokemon() -> dict[int, SerebiiPokemon]:
    if not exists(SEREBII_POKEMON_FILE):
        pokemon_index_to_pokemon: dict[int, SerebiiPokemon] = \
            __scrape_serebii_for_pokemon_data__()
        with open(SEREBII_POKEMON_FILE, "w") as fo:
            fo: typing.IO
            fo.write(
                json.dumps(
                    cattr.unstructure(pokemon_index_to_pokemon),
                    indent=4
                )
            )
    with open(SEREBII_POKEMON_FILE, "r") as fo:
        fo: typing.IO
        pokemon_index_to_pokemon = cattr.structure(
            json.loads(fo.read()),
            dict[int, SerebiiPokemon]
        )
    return pokemon_index_to_pokemon


if __name__ == "__main__":
    g_pokemon_index_to_pokemon: dict[int, SerebiiPokemon] = \
        get_all_serebii_pokemon()
    pprint.pp(g_pokemon_index_to_pokemon)
