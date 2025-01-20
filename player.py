import random
import time
import pyfiglet
from colorama import Fore, Back, Style
from tkinter import *

try:
    import trainerBattle
    import gameBoard
    import card
    import myPokemon

except ImportError as e:
    print(f"Import error: {e}")

with open("shopItems.txt", "r") as shopItems:
    class Player:
        def __init__(self, board):
            # Initialize player with their name, inventory, and a starter Pokémon
            self._player = input("What is your name? ")  # Prompt user for their name
            self._inventory = {"pokeball": 15, "potion": 2}  # Initial inventory with basic items
            self._pokemonList = []  # List of Pokémon the player owns
            self._pokemonClassList = []  # List to store instances of Pokémon objects
            self._optionList = ["move", "bag", "pokemon", "home"]  # Possible options during gameplay
            self._battleOptions = ["battle", "pokemon", "bag", "run"]  # Options during a battle
            self._homeOptions = ["heal your pokemon (heal)", "store", "pokemon", "bag", "box", "back"]  # Options when at home
            self._steps = 0
            self._box = []
            self._trainer = 0
            # Handle healing and status items
            self._healing_items = {
                "revive": lambda p: (p.up_status("revive"), p.heal(0, False, True, False)),
                "max revive": lambda p: (p.up_status("max revive"), p.heal(0, True, False, False)),
                "soda pop": lambda p: p.heal(25, False, False, False),
                "potion": lambda p: p.heal(10, False, False, False),
                "super potion": lambda p: p.heal(15, False, False, False),
                "max potion": lambda p: p.heal(0, True, False, False),
                "lemonade": lambda p: p.heal(35, False, False, False),
                "hp up": lambda p: p.heal(0, False, False, True),
                "fresh water": lambda p: p.heal(5, False, False, False),
                "hyper potion": lambda p: p.heal(50, False, False, False),
            }

            self._status_items = {
                "full heal": lambda p: [p.special_potion(s) for s in ["paralysis", "poison", "burn", "freeze", "sleep"]],
                "full restore": lambda p: [p.special_potion(s) for s in ["paralysis", "poison", "burn", "freeze", "sleep"]] + [p.heal(0, True, False, False)],
                "dire hit": lambda p: p.up_status("dire hit"),
                "ice heal": lambda p: p.special_potion("freeze"),
                "antidote": lambda p: p.special_potion("poison"),
                "awakening": lambda p: p.special_potion("sleep"),
                "burn heal": lambda p: p.special_potion("burn"),
                "paralyze heal": lambda p: p.special_potion("paralysis"),
            }
            self._boxNames = []
            self._pokemonCreated = ""  # Placeholder for the created Pokémon object
            self._money = 3000  # Starting money for the player
            self._shopItems = []  # List of items available for purchase in the shop
            for line in shopItems:
                line = line.replace("\n", "")  # Remove newline character
                line = line.lower()  # Convert to lowercase for easier comparison
                line = line.split("/")  # Split each line by '/' to extract item details
                self._shopItems.append(line)  # Append item data to the shopItems list
            
            self.board = board
            time.sleep(2)
            print(f"Welcome {self._player} to: ")
            time.sleep(3)
            text = pyfiglet.figlet_format("Pokemon")
            text = text.splitlines()
            total_lines = len(text)
            black_line_index = total_lines // 2
            split_point = black_line_index
            colored_text = ""
            for i, line in enumerate(text):
                if i < split_point:
                    color = Fore.RED
                elif i == black_line_index:
                    color = Fore.BLACK
                else:
                    color = Fore.WHITE
                colored_text += f"{color}{line}{Style.RESET_ALL}\n"
            print(colored_text)
            time.sleep(2)
            self.getPokemon()  # Call method to let the player choose their first Pokémon
        
        def printOptions(self):
            # Print available options for the player
            print("----------------------------")
            for option in self._optionList:
                print(option.upper())  # Display each option in the option list
            print("----------------------------")
            return

        def options(self):
            # Allow the player to choose an action
            self.printOptions()
            option = input("What do you want to do? ")
            if option.lower() == "move":
                self.move()  # Call the move function
            elif option.lower() == "bag":
                self.bag(self.options)  # Call the bag function
            elif option.lower() == "pokemon":
                self.pokemon(self.options)  # Call the pokemon function
            elif option.lower() == "home":
                print("You went home")  # Print message when choosing "home"
                self.home()  # Call the home function
            else:
                # Reprint options if the input is invalid
                self.options()

        def move(self):
            valid = False
            while not valid:
                # Get input from the user for movement direction
                direction = input("Which direction would you like to go (left, right, up, down)? ").lower()
                time.sleep(1)

                if direction in ["left", "right", "up", "down"]:
                    # Try moving the player
                    moved, trainer_encounter, gym_encounter, home_encounter = self.board.movePlayer(direction)
                    
                    if not moved:
                        print("You can't move that way!")
                        continue

                    valid = True
                    self._steps += 1

                    # Check if a trainer is encountered
                    if home_encounter:
                        self.home()
                        return
                    if trainer_encounter:
                        self._steps = 0
                        print("A trainer would like to battle!")
                        self.trainer(len(self._pokemonClassList))
                        return
                    
                    if gym_encounter:
                        self._steps = 0
                        print("A gym trainer would like to battle!")
                        self.gym()
                        return

                    # Random event logic
                    chance = random.randint(1, 6)
                    if chance in [1, 2]:
                        print("You found nothing.")
                    elif chance in [3, 4]:
                        print("You encountered a wild Pokémon!")
                        self.fight()
                    else:
                        item = random.choice(self._shopItems)
                        print("You found an item!")
                        print(f"You found a {item[0]}!")
                        if item[0] in self._inventory:
                            self._inventory[item[0]] += 1
                        else:
                            self._inventory[item[0]] = 1

            # Small delay for user experience
            time.sleep(2)
            self.options()


        def homeOptions(self):
            # Print available options for the player at home
            print("----------------------------")
            for option in self._homeOptions:
                print(option.upper())  # Display each option for home activities
            print("----------------------------")
            return

        
        def home(self):
            self.board.movePlayer("", True)
            self.homeOptions()  # Print home-related options
            # Allow the player to choose an action
            option = input("What do you want to do? ")
            if option.lower() == "heal your pokemon" or option.lower() == "heal":
                self.heal()  # Heal all Pokémon if the player chooses to heal
            elif option.lower() == "store":
                self.store()  # Open the store to buy items
            elif option.lower() == "pokemon":
                self.pokemon(self.home)  # Show the player's Pokémon list
            elif option.lower() == "bag":
                self.bag(self.home)  # Show the player's inventory
            elif option.lower() == "box":
                self.box()
            elif option.lower() == "back":
                self.options()  # Go back to the main options screen
            else:
                # Reprint options if the input is invalid
                self.home()

        def heal(self):
            # Heal all the Pokémon in the player's list
            for pokemon in self._pokemonClassList:
                pokemon.heal_doctor()  # Call the heal_doctor method from the Pokémon class
            print("Your pokemon(s) have been healed")  # Print message when healing is complete
            time.sleep(2)
            self.home()  # Return to the home options

        def printItems(self):
            # Print the available items in the shop with their cost and description, using a numbered list
            print("---------------------------------------------------------------------------")
            print("No.\tItem\t\tCost\t\tDescription")
            print("---------------------------------------------------------------------------")
            for idx, option in enumerate(self._shopItems, 1):
                print(f"{idx:<3}\t{option[0].upper():<15}{option[1]:<10}{option[2].capitalize()}")
            print("---------------------------------------------------------------------------")
            return

        def store(self):
            # Handle item purchase in the store using the numbered system
            valid = False
            while not valid:
                time.sleep(5)
                self.printItems()  # Display available items
                print(f"You have {self._money} pokedollars")  # Show player’s remaining money

                try:
                    choice = int(input("Select an item to buy by number: ")) - 1  # Adjust for 0-based index
                    if 0 <= choice < len(self._shopItems):
                        selected_item = self._shopItems[choice]
                        item_name, item_cost, _ = selected_item
                        item_cost = int(item_cost)  # Convert cost to integer for calculation

                        count = int(input(f"How many {item_name.upper()}(s) would you like to buy? "))
                        total_cost = item_cost * count

                        if self._money < total_cost:
                            print("You do not have enough money.")  # Handle insufficient funds
                            continue

                        # Process purchase
                        print(f"You bought {count} {item_name.upper()}(s) for {total_cost} pokedollars.")
                        self._money -= total_cost  # Deduct the cost from the player's money
                        print(f"You have {self._money} pokedollars left.")

                        # Update inventory
                        if item_name not in self._inventory:
                            self._inventory[item_name] = 0
                        self._inventory[item_name] += count
                        time.sleep(3)
                        # Ask if they want to buy more
                        more = input("Would you like to buy anything else (y/n)? ").lower()
                        if more == "y":
                            continue
                        else:
                            valid = True  # Exit the loop if the player is done shopping
                    else:
                        print("Invalid selection. Please choose a valid item number.")
                except (ValueError, IndexError):
                    print("Invalid input. Please enter a valid item number.")
            time.sleep(2)
            self.home()  # Return to home options when done shopping


        def fight(self):
            with open("pokemonNames.txt", "r") as pokemonNames:
                pokemonList = []
                for line in pokemonNames:
                    line = line.strip("\n")
                    pokemonList.append(line)

            otherpoke = pokemonList[random.randint(1, len(pokemonList)-1)]
            print("You heard a pokemon in the grass!")
            all_data = card.get_all_hero_data(otherpoke)
            other = card.create_card(all_data, pokemonList)
            self._other = myPokemon.Pokemon(other)
            self._other.setEvolveLevel((self._other._trueLevel+10))
            #self._fight = battle.Counter(self._pokemonList[0], self._other)
            self._pokemon = self._pokemonClassList[0]
            self.fightOptions()

        def printBattleOptions(self):
            # Print available options for the player
            print("----------------------------")
            for option in self._battleOptions:
                print(option.upper())  # Display each option in the option list
            print("----------------------------")
            return

        def fightOptions(self, trainer = False):
            print("\n")
            if trainer:
                print("Trainer items:")
                if len(self._trainer._heals)>0:
                    for heal in self._trainer._heals:
                        print(f"  - {heal}")
                else:
                    print("  The trainer has no more heals")
            
            self._pokemon = self._pokemonClassList[0]  # Always ensure the first Pokémon is selected
            count = 0
            if self._pokemon._fainted:
                for pokemon in self._pokemonClassList:
                    if pokemon._fainted:
                        count += 1
                    else:
                        if trainer:
                            self.pokemonSwitch(True, True)
                        else:
                            self.pokemonSwitch(True)
                        print(f"You sent out {self._pokemon._name.upper()}")
                        self._pokemon.printData(False)
                        break

            if count == len(self._pokemonClassList):
                if trainer:
                    print("You lost the battle")
                    owe = 8 * self._pokemon._trueLevel
                    owe = min(owe, 12000)
                    print(f"You owe {owe} pokedollars")
                    self._money -= owe
                    if self._money <= 0:
                        self._money = 0

                print("You whited out")
                self.board.movePlayer("", True)
                for pokemon in self._pokemonClassList:
                    pokemon.heal_doctor()
                self.home()

            if not trainer:
                if self._other.isFainted():
                    self._pokemon = self._pokemonClassList[0]  # Ensure first Pokémon levels up
                    evolve, name = self._pokemon.level_up(self._other._trueLevel)
                    reward = 50 + (self._other._trueLevel * 10)
                    reward = min(reward, 10000)
                    print(f"You got {reward} pokedollars!")
                    self._money += reward

                    if evolve:
                        poke = self._pokemon
                        indexPoke = self._pokemonList.index(poke._name.upper())
                        self._pokemonList.remove(poke._name.upper())
                        level = poke._level
                        data = card.get_all_hero_data(name.lower())  # Retrieve Pokémon data
                        self._pokemonCreated = card.get_card_from_pokemon(data)  # Create a card for the evolved Pokémon
                        new_pokemon = myPokemon.Pokemon(self._pokemonCreated, level + 10)  # Update Pokémon's evolution level
                        new_pokemon.setLevel(poke._level)
                        self._pokemonList.insert(indexPoke, name.upper())
                        self._pokemonClassList[self._pokemonClassList.index(poke)] = new_pokemon  # Replace the first Pokémon with the evolved Pokémon
                        new_pokemon._hp = poke._hp
                    self.options()

                time.sleep(2)
                self._other.printData(True)
                time.sleep(2)
                self._pokemon.printData(False)
            else:
                if not self._trainer._faintedPokemon == None:
                    self._pokemon = self._pokemonClassList[0]  # Ensure first Pokémon levels up
                    evolve, name = self._pokemon.level_up(self._trainer._pokemon._trueLevel)
                    if evolve:
                        poke = self._pokemon
                        indexPoke = self._pokemonList.index(poke._name.upper())
                        self._pokemonList.remove(poke._name.upper())
                        level = poke._level
                        data = card.get_all_hero_data(name.lower())  # Retrieve Pokémon data
                        self._pokemonCreated = card.get_card_from_pokemon(data)  # Create a card for the evolved Pokémon
                        new_pokemon = myPokemon.Pokemon(self._pokemonCreated, level + 10)  # Update Pokémon's evolution level
                        new_pokemon.setLevel(poke._level)
                        self._pokemonList.insert(indexPoke, name.upper())
                        self._pokemonClassList[self._pokemonClassList.index(poke)] = new_pokemon  # Replace the first Pokémon with the evolved Pokémon
                        self._trainer.setNewPokemon(new_pokemon)
                        new_pokemon._hp = poke._hp
                    self._trainer.attack()

                if self._trainer.isWhited():
                    print("The trainer has been defeated")
                    reward = random.randint(20, 99) * self._trainer._pokemon._trueLevel * 3
                    reward = min(reward, 25000)
                    print(f"You got {reward} pokedollars!")
                    self._money += reward
                    self.options()
                time.sleep(2)
                self._trainer._pokemon.printData(True)
                time.sleep(2)
                self._pokemon.printData(False)
                
            if trainer:
                # Allow the player to choose an action
                self.printBattleOptions()
                option = input("What do you want to do? ")
                if option.lower() == "battle":
                    self.battle(True)  # Call the move function
                elif option.lower() == "pokemon":
                    self.pokemon(self.fightOptions, True, True)  # Call the bag function
                elif option.lower() == "bag":
                    self.battleBag(True)  # Call the pokemon function
                elif option.lower() == "run":
                    self.run(True)  # Call the home function
                else:
                    # Reprint options if the input is invalid
                    self.fightOptions(trainer)
            else:
                # Allow the player to choose an action
                self.printBattleOptions()
                option = input("What do you want to do? ")
                if option.lower() == "battle":
                    self.battle()  # Call the move function
                elif option.lower() == "pokemon":
                    self.pokemon(self.fightOptions, True, False)  # Call the bag function
                elif option.lower() == "bag":
                    self.battleBag()  # Call the pokemon function
                elif option.lower() == "run":
                    self.run()  # Call the home function
                else:
                    # Reprint options if the input is invalid
                    self.fightOptions()

        def battle(self, trainer=False):
            while True:
                try:
                    num_moves = len(self._pokemon._attacks)
                    if num_moves > 1:
                        attack = int(input(f"{self._pokemon._name} has {num_moves} moves. Which one do you want (1-{num_moves})? "))
                    else:
                        attack = int(input(f"{self._pokemon._name} has {num_moves} move. Which one do you want (1)? "))
                    
                    # Validate attack selection
                    if 1 <= attack <= num_moves:
                        break  # Exit loop if the input is valid
                    else:
                        print(f"Invalid choice. Please choose a number between 1 and {num_moves}.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
            
            chance = random.randint(1,3) == 1
            if chance:
                if trainer:
                    print(f"{self._trainer._pokemon._name.upper()} outsped")
                    self._trainer.attack()
                    print("\n")
                    # Execute the selected attack
                    if not self._pokemon.attack(attack, self._trainer._pokemon):
                        self.battle(trainer)
                else:
                    print(f"{self._other._name.upper()} outsped")
                    # Opponent attacks
                    self._other.attack(random.randint(1, len(self._other._attacks)), self._pokemon)
                    print("\n")
                    # Execute the selected attack
                    if not self._pokemon.attack(attack, self._other):
                        self.battle(trainer)       
            else:
                if trainer:
                    # Execute the selected attack
                    if not self._pokemon.attack(attack, self._trainer._pokemon):
                        self.battle(trainer)
                    print("\n")
                    self._trainer.attack()   
                else:
                    # Execute the selected attack
                    if not self._pokemon.attack(attack, self._other):
                        self.battle(trainer)
                    print("\n")
                    # Opponent attacks
                    self._other.attack(random.randint(1, len(self._other._attacks)), self._pokemon) 

            # Update turn states
            self._pokemon.turnOver()
            if trainer:
                self._trainer._pokemon.turnOver()
            else:
                self._other.turnOver()
            time.sleep(6)
            # Return to fight options
            self.fightOptions(trainer)

        def showBag(self):
            # Display inventory items and quantities in a numbered list
            print("----------------------------")
            print("Your Inventory:")
            for idx, (item, quantity) in enumerate(self._inventory.items(), 1):
                print(f"{idx}. {item.upper()} (x{quantity})")  # Show item number, name, and quantity
            print("----------------------------")
            return


        def battleBag(self, trainer=False):
            self.showBag()
            sure = input("Do you want to use an item (y/n)? ")
            if sure.lower() == "y":
                valid = False
                while not valid:
                    try:
                        choice = int(input("Select an item by number: ")) - 1  # Adjust for 0-based index
                        if 0 <= choice < len(self._inventory):
                            item = list(self._inventory.keys())[choice]
                            if item == "rare candy":
                                self.useCandy(trainer)
                                valid = True
                                if trainer:
                                    self._trainer.attack()
                                else:
                                    self._other.attack(random.randint(1, len(self._other._attacks)), self._pokemon)

                                self._pokemon.turnOver()
                                if trainer:
                                    self._trainer._pokemon.turnOver()
                                else:
                                    self._other.turnOver()
                                time.sleep(3)
                                self.fightOptions(trainer)
                            if item == "pp up":
                                self.resetPP()
                                valid = True
                                if trainer:
                                    self._trainer.attack()
                                else:
                                    self._other.attack(random.randint(1, len(self._other._attacks)), self._pokemon)

                                self._pokemon.turnOver()
                                if trainer:
                                    self._trainer._pokemon.turnOver()
                                else:
                                    self._other.turnOver()
                                time.sleep(3)
                                self.fightOptions(trainer)
                            if trainer:
                                if item in ["pokeball", "great ball", "ultra ball"]:
                                    print("You cannot use those in a trainer battle")
                                    self.battleBag(trainer)
                            if self._inventory[item] > 0:
                                # Use the item
                                self._inventory[item] -= 1
                                if self._inventory[item] == 0:
                                    print(f"You ran out of {item.upper()}s")
                                    del self._inventory[item]
                                
                                message = self.useItem(item)
                                if message:
                                    print(f"You used a(n) {item.upper()}")
                                valid = True
                            else:
                                print(f"You do not have any {item.upper()}s left.")
                        else:
                            print("Invalid selection. Please select a valid number.")
                    except (ValueError, IndexError):
                        print("Invalid input. Please enter a valid number.")

                # Process turn mechanics
                if trainer:
                    self._trainer.attack()
                else:
                    self._other.attack(random.randint(1, len(self._other._attacks)), self._pokemon)

                self._pokemon.turnOver()
                if trainer:
                    self._trainer._pokemon.turnOver()
                else:
                    self._other.turnOver()
            time.sleep(3)
            self.fightOptions(trainer)


        def useItem(self, item):
            if item == "pokeball":
                self.useBall(self._other, self._other._baseCatchRate, 1)
                return False
            elif item == "great ball":
                self.useBall(self._other, self._other._baseCatchRate, 1.5)
                return False
            elif item == "ultra ball":
                self.useBall(self._other, self._other._baseCatchRate, 2)
                return False

            print("----------------------------")
            self.printPokemon()  # Print the list of Pokémon
            print("----------------------------")
            valid = False
            while not valid:
                try:
                    choice = int(input(f"Enter the number of the Pokémon you want to use the {item.upper()} on: ")) - 1  # Adjust for 0-based index
                    
                    if 0 <= choice < len(self._pokemonClassList):
                        poke = self._pokemonClassList[choice]
                        valid = True  # Exit the loop once valid selection is made
                    else:
                        print(f"Invalid choice. Please select a number between 1 and {len(self._pokemonClassList)}.")
                except ValueError:
                    print("Invalid input. Please enter a valid number.")

            pokemon = poke

            if item in self._healing_items:
                self._healing_items[item](pokemon)
            elif item in self._status_items:
                self._status_items[item](pokemon)

            return True
        
        def printPokemonLevel(self):
            for idx, poke in enumerate(self._pokemonClassList, start=1):
                print(f"{idx}. {poke._name}")
                if len(poke._evolve)>0:
                    print(f"  - Level: {poke._level}")
                    print(f"  - Evolve Level: {poke._evolvelevel}")
                else:
                    print(Fore.RED + f"  {poke._name} cannot evolve" + Fore.RESET)

        def resetPP(self):
            print("----------------------------")
            self.printPokemon()  # Print the list of Pokémon
            print("----------------------------")
            valid = False
            while not valid:
                try:
                    choice = int(input(f"Enter the number of the Pokémon you want to use the PP Up on: ")) - 1  # Adjust for 0-based index
                    
                    if 0 <= choice < len(self._pokemonClassList):
                        pokemon = self._pokemonClassList[choice]
                        valid = True  # Exit the loop once valid selection is made
                    else:
                        print(f"Invalid choice. Please select a number between 1 and {len(self._pokemonClassList)}.")
                except ValueError:
                    print("Invalid input. Please enter a valid number.")

            
            while True:
                try:
                    num_moves = len(pokemon._attacks)
                    if num_moves > 1:
                        attack = int(input(f"{pokemon._name} has {num_moves} moves. Which one do you want (1-{num_moves})? "))
                    else:
                        attack = int(input(f"{pokemon._name} has {num_moves} move. Which one do you want (1)? "))
                    
                    # Validate attack selection
                    if 1 <= attack <= num_moves:
                        break  # Exit loop if the input is valid
                    else:
                        print(f"Invalid choice. Please choose a number between 1 and {num_moves}.")
                except ValueError:
                    print("Invalid input. Please enter a number.")

            pokemon.reset_pp(attack)
            return
            

        def useCandy(self, trainer=False):
            print("----------------------------")
            self.printPokemonLevel()  # Print the list of Pokémon
            print("----------------------------")
            valid = False
            while not valid:
                try:
                    choice = int(input(f"Enter the number of the Pokémon you want to use the rare candy on: ")) - 1  # Adjust for 0-based index
                    
                    if 0 <= choice < len(self._pokemonClassList):
                        poke = self._pokemonClassList[choice]
                        valid = True  # Exit the loop once valid selection is made
                    else:
                        print(f"Invalid choice. Please select a number between 1 and {len(self._pokemonClassList)}.")
                except ValueError:
                    print("Invalid input. Please enter a valid number.")

            valid = False
            while not valid:
                try:
                    count = int(input("How many rare candies would you like to use? "))
                except:
                    print("Invalid input. Please enter a valid number.")

                if self._inventory["rare candy"]-count<0:
                    print("You do not have enough rare candies")
                else:
                    self._inventory["rare candy"]-=count
                    print(f"You used {count} rare candies")
                    if self._inventory["rare candy"] == 0:
                        del self._inventory["rare candy"]
                    valid = True
            
            evolve, name =  poke.level_up(20*count)
            if evolve:
                indexPoke = self._pokemonList.index(poke._name.upper())
                self._pokemonList.remove(poke._name.upper())
                level = poke._level
                hp = poke._hp
                data = card.get_all_hero_data(name.lower())  # Retrieve Pokémon data
                self._pokemonCreated = card.get_card_from_pokemon(data)  # Create a card for the evolved Pokémon
                new_pokemon = myPokemon.Pokemon(self._pokemonCreated, level + 10)  # Update Pokémon's evolution level
                new_pokemon.setLevel(poke._level)
                self._pokemonList.insert(indexPoke, name.upper())
                self._pokemonClassList[self._pokemonClassList.index(poke)] = new_pokemon  # Replace the first Pokémon with the evolved Pokémon
                new_pokemon._hp = hp
                if trainer:
                    if self._pokemonClassList[0] == new_pokemon:
                        self._trainer.setNewPokemon()
            return


        def useBall(self, pokemon, catchRate, ballModifier):
            catchProb = int(self.calculate_catch_rate(pokemon, catchRate, ballModifier))
            catchProb = max(0, min(100, catchProb))
            print("You threw a ball")
            print(f"You have a {catchProb}% chance of catching {self._other._name}")
            chance = self.check_chance(catchProb)
            if chance:
                print("It shakes once...")
                print("It shakes twice...")
                print("It shakes three times...")
                print(f"{self._other._name} was caught")
                if len(self._pokemonClassList) == 6:
                    print(f"You have too many pokemon in your lineup")
                    print(f"{self._other._name} was put in the box")
                    self._box.append(self._other)
                    self._boxNames.append(self._other._name.upper())
                else:
                    self._pokemonClassList.append(self._other)
                    self._pokemonList.append(self._other._name.upper())

                reward = 50 + (self._other._trueLevel * 10)
                reward = min(reward, 10000)
                self._money += reward
                print(f"You got {reward} pokedollars!")

                evolve, name = self._pokemon.level_up(self._other._trueLevel)
                if evolve:
                    self._pokemonList.remove(self._pokemon._name.upper())
                    self._pokemonList.insert(0, name.upper())
                    data = card.get_all_hero_data(name.lower())  # Retrieve Pokémon data
                    self._pokemonCreated = card.get_card_from_pokemon(data)  # Create a card for the evolved Pokémon
                    new_pokemon = myPokemon.Pokemon(self._pokemonCreated, self._pokemon._evolvelevel + 10)  # Update Pokémon's evolution level
                    self._pokemonClassList[0] = new_pokemon  # Replace the first Pokémon with the evolved Pokémon
                    self._pokemonClassList[0].setLevel(self._pokemon._level)
                    new_pokemon._hp = self._pokemon._hp

                self._pokemon = self._pokemonClassList[0]
                time.sleep(3)
                self.options()
            else:
                message = random.randint(1, 6)
                if message in [1, 2]:
                    print("It broke out!")
                if message in [3, 4]:
                    print("It shakes once...")
                    print("It broke out!")
                if message == 5:
                    print("It shakes once...")
                    print("It shakes twice...")
                    print("It broke out!")
                if message == 6:
                    print("It shakes once...")
                    print("It shakes twice...")
                    print("It shakes three times...")
                    print("It broke out!")

                self._other.attack(random.randint(1, len(self._other._attacks)), self._pokemon)
                self._pokemon.turnOver()
                self._other.turnOver()
                time.sleep(3)
                self.fightOptions()
        
        def calculate_catch_rate(self, pokemon, base_catch_rate, ball_bonus=1.0):
            """
            Calculate the catch probability for a Pokémon using attributes from the Pokémon class.

            Parameters:
            - pokemon (Pokemon): An instance of the Pokémon class.
            - base_catch_rate (int): The base catch rate of the Pokémon.
            - ball_bonus (float): Modifier for the Poké Ball used (default: 1.0).

            Returns:
            - probability (float): Approximate catch probability as a percentage.
            """
            # Status bonus
            status_bonus = 1.0
            if pokemon._paralyzed or pokemon._sleep or pokemon._freeze:
                status_bonus = 1.5
            elif pokemon._poisoned or pokemon._burn:
                status_bonus = 1.2

            # Exponential level factor: lower levels easier to catch, higher levels harder
            level_factor = 100 - (98 * ((pokemon._trueLevel - 1) / 74) ** 2)

            # Current HP and Max HP from the Pokémon instance
            current_hp = pokemon._hp
            max_hp = pokemon._fullhp

            # Calculate the modified catch rate
            modified_catch_rate = (
                ((3 * max_hp - 2 * current_hp) / (3 * max_hp)) * base_catch_rate * ball_bonus * status_bonus * level_factor / 100
            )

            # Calculate the approximate catch probability
            catch_probability = (modified_catch_rate / 255)

            catch_probability = catch_probability * 100
            if int(catch_probability) > 75:
                catch_probability = catch_probability/2
            if pokemon._hp<20:
                catch_probability = catch_probability*2
            
            return catch_probability # Return as a percentage
      
        def check_chance(self, percentage):
            """
            Checks if an event occurs based on a given percentage chance.

            :param percentage: The percentage chance (0-100) of the event happening.
            :return: True if the event occurs, False otherwise.
            """
            if not 0 <= percentage <= 100:
                raise ValueError("Percentage must be between 0 and 100.")

            # Generate a random number between 0 and 100
            random_value = random.uniform(0, 100)
            return random_value < percentage

        def run(self, trainer = False):
            firstTurn = random.randint(1, 5) == 1
            if not trainer:
                if firstTurn:
                    self._other.attack(random.randint(1, len(self._other._attacks)), self._pokemon)
                    self._other.turnOver()
                    count = 0
                    for pokemon in self._pokemonClassList:
                        if pokemon._fainted:
                            count += 1
                    if count == len(self._pokemonClassList):
                        print("You whited out")
                        for pokemon in self._pokemonClassList:
                            pokemon.heal_doctor()
                        self.home()
                    
                # Simulate a chance to run away from a battle
                chance = random.randint(1, 5)
                if chance == 1:
                    print("You could not run away")  # Print message if running away fails
                    if not firstTurn:
                        self._other.attack(random.randint(1, len(self._other._attacks)), self._pokemon)
                        self._other.turnOver()
                    time.sleep(3)
                    self.fightOptions(trainer)
                else:
                    print("You ran away")  # Print message if running away succeeds
                    self.options()
            else:
                print("You are in a trainer battle")
                print("You cannot run away")
                time.sleep(2)
                self.fightOptions(trainer)

        def trainer(self, length):
            time.sleep(2)
            trainerPokemon = []
            healingItems = []
            amountItems = random.randint(2,4)
            for i in range(amountItems):
                item = random.choice(self._shopItems)[0]
                if item not in ["pokeball", "great ball", "ultra ball", "rare candy"]:
                    healingItems.append(item)
            for i in range(length):
                all_data = card.get_all_hero_data(random.choice(pokemonList))
                other = card.create_card_trainer(all_data, pokemonList)
                self._other = myPokemon.Pokemon(other)
                self._other.setEvolveLevel((self._other._trueLevel+10))
                trainerPokemon.append(self._other)
            
            self._otherPokemon = trainerPokemon[0]
            for pokemon in self._pokemonClassList:
                pokemon.heal_doctor()

            print("Your pokemon have been healed")
            
            print(f"Your opponent has {length} pokemon")
            print(f"You have {len(self._pokemonClassList)} pokemon")

            time.sleep(2)
            print(f"Your opponent sent out {self._otherPokemon._name}")
            print(f"You sent out {self._pokemon._name}")
            time.sleep(2)

            self._trainer = trainerBattle.Trainer(trainerPokemon, self._otherPokemon, self._pokemon, healingItems, self._status_items, self._healing_items)
            self.fightOptions(True)

        def gym(self):
            time.sleep(2)
            trainerPokemon = []
            healingItems = []
            count=random.randint(4,6)
            for i in range(count):
                item = random.choice(self._shopItems)[0]
                if item not in ["pokeball", "great ball", "ultra ball", "rare candy"]:
                    healingItems.append(item)
                    count-=1
            for i in range(6):
                all_data = card.get_all_hero_data(random.choice(pokemonList))
                other = card.create_card_trainer(all_data, pokemonList)
                self._other = myPokemon.Pokemon(other)
                self._other.setEvolveLevel((self._other._trueLevel+10))
                trainerPokemon.append(self._other)
            
            self._otherPokemon = trainerPokemon[0]
            for pokemon in self._pokemonClassList:
                pokemon.heal_doctor()

            print("Your pokemon have been healed")
            
            print(f"Your opponent has 6 pokemon")
            print(f"You have {len(self._pokemonClassList)} pokemon")

            time.sleep(2)
            print(f"Your opponent sent out {self._otherPokemon._name}")
            print(f"You sent out {self._pokemon._name}")
            time.sleep(2)

            self._trainer = trainerBattle.Trainer(trainerPokemon, self._otherPokemon, self._pokemon, healingItems, self._status_items, self._healing_items)
            self.fightOptions(True)

        # def trainerOptions(self):
            

        def bag(self, func):
            # Display inventory items and quantities
            self.showBag()
            time.sleep(2)
            sure = input("Do you want to use an item (y/n)? ")
            if sure.lower() == "y":
                valid = False
                while not valid:
                    try:
                        choice = int(input("Select an item by number: ")) - 1  # Adjust for 0-based index
                        if 0 <= choice < len(self._inventory):
                            item = list(self._inventory.keys())[choice]
                            if item == "rare candy":
                                self.useCandy()
                                valid = True
                                func()
                            if item == "pp up":
                                self.resetPP()
                                valid = True
                                func()
                            if item in ["pokeball", "great ball", "ultra ball"]:
                                print("You cannot use those")
                                continue
                            if self._inventory[item] > 0:
                                # Use the item
                                self._inventory[item] -= 1
                                if self._inventory[item] == 0:
                                    print(f"You ran out of {item.upper()}s")
                                    del self._inventory[item]
                                
                                message = self.useItem(item)
                                if message:
                                    print(f"You used a(n) {item.upper()}")
                                valid = True
                            else:
                                print(f"You do not have any {item.upper()}s left.")
                        else:
                            print("Invalid selection. Please select a valid number.")
                    except (ValueError, IndexError):
                        print("Invalid input. Please enter a valid number.")

            func()  # Call the provided function as a callback

        def getPokemon(self):
            # Let the player choose a starting Pokémon
            valid = False
            pokeList = ["PIKACHU", "CHARMANDER", "BULBASAUR", "SQUIRTLE"]
            color = [Fore.YELLOW, Fore.RED, Fore.GREEN, Fore.BLUE]
            type = ["Electric Type", "Fire Type", "Grass Type", "Water Type"]
            while not valid:
                print("----------------------------------")
                for idx, poke in enumerate(pokeList, start=1):
                    print(f"{idx}. {Style.BRIGHT + color[idx-1] + poke + Style.RESET_ALL}")  # Display Pokémon name with its position number
                    print(f"  - {Style.BRIGHT + color[idx-1] + type[idx-1] + Style.RESET_ALL}")
                print("----------------------------------")
                time.sleep(1)    
                print("Which pokemon do you want? ")
                try:
                    pokemon = int(input("Enter a number: "))
                except:
                    print("Invalid input. Please enter a valid number.")
                    time.sleep(1)
                    continue
                if pokemon in [1,2,3,4]:
                    poke = pokeList[pokemon-1]
                    # poke = "Charizard"
                    print(f"You chose {color[pokemon-1] + poke}")
                    self._pokemonList.append(poke.upper())  # Add chosen Pokémon to the list
                    valid = True  # Exit the loop when a valid choice is made
                else:
                    print("Sorry I do not have that. Pick something else.")  # Invalid choice message
                    time.sleep(2)
            print(Style.RESET_ALL)
            # Get Pokémon data using the `card` module
            data = card.get_all_hero_data(poke.lower())  # Retrieve Pokémon data
            self._pokemonCreated = card.get_card_from_pokemon(data)  # Create a card for the chosen Pokémon
            pokemon = myPokemon.Pokemon(self._pokemonCreated)  # Create a Pokémon object
            self._pokemonClassList.append(pokemon)  # Add the Pokémon object to the player's list
            self._pokemon = self._pokemonClassList[0]
            return

        def pokemon(self, func, inBattle=False, trainer=False):
            """
            Allow the player to either view info or switch the Pokémon in the first position based on number selection.
            """
            time.sleep(2)
            valid = False
            print("----------------------------")
            self.printPokemon()  # Print the list of Pokémon
            print("----------------------------")
            
            while not valid:
                try:
                    # Ask the player to choose between getting info (1) or switching (2)
                    action_choice = int(input("Enter 1 to get Pokémon info, or 2 to switch Pokémon to the first position: "))
                    
                    if action_choice == 1:
                        # Get detailed info about a Pokémon
                        self.pokemonInfo()
                        valid = True  # Exit the loop once info is viewed
                        
                    elif action_choice == 2:
                        if len(self._pokemonClassList)>0:
                            # Switch the Pokémon to the first position
                            if inBattle:
                                chance = random.randint(1, 5) == 1
                                if chance:
                                    if trainer:
                                        self._trainer.attack()
                                    else:
                                        self._other.attack(random.randint(1, len(self._other._attacks)), self._pokemon)
                                    if trainer:
                                        self.pokemonSwitch(False, trainer)
                                    else:
                                        self.pokemonSwitch(True)
                                else:
                                    if trainer:
                                        self.pokemonSwitch(False, trainer)
                                    else:
                                        self.pokemonSwitch(True)
                                    if trainer:
                                        self._trainer.attack()
                                    else:
                                        self._other.attack(random.randint(1, len(self._other._attacks)), self._pokemon)
                            else:
                                self.pokemonSwitch()
                            valid = True  # Exit the loop once switch is done
                        else:
                            print("You only have one pokemon")
                        
                    else:
                        print("Invalid choice. Please enter 1 to get info or 2 to switch Pokémon.")
                
                except ValueError:
                    print("Invalid input. Please enter a valid number.")
            func()

        def pokemonInfo(self):
            """
            Display detailed info about a chosen Pokémon
            """
            valid = False
            print("----------------------------")
            self.printPokemon()  # Print the list of Pokémon
            print("----------------------------")
            
            while not valid:
                try:
                    choice = int(input("Enter the number of the Pokémon you want to get more info on: ")) - 1  # Adjust for 0-based index
                    
                    if 0 <= choice < len(self._pokemonClassList):
                        self._pokemonClassList[choice].printData(False)  # Show detailed info about the chosen Pokémon
                        valid = True  # Exit the loop once valid selection is made
                    else:
                        print(f"Invalid choice. Please select a number between 1 and {len(self._pokemonClassList)}.")
                except ValueError:
                    print("Invalid input. Please enter a valid number.")
            time.sleep(2)
            return

        def pokemonSwitch(self, fainted=False, trainer=False):
            """
            Switch the Pokémon in the first position of the party using a number-based selection.
            """
            valid = False
            print("----------------------------")
            self.printPokemon()  # Print the list of Pokémon
            print("----------------------------")

            while not valid:
                try:
                    choice = int(input("Enter the number of the Pokémon you want to switch to the first position: ")) - 1  # Adjust for 0-based index
                    
                    if 0 <= choice < len(self._pokemonClassList):
                        if self._pokemonClassList[choice].isFainted():
                            print("You cannot switch in a fainted pokemon")
                        else:
                            # Move the selected Pokémon to the first position
                            poke = self._pokemonClassList.pop(choice)
                            pokemon_name = self._pokemonList.pop(choice)
                            self._pokemonClassList.insert(0, poke)
                            self._pokemonList.insert(0, pokemon_name)
                            self._pokemon = self._pokemonClassList[0]  # Set the selected Pokémon as the first position
                            valid = True  # Exit the loop when a valid choice is made
                            time.sleep(2)
                            if trainer:
                                self._trainer.setNewPokemon(self._pokemon)
                                self.fightOptions(trainer)
                            elif fainted:
                                self.fightOptions()
                    else:
                        print(f"Invalid choice. Please select a number between 1 and {len(self._pokemonClassList)}.")
                except ValueError:
                    print("Invalid input. Please enter a valid number.")
            return

        def printPokemon(self):
            """
            Print the list of Pokémon owned by the player with numbers.
            """
            for idx, poke in enumerate(self._pokemonClassList, start=1):
                print(f"{idx}. {poke._name}")  # Display Pokémon name with its position number
       
        def printBox(self):
            """
            Print the list of Pokémon owned by the player with numbers.
            """
            for idx, poke in enumerate(self._box, start=1):
                print(f"{idx}. {poke._name}")  # Display Pokémon name with its position number
        
        def box(self):
            if len(self._box) == 0:
                print("Your box is empty")
            else:
                valid = False
                print("----------------------------")
                self.printPokemon()  # Print the list of Pokémon
                print("----------------------------")
                print("----------------------------")
                self.printBox()  # Print the list of Pokémon
                print("----------------------------")

                while not valid:
                    try:
                        choice = int(input("Enter the number of the Pokémon from your lineup: ")) - 1  # Adjust for 0-based index
                        
                        if 0 <= choice < len(self._pokemonClassList):
                            poke = self._pokemonClassList.pop(choice)
                            pokemon_name = self._pokemonList.pop(choice)
                            valid = True  # Exit the loop when a valid choice is made
                        else:
                            print(f"Invalid choice. Please select a number between 1 and {len(self._pokemonClassList)}.")
                    except ValueError:
                        print("Invalid input. Please enter a valid number.")

                valid = False
                while not valid:
                    try:
                        choiceBox = int(input("Enter the number of the Pokémon from your box: ")) - 1  # Adjust for 0-based index
                        
                        if 0 <= choiceBox < len(self._box):
                            pokeBox = self._box.pop(choiceBox)
                            pokemon_name_box = self._boxNames.pop(choiceBox)
                            valid = True  # Exit the loop when a valid choice is made
                        else:
                            print(f"Invalid choice. Please select a number between 1 and {len(self._box)}.")
                    except ValueError:
                        print("Invalid input. Please enter a valid number.")

                print(f"You put {pokemon_name.upper()} in the box")
                print(f"{pokemon_name_box.upper()} joined your lineup")

                self._pokemonClassList.insert(choice, pokeBox)
                self._pokemonList.insert(choice, pokemon_name_box)

                self._box.insert(choice, poke)
                self._boxNames.insert(choice, pokemon_name)

            time.sleep(2)
            self.home()  # Call the provided function as a callback

    # Main game initialization
    with open("pokemonNames.txt", "r") as pokemonNames:
        pokemonList = []
        for line in pokemonNames:
            line = line.strip("\n")  # Remove newline characters from each line
            pokemonList.append(line)  # Add each Pokémon to the list

        root = Tk()
        root.title('POKEMON MAP')
        board = gameBoard.Board(root, 20, 20)
        player = Player(board)  # Create a Player object
        player.options() # Start the player's interactions with the game
        root.mainloop()
        
        # player.fight()  

    # # player = Player()  # Create a Player object
    # # player.battleBag()

    # # Main game initialization
    # with open("pokemonNames.txt", "r") as pokemonNames:
    #     pokemonList = []
    #     for line in pokemonNames:
    #         line = line.strip("\n")  # Remove newline characters from each line
    #         pokemonList.append(line)
    #     player = Player()  # Create a Player object
    #     player.options()  # Start the player's interactions

# money for defeating pokemon higher based on level
