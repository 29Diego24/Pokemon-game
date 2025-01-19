# import card
import random
from colorama import Fore, Back, Style

class Pokemon:
    def __init__(self, data, evolvelevel=20):
        # Initialize basic attributes of the Pokémon

        self._fainted = False
        self._hp = int(data['hp'])
        self._fullhp = int(data['hp'])
        self._level = 10
        self._evolvelevel = evolvelevel
        self._name = data['name']
        self._attacks = {}
        self._energy = []
        self._weaknesses = []
        self._strengths = []
        self._pp = []
        self._evolve = ""
        self._text = ""
        self._trueLevel = int(data['level'])
        # Initialize status conditions
        self._paralyzed = False
        self._poisoned = False
        self._burn = False
        self._freeze = False
        self._sleep = False
        self._stats = ["paralysis", "poison", "burn", "freeze", "sleep"]  # List of status effects

        self._critHigh = False
        self._statsUp = ["revive", "dire hit"]  # Special statuses like revive or crit boost

        self._statusCount = [0, 0, 0, 0, 0, 0]  # Counter for each status effect

        # Process attacks and energy costs from data
        for attack in data['attacks']:

            # Filter out non-numeric characters
            damage = "".join([char for char in attack['damage'] if char.isdigit()])
            
            if damage:  # Ensure damage is not empty after filtering
                self._attacks[attack['name']] = int(int(damage) * 0.4)
                powerPoints = min(int(random.randint(200, 250) / self._attacks[attack['name']]), 60)
                powerPoints = 5 * round(powerPoints / 5)
                self._pp.append(powerPoints)
            else:
                self._attacks[attack['name']] = 0  # Default to 0 damage if no valid number found
                self._pp.append(5)
            
            self._energy.append(attack["cost"])

        self._maxpp = self._pp.copy()
        
        # Handle weaknesses, resistances, evolutions, and flavor text
        if 'weaknesses' in data:
            self._weaknesses = data['weaknesses']
        if 'resistances' in data:
            self._strengths = data['resistances']
        if 'evolvesTo' in data:
            self._evolve = data['evolvesTo']
        if 'flavorText' in data:
            self._text = data['flavorText']

        value = (250 - (self._level - 1)) * (250 - 5) / 99
        self._baseCatchRate = random.randint(int(value - 5), int(value + 5))

    def setLevel(self, level):
        self._level = level
        return

    def setEvolveLevel(self, evolveLevel):
        self._evolvelevel = evolveLevel
        return

    def turnOver(self):
        stat = [self._paralyzed, self._poisoned, self._burn, self._freeze, self._sleep, self._critHigh]
        for statIndex in range(len(stat)):
            if stat[statIndex]:
                self._statusCount[statIndex] += 1
        self.effectRunOutCount()
        return
    
    def printData(self, trueLevel):
        print(Style.BRIGHT)
        """
        Prints detailed information about the Pokémon, including its name, level, HP, 
        attacks, types, evolution, and flavor text.
        """
        print("----- Pokémon Info -----")
        print(f"Name: {self._name}")
        if trueLevel:
            print(f"Level: {self._trueLevel}")
            self._level = self._trueLevel
        else:
            print(f"Level: {self._level}")
        if self._hp <= self._fullhp/4:
            print(f"HP: {Fore.RED + self._hp + Fore.RESET}/{self._fullhp}")
        if self._hp <= self._fullhp/2:
            print(f"HP: {Fore.YELLOW + self._hp + Fore.RESET}/{self._fullhp}")
        else:
            print(f"HP: {self._hp}/{self._fullhp}")
        print("Attacks:")
        for attack_name, damage in self._attacks.items():
            print(f"  - {attack_name}: {damage} damage")
            index = list(self._attacks.keys()).index(attack_name)
            if self._pp[index] <= 3:
                print(f"  PP:  {Fore.RED + str(self._pp[index]) + Fore.RESET}/{self._maxpp[index]} ")
            elif self._pp[index] <= self._maxpp[index]/2:
                print(f"  PP:  {Fore.YELLOW + str(self._pp[index]) + Fore.RESET}/{self._maxpp[index]} ")
            else:
                print(f"  PP:  {str(self._pp[index])}/{self._maxpp[index]} ")
        print("Attack Types:")
        for energy_type in self._energy:
            if "Lightning" in energy_type:
                print("  - Electric")
            elif "Fire" in energy_type:
                print("  - Fire")
            elif "Physic" in energy_type:
                print("  - Physic")
            elif "Water" in energy_type:
                print("  - Water")
            elif "Grass" in energy_type:
                print("  - Grass")
            elif "Fighting" in energy_type:
                print("  - Fighting")
            elif "Metal" in energy_type:
                print("  - Metal")
            elif "Fairy" in energy_type:
                print("  - Fairy")
            elif "Dragon" in energy_type:
                print("  - Dragon")
            elif "Darkness" in energy_type:
                print("  - Darkness")
            else:
                print(" - Normal")
        if self._evolve:
            print(f"Evolves To: {self._evolve[0]}")
            print(f"Evolve Level: {self._evolvelevel}")
        if self._text:
            print(f"Description: {self._text}")
        print("------------------------")
        print(Style.RESET_ALL)


    def giveeffect(self, effect):
        # Apply the status effect to the Pokémon
        if effect in self._stats:
            # Handle mutually exclusive status effects (paralysis, sleep, freeze)
            if effect == "paralysis" and not self._paralyzed and not self._sleep and not self._freeze:
                self._paralyzed = True
                print(f"{self._name} was paralyzed!")
            elif effect == "sleep" and not self._paralyzed and not self._sleep and not self._freeze:
                self._sleep = True
                print(f"{self._name} fell asleep!")
            elif effect == "freeze" and not self._paralyzed and not self._sleep and not self._freeze:
                self._freeze = True
                print(f"{self._name} was frozen!")
            # Poison and burn are independent, so they can be applied even if other conditions exist
            elif effect == "poison" and not self._poisoned:
                self._poisoned = True
                print(f"{self._name} was poisoned!")
            elif effect == "burn" and not self._burn:
                self._burn = True
                print(f"{self._name} was burned!")
        return

    def has_effect(self):
        # Check for active poison or burn effects and return their names
        effects = [self._poisoned, self._burn]
        effectsTrue = []
        stats = self._stats[1:3]  # Only check poison and burn
        for i in range(len(effects)):
            if effects[i]:
                effectsTrue.append(stats[i])
        return effectsTrue

    def evolve(self):
        # Check if the Pokémon can evolve based on its level
        if self._level >= self._evolvelevel:
            if self._evolve != "":
                print(f"{self._name} evolved to {self._evolve[0]}!")
                return True, self._evolve[0]
        return False, ""

    def special_potion(self, specialHl):
        # Heal a specific status effect using a special potion
        if specialHl in self._stats:
            # Map the status effect name to the corresponding attribute
            status_attributes = {
                "paralysis": "_paralyzed",
                "poison": "_poisoned",
                "burn": "_burn",
                "freeze": "_freeze",
                "sleep": "_sleep",
            }
            status_attr = status_attributes.get(specialHl)
            if status_attr and getattr(self, status_attr):  # Check if the effect is active
                setattr(self, status_attr, False)  # Heal the status effect
                print(f"{self._name} is no longer affected by {specialHl}!")
            else:
                print(f"{self._name} is not affected by {specialHl}.")

    def up_status(self, specialStat):
        # Handle special status boosts (e.g., revive, crit boost)
        if specialStat in self._statsUp:
            if specialStat == "revive" and self._fainted:
                self._fainted = False
                print(f"{self._name} has been revived!")
                return
            elif specialStat == "revive" and not self._fainted:
                print(f"{self._name} is already alive! Your {specialStat} does nothing!")
            if specialStat == "dire hit" and not self._critHigh:
                self._critHigh = True
                print(f"{self._name}'s critical hit chance increased!")
            elif specialStat == "dire hit" and self._critHigh:
                print(f"{self._name}'s critical hit chance is already increased! Your {specialStat} does nothing!")
        return

    def heal(self, value, full, half, raises):
        # Heal the Pokémon by a specified amount or set to full/half HP
        if raises:
            self._fullhp += 25  # Increase max HP by 25 (optional feature)
        if full:
            self._hp = self._fullhp  # Heal to full HP
        elif half:
            self._hp = int(self._fullhp / 2)  # Heal to half of full HP
        else:
            self._hp += value  # Heal by a specific value
            if self._hp > self._fullhp:
                self._hp = self._fullhp
        print(f"{self._name} healed to {self._hp}/{self._fullhp} HP!")
        return
        
    def heal_doctor(self):
        # Fully heal the Pokémon and clear all status conditions
        self._hp = self._fullhp
        self._paralyzed = False
        self._burn = False
        self._poisoned = False
        self._sleep = False
        self._freeze = False
        self._fainted = False
        self._pp = self._maxpp.copy()
        return

    def isFainted(self):
        return self._fainted

    def take_damage(self, value):
        # Inflict damage to the Pokémon
        self._hp -= int(value)
        if self._hp <= 0:
            self._hp = 0
            self._fainted = True
            print(f"{self._name} fainted!")  # Pokémon faints when HP reaches 0
        else:
            print(f"{self._name} took {int(value)} damage, {self._hp} HP remaining.")
        return
    
    def showPowerPoints(self, attackIndex):
        return self._pp[attackIndex-1]
    
    def attack(self, attackIndex, other):
        # Perform an attack on another Pokémon
        if self._fainted:
            print(f"{self._name} can't attack because it fainted!")
            return True
        
        count=0
        for pp in self._pp:
            if pp == 0:
                count+=1
        if count == len(self._pp):
            print(f"{self._name} has no more moves!")
            print(f"{self._name} used struggle")
            crit_chance = 3 if self._critHigh else 6  # Adjust critical hit chance if applicable
            crit = random.randint(1, crit_chance) == 1  # Determine if it's a critical hit
            if crit:
                if self._fullhp>=80:
                    damage = int(self._fullhp * 1.5/8)
                else:
                    damage = int(self._fullhp * 1.5/4)
            else:
                if self._fullhp>=80:
                    damage = int(self._fullhp/8)
                else:
                    damage = int(self._fullhp/4)
            other.take_damage(damage)
            print(f"{self._name} took recoil damage")
            self.take_damage(damage/2)
            effects = self.has_effect()
            for effect in effects:
                self.status_effect(effect)
            return True
        
        if self._pp[attackIndex-1] == 0:
            print(f"{self._name} has no more power points for that move.")
            return False

        # Get the attack name and damage from the attack list
        self._pp[attackIndex-1]-=1
        name, damage = list(self._attacks.items())[attackIndex - 1]
        crit_chance = 3 if self._critHigh else 6  # Adjust critical hit chance if applicable
        crit = random.randint(1, crit_chance)  # Determine if it's a critical hit
        # Apply special effects based on the attack's energy type

        # Determine the miss chance based on status conditions
        if self._paralyzed:
            missChance = 5
        elif self._freeze:
            missChance = 2
        elif self._sleep:
            missChance = 4
        else:
            missChance = 6

        miss = random.randint(1, missChance) == 1  # Random chance to miss the attack

        # Handle the result of the attack
        if miss:
            if self._paralyzed:
                print(f"{self._name} is paralyzed! It can't move!")
            elif self._freeze:
                print(f"{self._name} is frozen solid and can't move!")
            elif self._sleep:
                print(f"{self._name} is fast asleep and can't attack!")
            else:
                print(f"{self._name}'s attack missed!")
        else:
            if crit == 1:
                damage = int(damage * 1.5)  # Critical hit increases damage
                print(f"Critical hit! {self._name} used {name} and dealt {int(damage)} damage to {other._name}!")
            else:
                print(f"{self._name} used {name} and dealt {int(damage)} damage to {other._name}!")
            
            if "Fire" in self._energy[attackIndex-1]:
                chance = random.randint(1, 5) == 1
                if chance:
                    other.giveeffect("burn")
            elif "Psychic" in self._energy[attackIndex-1]:
                chance = random.randint(1, 5) == 1
                if chance:
                    other.giveeffect("sleep")
            elif "Water" in self._energy[attackIndex-1]:
                chance = random.randint(1, 5) == 1
                if chance:
                    other.giveeffect("freeze")
            elif "Lightning" in self._energy[attackIndex-1]:
                chance = random.randint(1, 5) == 1
                if chance:
                    other.giveeffect("paralysis")
            elif "Grass" in self._energy[attackIndex-1]:
                chance = random.randint(1, 3) == 1
                if chance:
                    other.giveeffect("poison")

            other.take_damage(damage)

        # Apply status effects (poison, burn, etc.)
        effects = self.has_effect()
        for effect in effects:
            self.status_effect(effect)
        return True
    
    def status_effect(self, effect):
        # Apply the effect of poison or burn over time (damage every turn)
        print(f"{self._name} was hurt by {effect}")
        if effect in self._stats:
            self.take_damage(int(self._fullhp / 16))  # Take damage from poison or burn
        return


    def effectRunOutCount(self):
        self._allstats = ["paralysis", "poison", "burn", "freeze", "sleep", "dire hit"]
        for count in range(len(self._statusCount)):
            if self._statusCount[count] == 4:
                self.effectRunOut(self._allstats[count])
        return

    def effectRunOut(self, effect):
        # Handle the expiration of status effects (paralysis, poison, etc.)
        if effect in self._stats:
            # Map the stat name to the corresponding attribute
            status_attributes = {
                "paralysis": "_paralyzed",
                "poison": "_poisoned",
                "burn": "_burn",
                "freeze": "_freeze",
                "sleep": "_sleep",
                "dire hit": "_critHigh"
            }
            status_attr = status_attributes.get(effect)
            setattr(self, status_attr, False)  # Remove the status effect
            # Print message for the status effect that ran out
            if effect == "paralysis":
                print(f"{self._name} is no longer paralyzed!")
                self._statusCount[self._allstats.index(effect)] = 0
            if effect == "poison":
                print(f"{self._name} is no longer poisoned!")
                self._statusCount[self._allstats.index(effect)] = 0
            if effect == "burn":
                print(f"{self._name} is no longer burned!")
                self._statusCount[self._allstats.index(effect)] = 0
            if effect == "freeze":
                print(f"{self._name} thawed out!")
                self._statusCount[self._allstats.index(effect)] = 0
            if effect == "sleep":
                print(f"{self._name} woke up!")
                self._statusCount[self._allstats.index(effect)] = 0
            if effect == "dire hit":
                print(f"{self._name}'s dire hit ran out!")
                self._statusCount[self._allstats.index(effect)] = 0
        return

    def level_up(self, otherLevel):
        # Level up the Pokémon and check for evolution
        levels_gained = otherLevel // 20
        self._level += levels_gained
        print(f"{self._name} gained {levels_gained} level(s), now level {self._level}!")
        if self._level >= self._evolvelevel and self._evolve != "":
            return self.evolve()
        hp = self._fullhp
        self._fullhp+=2*levels_gained
        if self._fullhp > hp:
            print(f"{self._name}'s max health was increased by {2*levels_gained}")
        return self.evolve()



# # Example usage
# pokemon = "bulbasaur"
# data = card.get_all_hero_data(pokemon.lower())
# pokemonCreated = card.get_card_from_pokemon(data)
# my_pokemon = Pokemon(pokemonCreated)

# my_pokemon.giveeffect("poison")
# my_pokemon.giveeffect("paralysis")

# # Perform an attack
# my_pokemon.attack(1, "Bulbasaur")

# my_pokemon.take_damage(22)

# my_pokemon.heal(20, False, False, False)

# my_pokemon.special_potion("paralysis")
# my_pokemon.giveeffect("freeze")
# my_pokemon.attack(1, "Bulbasaur")
# # Level up and check evolution
# my_pokemon.level_up(320)  # Assuming defeating a high-level opponent