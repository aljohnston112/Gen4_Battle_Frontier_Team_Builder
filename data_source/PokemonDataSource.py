import random
import time
import urllib.request
from collections import defaultdict

from bs4 import BeautifulSoup

from data_class.AllStats import AllStats
from data_class.Attack import Attack
from data_class.BaseStats import BaseStats
from data_class.Category import convert_to_attack_category
from data_class.PokemonInformation import PokemonInformation
from data_class.PokemonType import convert_to_pokemon_type
from data_class.Stat import Stat, StatEnum
from data_class.Stats import Stats

base_url = "https://www.serebii.net/pokedex-dp/"
num_pokemon = 493


def get_url(index: int):
    return base_url + str(index).zfill(3) + ".shtml"


def get_general_information(dextable):
    rows = [row for row in dextable.find_all("tr")]
    assert rows[0].text == "\nName\nJp. Name\nNo.\nGender Ratio\nType\n"
    columns = rows[1].text.strip().split("\n")
    name = columns[0].strip()
    national_id = int(columns[2].strip().split("Johto")[0].split("Sinnoh")[0].split("#")[1])
    pokemon_types = []
    type_image_links = rows[1].find_all("a")
    for type_image_link in type_image_links:
        type_name = type_image_link['href'].strip().split('/')[2].split('.')[0]
        pokemon_types.append(convert_to_pokemon_type(type_name))

    ability_index = 6
    weight_index = 9
    if rows[6].text == "\nClassification\nHeight\nWeight\nCapture Rate\nBase Egg Steps\n":
        ability_index -= 2
        weight_index -= 2
    elif rows[7].text == "\nClassification\nHeight\nWeight\nCapture Rate\nBase Egg Steps\n":
        ability_index -= 1
        weight_index -= 1
    elif rows[9].text == "\nClassification\nHeight\nWeight\nCapture Rate\nBase Egg Steps\n":
        ability_index += 1
        weight_index += 1
    else:
        assert rows[8].text == "\nClassification\nHeight\nWeight\nCapture Rate\nBase Egg Steps\n"
    assert "Ability" in rows[ability_index].text
    ability = rows[ability_index].text.strip().split(":")[1].strip()
    pounds = float(rows[weight_index].text.strip().split("\n")[2].split("lbs")[0])
    return PokemonInformation(
        name=name,
        id=national_id,
        ability=ability,
        pounds=pounds
    )


