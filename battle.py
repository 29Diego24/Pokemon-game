import random

class Counter:
    def __init__(self, myPokemon, other):
        self._pokemon = myPokemon
        self._other = other
        self._turnCount = 1
        self._statusCount = [0, 0, 0, 0, 0, 0]
        self._status = ["paralysis", "poison", "burn", "freeze", "sleep"]
        self._buff = "dire_hit"
        self._battleOptions = []

    # def turn(self):
    #     print(f"Turn: {self._turnCount}")
    #     if len(self._pokemon._attacks)>=2:
    #         attack = int(input(f"{self._pokemon._name} has {len(self._pokemon._attacks)} moves. Which one do you want (1-{len(self._pokemon._attacks)})?"))
    #     else:
    #         attack = int(input(f"{self._pokemon._name} has {len(self._pokemon._attacks)} moves. Which one do you want (1)?"))
        
    #     self._pokemon.attack(attack, self._other)
    #     self._other.attack(random.randint(1,len(self._other._attacks)))
    #     return
    
    
