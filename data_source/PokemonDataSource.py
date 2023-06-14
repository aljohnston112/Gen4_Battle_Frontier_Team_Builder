import urllib.request
from collections import defaultdict

from bs4 import BeautifulSoup, NavigableString

from data_class.Attack import Attack
from data_class.Category import convert_to_attack_category
from data_class.PokemonInformation import PokemonInformation
from data_class.PokemonType import convert_to_pokemon_type

base_url = "https://www.serebii.net/pokedex-dp/"
num_pokemon = 493


def get_url(index: int):
    return base_url + str(index).zfill(3) + ".shtml"


def assert_is_attack_double_wide_data_cell(td):
    assert td.name == 'td'
    assert td['rowspan'] == '2'
    assert td['class'] == ['fooinfo']


def assert_is_attack_single_wide_data_cell(td):
    assert td['align'] == 'center'
    assert td['class'] == ['fooinfo']


def __process_attacks_table_rows__(attacks_table_head_children) -> defaultdict[str, list]:
    level_to_attack: defaultdict[str, list] = defaultdict(lambda: list())

    attacks_table_head_children = [c for c in attacks_table_head_children if c != '\n']

    first_row = attacks_table_head_children[0]
    assert first_row.name == "tr"
    first_row_children = [c for c in first_row.children]
    assert len(first_row_children) == 1

    first_row_table_data = first_row_children[0]
    assert first_row_table_data.name == 'td'
    assert first_row_table_data['colspan'] == '10' or first_row_table_data['colspan'] == '9'
    assert first_row_table_data['class'] == ['fooevo']
    first_row_table_data_children = [c for c in first_row_table_data.children]
    assert len(first_row_table_data_children) == 1

    table_title = first_row_table_data_children[0]
    assert isinstance(table_title, NavigableString)
    assert table_title == 'Diamond/Pearl/Platinum/HeartGold/SoulSilver Level Up' or \
           table_title == 'TM & HM Attacks'

    second_row = attacks_table_head_children[1]
    assert second_row.name == "tr"
    second_row_children = [c for c in second_row.children]
    assert len(second_row_children) == 8

    assert second_row_children[0].text == 'Level' or \
           second_row_children[0].text == "TM/HM #"
    assert second_row_children[1].text == 'Attack Name'
    assert second_row_children[2].text == 'Type'
    assert second_row_children[3].text == 'Cat.'
    assert second_row_children[4].text == 'Att.'
    assert second_row_children[5].text == 'Acc.'

    current_row = 2
    while current_row < len(attacks_table_head_children):
        ith_row = attacks_table_head_children[current_row]
        assert ith_row.name == "tr"
        ith_row_children = [c for c in ith_row.children]
        ith_row_children = [c for c in ith_row_children if c != '\n']
        assert len(ith_row_children) == 8

        assert_is_attack_double_wide_data_cell(ith_row_children[0])
        level = ith_row_children[0].text
        if level == '—':
            level = '0'

        assert_is_attack_double_wide_data_cell(ith_row_children[1])
        attack_name = ith_row_children[1].text

        assert_is_attack_single_wide_data_cell(ith_row_children[2])
        attack_type_children = [c for c in ith_row_children[2].children]
        assert len(attack_type_children) == 1
        attack_type = attack_type_children[0]['src'].split("/")[-1].split(".")[0]

        assert_is_attack_single_wide_data_cell(ith_row_children[3])
        attack_category_children = [c for c in ith_row_children[3].children]
        assert len(attack_category_children) == 1
        attack_category = attack_category_children[0]['src'].split("/")[-1].split(".")[0]

        assert_is_attack_single_wide_data_cell(ith_row_children[4])
        attack_power = ith_row_children[4].text
        if attack_power == "--" or attack_power == "??":
            attack_power = 0
        else:
            attack_power = int(attack_power)

        assert_is_attack_single_wide_data_cell(ith_row_children[5])
        attack_accuracy = ith_row_children[5].text
        if attack_accuracy == "--":
            attack_accuracy = 100
        else:
            attack_accuracy = int(attack_accuracy)

        attack = Attack(
            attack_name,
            convert_to_pokemon_type(attack_type),
            convert_to_attack_category(attack_category),
            attack_power,
            attack_accuracy
        )

        level_to_attack[str(level)].append(attack)
        current_row += 2
    return level_to_attack


def __process_general_information_table__(general_information_table):
    assert len(general_information_table) == 17
    general_information_table_children = [c for c in general_information_table.children]
    assert general_information_table_children[1].text == '\nName\nJp. Name\nNo.\nGender Ratio\nType\n'
    cells = general_information_table_children[3].text.split("\n")
    assert len(cells) == 7
    name = cells[1]
    national_id = int(cells[3].split(":")[1][2:-5])
    assert len(general_information_table_children[5].text.split(":")) == 2
    assert general_information_table_children[5].text.split(":")[0].strip() == "Ability"
    ability = general_information_table_children[5].text.split(":")[1].strip()
    assert general_information_table_children[
               9].text == '\nClassification\nHeight\nWeight\nCapture Rate\nBase Egg Steps\n'
    cells = general_information_table_children[11].text.split("\n")
    assert len(cells) == 7
    pounds = cells[3][:-3]

    return PokemonInformation(name, national_id, ability, pounds)


