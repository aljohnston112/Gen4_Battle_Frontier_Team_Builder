import random
import time
import urllib.request
from collections import defaultdict

from bs4 import BeautifulSoup

from data_class.PokemonInformation import PokemonInformation
from data_class.PokemonType import convert_to_pokemon_type

base_url = "https://www.serebii.net/pokedex-dp/"
num_pokemon = 493


def get_url(index: int):
    return base_url + str(index).zfill(3) + ".shtml"


def get_general_information(dextable):
    rows = [row for row in dextable.find_all("tr")]
    assert rows[0] == "\nName\nJp. Name\nNo.\nGender Ratio\nType\n"
    columns = rows[1].text.strip().split("\n")
    name = columns[0].strip()
    national_id = int(columns[2].strip().split("Johto")[0].split("#")[1])
    pokemon_types = []
    type_image_links = rows[1].find_all("a")
    for type_image_link in type_image_links:
        type_name = type_image_link['href'].strip().split('/')[2].split('.')[0]
        pokemon_types.append(convert_to_pokemon_type(type_name))
    ability = rows[6].text.strip().split(":")[1].strip()
    assert rows[8].text == "\nClassification\nHeight\nWeight\nCapture Rate\nBase Egg Steps\n"
    pounds = float(rows[9].text.strip().split("\n")[2].split("lbs")[0])
    return PokemonInformation(
        name=name,
        id=national_id,
        ability=ability,
        pounds=pounds
    )


def __scrape_serebii_for_move_sets__():
    pokemon_to_moves = defaultdict(lambda: list())
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
            center_dextables = center.find_all("table", class_="dextable")
            first_row_text_that_marks_skippable_table = [
                "\nImages\n",
                "\n\n\t\tDamage Taken\n\t\t\n",
                "\nWild Hold Item\nEgg Groups\n",
                "\nEvolutionary Chain\n",
                "\n\nFlavour Text\n\n",
                "\n\nLocation\n\n",
                "HeartGold/SoulSilver Move Tutor Attacks",
                "Base/Max Pokéathlon Stats",
            ]
            for dextable in center_dextables:
                first_row_text = dextable.find("tr").text
                if first_row_text not in first_row_text_that_marks_skippable_table:
                    if first_row_text == "\nName\nJp. Name\nNo.\nGender Ratio\nType\n":
                        pokemon_information = get_general_information(dextable)
                    elif first_row_text == "Diamond/Pearl/Platinum/HeartGold/SoulSilver Level Up":
                        pass
                    elif first_row_text == "TM & HM Attacks":
                        pass
                    elif first_row_text == "Platinum/HeartGold/SoulSilver Move Tutor Attacks":
                        pass
                    elif first_row_text == "Egg Moves (Details)":
                        pass
                    elif first_row_text == "3rd Gen Only  Moves":
                        pass
                    elif first_row_text == "\nStats":
                        pass
                    else:
                        assert False
        time.sleep(0.5 + (random.random() / 2.0))


if __name__ == "__main__":
    __scrape_serebii_for_move_sets__()