def get_level_up_attacks(dextable):
    level_to_attacks = defaultdict(lambda: [])
    rows = [row for row in dextable.find_all("tr")]
    assert rows[0].text == "Diamond/Pearl/Platinum/HeartGold/SoulSilver Level Up" or \
           rows[0].text == 'Platinum/HeartGold/SoulSilver Level Up' or \
           rows[0].text == 'Diamond/Pearl/Platinum Level Up'
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
        pokemon_type = type_images[0]['src'].split("/")[-1].split(".")[0].strip()
        category_images = columns[3].find_all("img")
        assert len(category_images) == 1
        category = category_images[0]['src'].split("/")[-1].split(".")[0].strip()
        power = columns[4].text
        if power == "--" or \
                name == "Endeavor" or \
                name == "Dragon Rage" or \
                name == "Super Fang" or \
                name == "Sonicboom" or \
                name == "Mirror Coat" or \
                name == "Counter" or \
                name == "Bide":
            power = 0
        elif name == "Gyro Ball" or name == "Magnitude":
            power = 150
        elif name == "Horn Drill" or \
                name == "Fissure" or \
                name == "Sheer Cold" or \
                name == "Guillotine":
            power = -1
        elif name == "Natural Gift":
            power = 80
        elif name == "Low Kick" or name == "Present":
            power = 120
        elif name == "Seismic Toss" or name == "Night Shade":
            power = 100
        elif name == "Punishment" or \
                name == "Reversal" or \
                name == "Flail" or \
                name == "Trump Card":
            power = 200
        elif name == "Fling":
            power = 130
        elif name == "Wring Out":
            power = 102
        elif name == "Spit Up":
            power = 300
        elif name == "Hidden Power":
            power = 70
        elif name == "Psywave":
            power = 150
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
            Attack(
                name=name,
                pokemon_type=convert_to_pokemon_type(pokemon_type),
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
        pokemon_type = type_images[0]['src'].split("/")[-1].split(".")[0].strip()
        category_images = columns[3].find_all("img")
        assert len(category_images) == 1
        category = category_images[0]['src'].split("/")[-1].split(".")[0].strip()
        power = columns[4].text
        if power == "--":
            power = 0
        elif name == "Hidden Power":
            power = 70
        elif name == "Frustration" or name == "Return":
            power = 102
        elif name == "Natural Gift":
            power = 80
        elif name == "Grass Knot":
            power = 120
        elif name == "Fling":
            power = 130
        elif name == "Gyro Ball":
            power = 150
        power = int(power)
        accuracy = columns[5].text
        if accuracy == "--":
            accuracy = 100
        accuracy = int(accuracy)
        effect_chance = columns[7].text
        if effect_chance == "--":
            effect_chance = 0
        effect_chance = int(effect_chance)
        tm_or_hm_to_attack[tm_or_hm] = Attack(
            name=name,
            pokemon_type=convert_to_pokemon_type(pokemon_type),
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
    assert rows[0].text == "Platinum/HeartGold/SoulSilver Move Tutor Attacks" or \
           rows[0].text == "Egg Moves (Details)" or \
           rows[0].text == 'Move Tutor Attacks' or \
           rows[0].text == "Special Moves"
    assert rows[1].text.strip() == 'Attack NameTypeCat.Att.Acc.PPEffect %'
    current_index = 2
    while current_index < len(rows):
        columns = rows[current_index].find_all("td")
        name = columns[0].text.strip()
        if "HGSS Only" in name:
            return None
        type_images = columns[1].find_all("img")
        assert len(type_images) == 1
        pokemon_type = type_images[0]['src'].split("/")[-1].split(".")[0].strip()
        category_images = columns[2].find_all("img")
        assert len(category_images) == 1
        category = category_images[0]['src'].split("/")[-1].split(".")[0].strip()
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
            power = 70
        elif name == "Frustration" or name == "Return":
            power = 102
        elif name == "Natural Gift":
            power = 80
        elif name == "Grass Knot" or name == "Present":
            power = 120
        elif name == "Flail" or name == "Reversal" or name == "Punishment" or name == "Trump Card":
            power = 200
        elif name == "Horn Drill" or name == "Fissure" or name == "Sheer Cold":
            power = -1
        elif name == "Spit Up":
            power = 300
        elif name == "Psywave" or name == "Magnitude":
            power = 150
        elif name == "Wring Out":
            power = 102
        elif name == "Night Shade" or name == "Seismic Toss":
            power = 100
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
            Attack(
                name=name,
                pokemon_type=convert_to_pokemon_type(pokemon_type),
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
        pokemon_type = type_images[0]['src'].split("/")[-1].split(".")[0].strip()
        category_images = columns[2].find_all("img")
        assert len(category_images) == 1
        category = category_images[0]['src'].split("/")[-1].split(".")[0].strip()
        power = columns[3].text
        if power == "--":
            power = 0
        if name == "Hidden Power":
            power = 70
        elif name == "Frustration" or name == "Return":
            power = 102
        elif name == "Natural Gift":
            power = 80
        elif name == "Grass Knot":
            power = 120
        power = int(power)
        accuracy = columns[4].text
        if accuracy == "--":
            accuracy = 100
        accuracy = int(accuracy)
        effect_chance = columns[6].text
        if effect_chance == "--":
            effect_chance = 0
        effect_chance = int(effect_chance)
        if name == "" and pokemon_type == "" and power == 0 and accuracy == 100 and effect_chance == 0:
            current_index += 1
        else:
            attack = (
                Attack(
                    name=name,
                    pokemon_type=convert_to_pokemon_type(pokemon_type),
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


def get_stats(dextable, name):
    rows = [row for row in dextable.find_all("tr")]
    assert rows[0].text == "\nStats"
    assert rows[1].text.strip() == 'HP\nAttack\nDefense\nSp. Attack\nSp. Defense\nSpeed'
    base_stat_tokens = rows[2].text.split("\n")
    assert len(base_stat_tokens) == 7
    base_hp = int(base_stat_tokens[1])
    base_attack = int(base_stat_tokens[2])
    base_defense = int(base_stat_tokens[3])
    base_special_attack = int(base_stat_tokens[4])
    base_special_defense = int(base_stat_tokens[5])
    base_speed = int(base_stat_tokens[6])
    base_stats = BaseStats(
        name,
        Stats(
            name=name,
            health=base_hp,
            attack=base_attack,
            defense=base_defense,
            special_attack=base_special_attack,
            special_defense=base_special_defense,
            speed=base_speed
        )
    )
    max_stats_hindering_nature_tokens = rows[3].text.split("\n")
    level_50_min_hp_stat = int(max_stats_hindering_nature_tokens[2].split("-")[0].strip())
    level_50_min_attack_stat = int(max_stats_hindering_nature_tokens[3].split("-")[0].strip())
    level_50_min_defense_stat = int(max_stats_hindering_nature_tokens[4].split("-")[0].strip())
    level_50_min_special_attack_stat = int(max_stats_hindering_nature_tokens[5].split("-")[0].strip())
    level_50_min_special_defense_stat = int(max_stats_hindering_nature_tokens[6].split("-")[0].strip())
    level_50_min_speed_stat = int(max_stats_hindering_nature_tokens[7].split("-")[0].strip())
    level_50_min_stats = Stats(
        name=name,
        health=level_50_min_hp_stat,
        attack=level_50_min_attack_stat,
        defense=level_50_min_defense_stat,
        special_attack=level_50_min_special_attack_stat,
        special_defense=level_50_min_special_defense_stat,
        speed=level_50_min_speed_stat
    )

    max_stats_hindering_nature_tokens = rows[4].text.split("\n")
    level_100_min_hp_stat = int(max_stats_hindering_nature_tokens[1].split("-")[0].strip())
    level_100_min_attack_stat = int(max_stats_hindering_nature_tokens[2].split("-")[0].strip())
    level_100_min_defense_stat = int(max_stats_hindering_nature_tokens[3].split("-")[0].strip())
    level_100_min_special_attack_stat = int(max_stats_hindering_nature_tokens[4].split("-")[0].strip())
    level_100_min_special_defense_stat = int(max_stats_hindering_nature_tokens[5].split("-")[0].strip())
    level_100_min_speed_stat = int(max_stats_hindering_nature_tokens[6].split("-")[0].strip())
    level_100_min_stats = Stats(
        name=name,
        health=level_100_min_hp_stat,
        attack=level_100_min_attack_stat,
        defense=level_100_min_defense_stat,
        special_attack=level_100_min_special_attack_stat,
        special_defense=level_100_min_special_defense_stat,
        speed=level_100_min_speed_stat
    )

    max_stats_beneficial_nature_tokens = rows[7].text.split("\n")
    level_50_max_hp_stat = int(max_stats_beneficial_nature_tokens[2].split("-")[1].strip())
    level_50_max_attack_stat = int(max_stats_beneficial_nature_tokens[3].split("-")[1].strip())
    level_50_max_defense_stat = int(max_stats_beneficial_nature_tokens[4].split("-")[1].strip())
    level_50_max_special_attack_stat = int(max_stats_beneficial_nature_tokens[5].split("-")[1].strip())
    level_50_max_special_defense_stat = int(max_stats_beneficial_nature_tokens[6].split("-")[1].strip())
    level_50_max_speed_stat = int(max_stats_beneficial_nature_tokens[7].split("-")[1].strip())
    level_50_max_stats = Stats(
        name=name,
        health=level_50_max_hp_stat,
        attack=level_50_max_attack_stat,
        defense=level_50_max_defense_stat,
        special_attack=level_50_max_special_attack_stat,
        special_defense=level_50_max_special_defense_stat,
        speed=level_50_max_speed_stat
    )

    max_stats_beneficial_nature_tokens = rows[8].text.split("\n")
    level_100_max_hp_stat = int(max_stats_beneficial_nature_tokens[1].split("-")[1].strip())
    level_100_max_attack_stat = int(max_stats_beneficial_nature_tokens[2].split("-")[1].strip())
    level_100_max_defense_stat = int(max_stats_beneficial_nature_tokens[3].split("-")[1].strip())
    level_100_max_special_attack_stat = int(max_stats_beneficial_nature_tokens[4].split("-")[1].strip())
    level_100_max_special_defense_stat = int(max_stats_beneficial_nature_tokens[5].split("-")[1].strip())
    level_100_max_speed_stat = int(max_stats_beneficial_nature_tokens[6].split("-")[1].strip())
    level_100_max_stats = Stats(
        name=name,
        health=level_100_max_hp_stat,
        attack=level_100_max_attack_stat,
        defense=level_100_max_defense_stat,
        special_attack=level_100_max_special_attack_stat,
        special_defense=level_100_max_special_defense_stat,
        speed=level_100_max_speed_stat
    )
    return AllStats(
        name=name,
        base_stats=base_stats,
        level_50_min_stats=level_50_min_stats,
        level_50_max_stats=level_50_max_stats,
        level_100_min_stats=level_100_min_stats,
        level_100_max_stats=level_100_max_stats
    )


def get_pre_evolution_moves(dextable):
    pre_evolution_index_to_level_to_moves = defaultdict(lambda: defaultdict(lambda: list()))
    rows = [row for row in dextable.find_all("tr")]
    assert rows[0].text == 'Pre-Evolution Moves'
    assert rows[1].text.strip() == 'Attack NameTypeCat.Att.Acc.PPEffect % Means'
    current_index = 2
    while current_index < len(rows):
        columns = rows[current_index].find_all("td")
        if columns[0].text == 'Base/Max Pokéathlon Stats' or \
                columns[0].text == 'Base/Max Pok�athlon Stats':
            current_index = len(rows)
        else:
            name = columns[0].text.strip()
            type_images = columns[1].find_all("img")
            assert len(type_images) == 1
            pokemon_type = type_images[0]['src'].split("/")[-1].split(".")[0].strip()
            category_images = columns[2].find_all("img")
            assert len(category_images) == 1
            category = category_images[0]['src'].split("/")[-1].split(".")[0].strip()
            power = columns[3].text
            if power == "--" or name == "Endeavor" or name == "Bide":
                power = 0
            if name == "Hidden Power":
                power = 70
            elif name == "Frustration" or name == "Return":
                power = 102
            elif name == "Natural Gift":
                power = 80
            elif name == "Grass Knot":
                power = 120
            elif name == "Horn Drill":
                power = -1
            elif name == "Reversal" or name == "Flail" or name == "Trump Card":
                power = 200
            elif name == "Wring Out":
                power = 102
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
                Attack(
                    name=name,
                    pokemon_type=convert_to_pokemon_type(pokemon_type),
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
            pokemon_index = int(pokemon_images[0]['src'].split("/")[-1].split(".")[0])
            possible_level = columns[1].text.split(".")
            if len(possible_level) > 1:
                level = int(possible_level[1].strip())
            else:
                level = 0
            pre_evolution_index_to_level_to_moves[pokemon_index][level].append(attack)
            current_index += 2
    return pre_evolution_index_to_level_to_moves


def __scrape_serebii_for_move_sets__():
    pokemon_to_moves = defaultdict(lambda: list())
    last_url_index = 278
    for pokemon_index in range(last_url_index + 1, num_pokemon + 1):
        url = get_url(pokemon_index)
        with urllib.request.urlopen(url) as fp:
            soup = BeautifulSoup(fp, 'html.parser')
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
            first_row_text_that_marks_skippable_table = [
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
            ]
            for dextable in center_dextables:
                first_row_text = dextable.find("tr").text
                if first_row_text not in first_row_text_that_marks_skippable_table:
                    if first_row_text == "\nName\nJp. Name\nNo.\nGender Ratio\nType\n":
                        pokemon_information = get_general_information(dextable)
                    elif first_row_text == "Diamond/Pearl/Platinum/HeartGold/SoulSilver Level Up" or \
                            first_row_text == 'Platinum/HeartGold/SoulSilver Level Up' or \
                            first_row_text == 'Diamond/Pearl/Platinum Level Up':
                        level_to_attacks = get_level_up_attacks(dextable)
                    elif first_row_text == "TM & HM Attacks":
                        tm_or_hm_to_attack = get_tm_and_hm_attacks(dextable)
                    elif first_row_text == "Platinum/HeartGold/SoulSilver Move Tutor Attacks":
                        gen_4_move_tutor_attacks = get_attacks(dextable)
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
                    elif first_row_text == 'Pre-Evolution Moves':
                        pre_evolution_index_to_level_to_moves = get_pre_evolution_moves(dextable)
                    elif first_row_text == "Special Moves":
                        special_moves = get_attacks(dextable)
                    else:
                        assert False
        time.sleep(0.5 + (random.random() / 2.0))


if __name__ == "__main__":
    __scrape_serebii_for_move_sets__()