def __process_move_tutor_attacks_table_rows__(attacks_table_children):
    attacks = list()

    attacks_table_head_children = [c for c in attacks_table_children if c != '\n']

    first_row = attacks_table_head_children[0]
    assert first_row.name == "tr"
    first_row_children = [c for c in first_row.children]
    assert len(first_row_children) == 1

    first_row_table_data = first_row_children[0]
    assert first_row_table_data.name == 'td'
    assert first_row_table_data['colspan'] == '10' or first_row_table_data['colspan'] == '9'
    assert first_row_table_data['class'] == ['fooevo']
    first_row_table_data_children = [c for c in first_row_table_data.children]
    assert len(first_row_table_data_children) == 1

    table_title = first_row_table_data_children[0]
    assert isinstance(table_title, NavigableString)
    assert table_title == 'Platinum/HeartGold/SoulSilver Move Tutor Attacks'

    second_row = attacks_table_head_children[1]
    assert second_row.name == "tr"
    second_row_children = [c for c in second_row.children]
    assert len(second_row_children) == 7

    assert second_row_children[0].text == 'Attack Name'
    assert second_row_children[1].text == 'Type'
    assert second_row_children[2].text == 'Cat.'
    assert second_row_children[3].text == 'Att.'
    assert second_row_children[4].text == 'Acc.'

    current_row = 2
    while current_row < len(attacks_table_head_children):
        ith_row = attacks_table_head_children[current_row]
        assert ith_row.name == "tr"
        ith_row_children = [c for c in ith_row.children]
        ith_row_children = [c for c in ith_row_children if c != '\n']
        assert len(ith_row_children) == 7

        assert_is_attack_double_wide_data_cell(ith_row_children[0])
        attack_name = ith_row_children[1].text

        assert_is_attack_single_wide_data_cell(ith_row_children[1])
        attack_type_children = [c for c in ith_row_children[1].children]
        assert len(attack_type_children) == 1
        attack_type = attack_type_children[0]['src'].split("/")[-1].split(".")[0]

        assert_is_attack_single_wide_data_cell(ith_row_children[2])
        attack_category_children = [c for c in ith_row_children[2].children]
        assert len(attack_category_children) == 1
        attack_category = attack_category_children[0]['src'].split("/")[-1].split(".")[0]

        assert_is_attack_single_wide_data_cell(ith_row_children[3])
        attack_power = ith_row_children[3].text
        if attack_power == "--" or attack_power == "??":
            attack_power = 0
        else:
            attack_power = int(attack_power)

        assert_is_attack_single_wide_data_cell(ith_row_children[5])
        attack_accuracy = ith_row_children[4].text
        if attack_accuracy == "--":
            attack_accuracy = 100
        else:
            attack_accuracy = int(attack_accuracy)

        attack = Attack(
            attack_name,
            convert_to_pokemon_type(attack_type),
            convert_to_attack_category(attack_category),
            attack_power,
            attack_accuracy
        )

        attacks.append(attack)
        current_row += 2
    return attacks


def __scrape_serebii_for_move_sets__():
    last_url_index = 0
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
            center_children = [c for c in center.children]
            assert len(center_children) == 6

            general = center_children[5]
            assert general.name == 'p'
            general_children = [c for c in general.children]
            assert len(general_children) == 13

            first_dextable = general_children[4]
            assert first_dextable.name == 'table'
            assert first_dextable['class'] == ['dextable']
            pokemon_information = __process_general_information_table__(first_dextable)

            location = general_children[12]
            assert location.name == 'p'
            location_children = [c for c in location.children]
            assert len(location_children) == 4

            attacks = location_children[3]
            assert attacks.name == 'p'
            attacks_children = [c for c in attacks.children]
            assert len(attacks_children) == 3

            attacks_table = attacks_children[1]
            assert attacks_table.name == "table"
            assert attacks_table['class'] == ['dextable']
            attacks_table_children = [c for c in attacks_table.children]
            assert len(attacks_table_children) == 1

            attacks_table_head = attacks_table_children[0]
            attacks_table_head_children = [c for c in attacks_table_head]
            level_to_attacks = __process_attacks_table_rows__(attacks_table_head_children)

            attacks = attacks_children[2]
            assert attacks.name == 'p'
            attacks_children = [c for c in attacks.children]
            assert len(attacks_children) == 3

            attacks_table = attacks_children[0]
            assert attacks_table.name == "table"
            assert attacks_table['class'] == ['dextable']
            attacks_table_children = [c for c in attacks_table.children]
            tm_or_hm_to_attacks = __process_attacks_table_rows__(attacks_table_children)

            attacks_table = attacks_children[1]
            assert attacks_table.name == "table"
            assert attacks_table['class'] == ['dextable']
            attacks_table_children = [c for c in attacks_table.children]

            attacks_table_head_children = [c for c in attacks_table_children if c != '\n']
            attacks_table_children_head = attacks_table_head_children[0]
            move_tutor_attacks = __process_move_tutor_attacks_table_rows__(attacks_table_children_head)

            attacks = attacks_children[2]
            assert attacks.name == 'p'
            attacks_children = [c for c in attacks.children]
            assert len(attacks_children) == 2

            attacks_table = attacks_children[0]
            assert attacks_table.name == "table"
            assert attacks_table['class'] == ['dextable']
            attacks_table_children = [c for c in attacks_table.children]
            tm_or_hm_to_attacks = __process_attacks_table_rows__(attacks_table_children)

            print()


if __name__ == "__main__":
    __scrape_serebii_for_move_sets__()
