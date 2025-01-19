from tkinter import *
import random

class BoardCell(Canvas):
    def __init__(self, master, coord):
        Canvas.__init__(self, master, width=30, height=30, bg='light green', bd=0, highlightthickness=1, highlightbackground="black")
        self._coord = coord
        self._hasTrainer = False
        self._hasPlayer = False
        self._hasGym = False
        self._hasShop = False
        self._text = ""

    def givePlayer(self):
        self._hasPlayer = True
        self.delete(self._text)
        self._text = self.create_text(15, 15, text="O", font=("Arial", 25), fill="black", anchor="center")
        self.config(bg='blue')  # Change color to indicate the player's position

    def giveTrainer(self):
        self._hasTrainer = True
        self.config(bg='red')  # Change color to indicate a trainer's position

    def giveGym(self):
        self._hasGym = True
        self._text = self.create_text(15, 15, text="X", font=("Arial", 25), fill="black", anchor="center")
        self.config(bg='dark red')  # Change color to indicate a gym's position

    def giveShop(self):
        self._hasShop = True
        self._text = self.create_text(15, 15, text="S", font=("Arial", 25), fill="black", anchor="center")
        self.config(bg='dark green')

    def removePlayer(self):
        self._hasPlayer = False
        self.delete(self._text)

    def showPath(self):
        if not self._hasTrainer and not self._hasGym and not self._hasShop:
            self.config(bg='light blue')  # Highlight the path the player has traveled
        if self._hasTrainer and not self._hasGym and not self._hasShop:
            self.config(bg='magenta')
        if not self._hasTrainer and self._hasGym and not self._hasShop:
            self.config(bg='purple')
        if not self._hasTrainer and not self._hasGym and self._hasShop:
            self.config(bg='cyan')
        return

    def revertColor(self):
        if self._hasGym:
            self.giveGym()
            self.config(bg='dark red')
        elif self._hasTrainer:
            self.giveTrainer()
            self.config(bg='red')
        elif self._hasShop:
            self.giveShop()
            self.config(bg='dark green')
        else:
            self.config(bg='light green')
        return

    def hasTrainer(self):
        return self._hasTrainer

    def hasPlayer(self):
        return self._hasPlayer
    
    def hasGym(self):
        return self._hasGym
    
    def hasShop(self):
        return self._hasShop


class Board(Frame):
    def __init__(self, master, width=20, height=20, numTrainers=50):
        Frame.__init__(self, master, bg="black", bd=5)
        self.grid()
        self._directionsX = {"left": -1, "right": 1}
        self._directionsY = {"up": -1, "down": 1}
        self._cells = {}
        self._width = width
        self._height = height
        self._numTrainers = numTrainers
        self._homeCoord = (20,10)
        self._path = []  # Keep track of the player's path (last two cells only)

        # Initialize the board
        for column in range(1, width + 1):
            for row in range(1, height + 1):
                coord = (row, column)
                self._cells[coord] = BoardCell(self, coord)
                self._cells[coord].grid(row=row, column=column, padx=0, pady=0)

        # Place the player and other elements
        self._cells[(10, 10)].givePlayer()
        self._cells[self._homeCoord].giveShop()
        self._path.append((10, 10))  # Add the starting position to the path
        self.place(numTrainers)
        self.place_gym(8)

    def place(self, amount):
        placed_trainers = set()
        while len(placed_trainers) < amount:
            newCoord = (random.randint(1, self._height), random.randint(1, self._width))
            if newCoord != (10, 10) and newCoord != self._homeCoord and newCoord not in placed_trainers:
                self._cells[newCoord].giveTrainer()
                placed_trainers.add(newCoord)

    def place_gym(self, amount):
        placed_gym = set()
        while len(placed_gym) < amount:
            newCoord = (random.randint(1, self._height), random.randint(1, self._width))
            if newCoord != (10, 10) and newCoord != self._homeCoord and newCoord not in placed_gym and not self._cells[newCoord].hasTrainer():
                self._cells[newCoord].giveGym()
                placed_gym.add(newCoord)

    def findPlayerCoords(self):
        for coord, cell in self._cells.items():
            if cell.hasPlayer():
                return coord
        return None

    def movePlayer(self, direction, home=False):
        playerCoord = self.findPlayerCoords()
        if home:
            for x in self._path:
                self._cells[x].revertColor()
            self._cells[playerCoord].removePlayer()
            self._cells[playerCoord].revertColor()
            self._cells[self._homeCoord].givePlayer()
            return
            
        if not playerCoord:
            return False, False, False, False

        # Determine the new coordinates based on the direction
        newCoord = None
        if direction in self._directionsX:
            val = self._directionsX[direction]
            newCoord = (playerCoord[0], playerCoord[1] + val)  # Adjust column for left/right
        elif direction in self._directionsY:
            val = self._directionsY[direction]
            newCoord = (playerCoord[0] + val, playerCoord[1])  # Adjust row for up/down

        # Ensure the new coordinates are within bounds
        if not newCoord or not (1 <= newCoord[0] <= self._height and 1 <= newCoord[1] <= self._width):
            return False, False, False, False

        # Revert the oldest cell in the path if it exceeds two moves
        if len(self._path) == 1:
            oldestCoord = self._path.pop(0)
            self._cells[oldestCoord].revertColor()

        # Add the current position to the path and highlight it
        self._cells[playerCoord].showPath()
        self._path.append(playerCoord)

        # Update player's position
        self._cells[playerCoord].removePlayer()  # Remove the player from the old cell
        self._cells[newCoord].givePlayer()  # Place the player in the new cell

        # Check for events at the new position
        if self._cells[newCoord].hasShop():
            print("You went home")
            return True, False, False, True
        if self._cells[newCoord].hasTrainer():
            print("Trainer found!")
            return True, True, False, False
        if self._cells[newCoord].hasGym():
            return True, False, True, False

        return True, False, False, False


# Uncomment to run the program
# root = Tk()
# root.title("POKEMON MAP")
# board = Board(root, width=20, height=20, numTrainers=50)
# root.mainloop()
