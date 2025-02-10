import random
from colorama import Fore, Back, Style

class Trainer:
    def __init__(self, pokemonList, myPokemon, other, heals, statusheals, heal):
        self._pokemonList = pokemonList
        self._pokemon = self._pokemonList[0]
        self.worst_pokemon()
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

    def switch_worst_pokemon(self):
        worst = 0
        for pokemon in self._pokemonList:
            if not pokemon.isFainted():
                attackDamage = max(pokemon._attacks.values())
                if attackDamage < worst:
                    if pokemon != self._pokemon:
                        worst = attackDamage
                        index = self._pokemonList.index(pokemon)

        self._pokemon = self._pokemonList[index]
        return True

    def switch_to_valid_pokemon(self):
        """Switch to a valid (non-fainted) Pokémon if possible."""
        if self.switch_worst_pokemon():
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
        hasStatusHeal = False
        if any([self._pokemon._paralyzed, self._pokemon._poisoned, self._pokemon._burn, self._pokemon._freeze, self._pokemon._sleep, self._pokemon._confuse]):
            for heal_item in self._heals:
                if isinstance(heal_item, str) and (heal_item in list(self._statusheals.keys())):
                    if self._pokemon._paralyzed:
                        if heal_item == "paralyze heal":
                            hasStatusHeal = True
                    elif self._pokemon._poisoned:
                        if heal_item == "antidote":
                            hasStatusHeal = True
                    elif self._pokemon._burn:
                        if heal_item == "burn heal":
                            hasStatusHeal = True
                    elif self._pokemon._freeze:
                        if heal_item == "ice heal":
                            hasStatusHeal = True
                    elif self._pokemon._sleep:
                        if heal_item == "awakening":
                            hasStatusHeal = True
                    elif self._pokemon._confuse:
                        if heal_item == "bitter berry":
                            hasStatusHeal = True
                    elif heal_item in ["full heal", "full restore"]:
                        hasStatusHeal = True

                    if hasStatusHeal:
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
            
    def worst_pokemon(self):
        worst = 0
        for pokemon in self._pokemonList:
            if not pokemon.isFainted():
                attackDamage = max(pokemon._attacks.values())
                if attackDamage < worst:
                    worst = attackDamage
                    index = self._pokemonList.index(pokemon)

        if self._pokemon == self._pokemonList[index]:
            return False
        self._pokemon = self._pokemonList[index]
        return True
            
    def next_largest(self, max_vals):
        arr = list(self._pokemon._attacks.values())
        second_largest = arr[0]
        for num in arr:
            if num > second_largest and num not in max_vals:
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
        largest = [strongest_attack]
        # Check if we can faint the opponent.
        if self._other._hp <= strongest_attack:
            valid = self._pokemon.attack(attack_index, self._other)
            while not valid:
                largest.append(self.next_largest(strongest_attack))
                attack_index = list(self._pokemon._attacks.values()).index(largest[-1]) + 1
                valid = self._pokemon.attack(attack_index, self._other)
            return

        # check if the other pokemons attack is too strong
        if predicted_damage > 30:
            if self._pokemon._hp- predicted_damage <= 0:
                if not self.heal(True):
                    if not self.heal(False, True):
                        if len(available_pokemon) <= 3:
                            self.switch_to_valid_pokemon()
                            return
            # attack if not deadly
            valid = self._pokemon.attack(attack_index, self._other)
            while not valid:
                largest.append(self.next_largest(strongest_attack))
                attack_index = list(self._pokemon._attacks.values()).index(largest[-1]) + 1
                valid = self._pokemon.attack(attack_index, self._other)
            return

        # Consider switching Pokémon or healing if damage can kill.
        if self._pokemon._hp - 1.5*predicted_damage <= 0:
            # if available pokemon is 2 or 3 and hp is low
            if 1 < len(available_pokemon) <= 3 and self._pokemon._fullhp/4 == self._hp:
                self.switch_to_valid_pokemon()
                return
            else:
                # otherwise try to heal or attack
                if not self.heal(True):
                    valid = self._pokemon.attack(attack_index, self._other)
                    while not valid:
                        largest.append(self.next_largest(strongest_attack))
                        attack_index = list(self._pokemon._attacks.values()).index(largest[-1]) + 1
                        valid = self._pokemon.attack(attack_index, self._other)
                        return

        # heal if hp is low
        elif self._pokemon._hp <= self._pokemon._fullhp / 3:
            if not self.heal():
                # attack if cannot heal
                valid = self._pokemon.attack(attack_index, self._other)
                while not valid:
                    largest.append(self.next_largest(strongest_attack))
                    attack_index = list(self._pokemon._attacks.values()).index(largest[-1]) + 1
                    valid = self._pokemon.attack(attack_index, self._other)
                return
            
        # otherwise attack
        else:
            valid = self._pokemon.attack(attack_index, self._other)
            while not valid:
                largest.append(self.next_largest(strongest_attack))
                attack_index = list(self._pokemon._attacks.values()).index(largest[-1]) + 1
                valid = self._pokemon.attack(attack_index, self._other)
            return

        return