import random
from colorama import Fore, Back, Style

class Trainer:
    def __init__(self, pokemonList, myPokemon, other, heals, statusheals, heal):
        self._pokemonList = pokemonList
        self._pokemon = pokemonList[0]
        self._other = other
        self._heals = heals
        self._statusheals = statusheals
        self._healingitems = heal
        self._switchPokemon = None
        self._whited = False
        self._faintedPokemon = None

    def setNewPokemon(self, pokemon):
        """Set the opposing Pokémon."""
        self._other = pokemon

    def switch_to_valid_pokemon(self):
        """Switch to a valid (non-fainted) Pokémon if possible."""
        for pokemon in self._pokemonList:
            if not pokemon.isFainted() and pokemon != self._pokemon:
                self._pokemonList.insert(0, pokemon)
                self._pokemon = pokemon
                print(f"The trainer switched to {self._pokemon._name}")
                self._faintedPokemon = None
                return True
        return False

    def heal(self, force_healing=False, revive=False):
        """Heal the current Pokémon or revive a fainted one if necessary."""
        if len(self._heals) == 0:
            return False
        
        if force_healing:
            for heal_item in self._heals:
                if (heal_item in list(self._healingitems.keys())) and ("revive" not in heal_item):
                    self._healingitems[heal_item](self._pokemon)
                    self._heals.remove(heal_item)
                    print(f"The trainer used a(n) {heal_item}.")
                    print(f"{self._pokemon._name} has been healed.")
                    return True
            return False
        
        if revive:
            for pokemon in self._pokemonList:
                if pokemon.isFainted():
                    for heal_item in self._heals:
                        if isinstance(heal_item, str) and (heal_item in list(self._healingitems.keys())) and ("revive" in heal_item):
                            self._healingitems[heal_item](pokemon)
                            print(f"The trainer used a(n) {heal_item}")
                            print(f"{pokemon._name} has been revived.")
                            return True
            return False

        # Check for healing based on damage estimation.
        predicted_damage = max(self._other._attacks.values())
        if self._pokemon._hp <= int(2.5 * predicted_damage):
            for heal_item in self._heals:
                if isinstance(heal_item, str) and (heal_item in list(self._healingitems.keys())) and ("revive" not in heal_item):
                    self._healingitems[heal_item](self._pokemon)
                    print(f"The trainer used a(n) {heal_item}")
                    print(f"{self._pokemon._name} has been healed.")
                    self._heals.remove(heal_item)
                    return True

        # Heal status conditions if needed.
        if any([self._pokemon._paralyzed, self._pokemon._poisoned, self._pokemon._burn, self._pokemon._freeze, self._pokemon._sleep]):
            for heal_item in self._heals:
                if isinstance(heal_item, str) and (heal_item in list(self._statusheals.keys())):
                    self._statusheals[heal_item](self._pokemon)
                    print(f"The trainer used a(n) {heal_item}")
                    print(f"{self._pokemon._name}'s status condition was healed.")
                    self._heals.remove(heal_item)
                    return True

        # Revive a fainted Pokémon if possible.
        for pokemon in self._pokemonList:
            if pokemon.isFainted():
                for heal_item in self._heals:
                    if isinstance(heal_item, str) and (heal_item in list(self._healingitems.keys())) and ("revive" in heal_item):
                        self._healingitems[heal_item](pokemon)
                        print(f"The trainer used a(n) {heal_item}")
                        print(f"{pokemon._name} has been revived.")
                        return True

        # If no action is taken, return False.
        return False
    
    def isWhited(self):
        available_pokemon = [poke for poke in self._pokemonList if not poke.isFainted()]
        if self._pokemon.isFainted():
            if not available_pokemon:
                return True
            
    def next_largest(self, max_val):
        arr = list(self._pokemon._attacks.values())
        second_largest = arr[0]
        for num in arr:
            if num > second_largest and num != max_val:
                second_largest = num
        return second_largest 

    def attack(self):
        """Perform an attack or take alternative actions if needed."""
        # Count non-fainted Pokémon.
        available_pokemon = [poke for poke in self._pokemonList if not poke.isFainted()]
        predicted_damage = max(self._other._attacks.values())
        self._faintedPokemon = None
        if self._pokemon.isFainted():
            self._faintedPokemon = self._pokemon
            # Switch to a valid Pokémon if the current one is fainted.
            if not available_pokemon:
                print("The trainer has no Pokémon left and has been defeated!")
                self._whited = True
                return
            else:
                self.switch_to_valid_pokemon()
                return
        # Determine the strongest attack.
        strongest_attack = max(self._pokemon._attacks.values())
        attack_index = list(self._pokemon._attacks.values()).index(strongest_attack) + 1
        # Check if we can faint the opponent.
        if self._other._hp <= strongest_attack:
            self._pokemon.attack(attack_index, self._other)
            return
        
        if len(available_pokemon) >= 2:
            if strongest_attack <= 12:
                self.switch_to_valid_pokemon()

        # check if the other pokemons attack is too strong
        if predicted_damage > 30:
            if self._pokemon._hp- predicted_damage <= 0:
                if not self.heal(True):
                    if not self.heal(False, True):
                        if len(available_pokemon) == 3:
                            self.switch_to_valid_pokemon()
                            return
                self._pokemon.attack(attack_index, self._other)
                return
            else:
                self._pokemon.attack(attack_index, self._other)
                return

        # Consider switching Pokémon or healing.
        if self._pokemon._hp - 1.5*predicted_damage <= 0:
            if len(available_pokemon) > 1:
                self.switch_to_valid_pokemon()
                return
            else:
                if not self.heal(True):

                    self._pokemon.attack(attack_index, self._other)
                    return

        elif self._pokemon._hp <= self._pokemon._fullhp / 3:
            if not self.heal():
                self._pokemon.attack(attack_index, self._other)
                return
        else:
            self._pokemon.attack(attack_index, self._other)
            return
