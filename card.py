import requests
import random


def get_all_hero_data(hero_name):
    try:
        while True:  # Keep trying until valid data is retrieved
            # Make the API request
            response = requests.get(
                f"https://api.pokemontcg.io/v2/cards?q=name:{hero_name}",
                headers={
                    "X-Api-Key": "29df32ad-c775-457a-b7f0-75e6fdaae1fd",
                    "Content-Type": "application/json",
                },
            )
            # Check if the request was successful
            response.raise_for_status()
            
            # Parse the JSON response
            data = response.json()
            
            # Extract all card data into a list
            card_list = data.get('data', [])
            
            # Return if valid data is found
            if card_list:
                return card_list
    
    except requests.exceptions.RequestException as e:
        return []

    
def create_card(all_data, pokemonList):
    """
    Continuously searches for a valid Pokémon card by validating data or fetching new Pokémon.
    Always returns a valid card.
    """
    while True:  # Persistent search loop
        for x in range(25):
            if len(all_data) > 20:  # Ensure enough data to select from
                index = random.randint(0, len(all_data) - 1)
                card = all_data[index]

                # Validate the card
                if "level" in card and card["level"].isdigit():
                    if all(attack.get("damage") for attack in card.get("attacks", [])):  # All attacks have damage
                        print(f"You encountered a wild {card['name']}!")
                        return card

        # If no valid card found in current dataset, switch to a new Pokémon
        hero_name = random.choice(pokemonList)
        all_data = get_all_hero_data(hero_name)

def create_card_trainer(all_data, pokemonList):
    """
    Continuously searches for a valid Pokémon card by validating data or fetching new Pokémon.
    Always returns a valid card.
    """
    while True:  # Persistent search loop
        for x in range(25):
            if len(all_data) > 20:  # Ensure enough data to select from
                index = random.randint(0, len(all_data) - 1)
                card = all_data[index]

                # Validate the card
                if "level" in card and card["level"].isdigit():
                    if all(attack.get("damage") for attack in card.get("attacks", [])):  # All attacks have damage
                        return card

        # If no valid card found in current dataset, switch to a new Pokémon
        hero_name = random.choice(pokemonList)
        all_data = get_all_hero_data(hero_name)

def get_card_from_pokemon(all_data):
    valid = False
    index = -1
    while (not valid) and (index<len(all_data)):
        index+=1
        # Check if the required keys exist in the selected card
        if "level" in all_data[index]:
            if all_data[index]['level'].isdigit():
                skip_card = False  # Flag to skip card details
                for attack in all_data[index]["attacks"]:
                    # Skip attack if damage is empty (None or empty string)
                    if not attack["damage"]:
                        skip_card = True
                        break  # No need to check further attacks, we already decided to skip the card
                
                # Skip card details if any attack's damage is empty
                if skip_card:
                    continue
                valid = True
    if valid:
        return all_data[index]
    else:
        return ""


def printCard(all_data):
    # Print card details after processing attacks
    print("Pokemon Details:")
    print(f"Name: {all_data['name']}")
    print("Attacks: ")
    print(f"\t{all_data['attacks'][0]['name']}: {all_data['attacks'][0]['damage']} damage")
    print(all_data['attacks'][0]['cost'])
    if len(all_data['attacks'])==2:
        print(f"\t{all_data['attacks'][1]['name']}: {all_data['attacks'][1]['damage']} damage")
        print(all_data['attacks'][1]['cost'])
    if len(all_data['attacks'])==3:
        print(f"\t{all_data['attacks'][2]['name']}: {all_data['attacks'][2]['damage']} damage")
        print(all_data['attacks'][2]['cost'])
    print(f"Level: {all_data['level']}")
    print(f"HP: {all_data['hp']}")
    print(f"Types: {all_data['types']}")
    #print(f"Weaknesses: {all_data[index]['weaknesses']}")

# with open("pokemonNames.txt", "r") as pokemonNames:
#     pokemonList = []
#     for line in pokemonNames:
#        line = line.strip("\n")
#        pokemonList.append(line)

# pokemon = ""
# all_data = get_all_hero_data(pokemon)
# pokemon = create_card(all_data, pokemonList)
# printCard(pokemon)
# one in five chance for a crit
# check if has weaknesses or resistances
# 0.4 times attack damage