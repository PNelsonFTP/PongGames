import random

# Maze generation using DFS for a 5x5 grid
class Maze:
    def __init__(self, width=5, height=5):
        self.width = width
        self.height = height
        self.cells = [[[] for _ in range(width)] for _ in range(height)]  # List of directions per cell
        self.visited = [[False for _ in range(width)] for _ in range(height)]
        self.generate_maze()
        self.exit_room = (random.randint(0, height-1), random.randint(0, width-1))  # Specific random exit room

    def generate_maze(self):
        directions = [(-1, 0, 0, 1), (1, 0, 1, 0), (0, 1, 2, 3), (0, -1, 3, 2)]  # dy, dx, dir, opp_dir
        stack = [(0, 0)]
        self.visited[0][0] = True

        while stack:
            y, x = stack[-1]
            unvisited_neighbors = []
            for dy, dx, d, opp in directions:
                ny, nx = y + dy, x + dx
                if 0 <= ny < self.height and 0 <= nx < self.width and not self.visited[ny][nx]:
                    unvisited_neighbors.append((ny, nx, d, opp))

            if unvisited_neighbors:
                ny, nx, d, opp = random.choice(unvisited_neighbors)
                self.cells[y][x].append(d)
                self.cells[ny][nx].append(opp)
                self.visited[ny][nx] = True
                stack.append((ny, nx))
            else:
                stack.pop()

        # Ensure 2-4 doors per room
        for y in range(self.height):
            for x in range(self.width):
                current_degree = len(self.cells[y][x])
                if current_degree < 4:
                    possible_adds = []
                    for dy, dx, d, opp in directions:
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < self.height and 0 <= nx < self.width and d not in self.cells[y][x]:
                            possible_adds.append((ny, nx, d, opp))
                    random.shuffle(possible_adds)
                    adds = min(max(2 - current_degree, 0), len(possible_adds))
                    for i in range(adds):
                        ny, nx, d, opp = possible_adds[i]
                        self.cells[y][x].append(d)
                        self.cells[ny][nx].append(opp)

    def get_neighbors(self, y, x):
        dirs = ['North', 'South', 'East', 'West']
        neighbors = []
        for d in self.cells[y][x]:
            if d == 0 and y-1 >= 0:
                neighbors.append(('North', y-1, x))
            elif d == 1 and y+1 < self.height:
                neighbors.append(('South', y+1, x))
            elif d == 2 and x+1 < self.width:
                neighbors.append(('East', y, x+1))
            elif d == 3 and x-1 >= 0:
                neighbors.append(('West', y, x-1))
        return neighbors

# Room descriptions and choices (classic D&D fantasy)
room_descriptions = [
    "A dusty chamber holds an old chest, faintly glowing with magic.",
    "A fountain bubbles with enchanted water in this dim room.",
    "Skeletons of fallen warriors are scattered across the floor.",
    "Ancient tomes of forgotten lore line a library’s shelves.",
    "A small altar holds a glowing idol of a forgotten god.",
    "Torchlight flickers on walls etched with arcane runes.",
    "A trapdoor in the ceiling leads to unknown heights.",
    "Glowing mushrooms grow in clusters on the damp floor.",
    "An abandoned campfire smolders, left by recent travelers.",
    "Webs cover everything, hinting at giant spiders nearby.",
    "A mirror reflects your image with a twist of illusion.",
    "Barrels and crates are stacked, possibly hiding treasure.",
    "A fierce dragon statue stands sentinel in the room.",
    "Vines creep along the walls, pulsing with druidic magic.",
    "Dripping water echoes in this cavernous chamber.",
    "Rusty weapons rest on racks, some still sharp.",
    "A puzzle box on a pedestal challenges your wits.",
    "Ghostly whispers of restless spirits fill the air.",
    "Enchanted flowers bloom in a vibrant bed.",
    "Chains dangle from the ceiling, rattling softly.",
    "A map etched into the stone floor hints at dungeon secrets.",
    "Candles burn brightly in a dark ritual circle.",
    "A pile of treasures glints temptingly in the corner.",
    "A deep well descends into abyssal darkness.",
    "Shadows dance as if alive, hiding unseen threats."
]

choices = [
    "Open the chest?",
    "Drink from the fountain?",
    "Disturb the skeletons?",
    "Read a random tome?",
    "Touch the idol?",
    "Trace the runes?",
    "Climb to the trapdoor?",
    "Eat a mushroom?",
    "Search the campfire ashes?",
    "Clear the webs?",
    "Stare into the mirror?",
    "Search the barrels?",
    "Examine the statue?",
    "Pull the vines?",
    "Investigate the dripping?",
    "Take a weapon?",
    "Open the puzzle box?",
    "Respond to the whispers?",
    "Pick a flower?",
    "Rattle the chains?",
    "Study the map?",
    "Blow out the candles?",
    "Dig into the treasures?",
    "Drop a coin into the well?",
    "Confront the shadows?"
]

# Outcomes, including combat
positive_outcomes = [
    "You find 20 gold pieces!",
    "Your health is restored by 10!",
    "You gain a healing potion!",
    "Your strength increases by 1!",
    "You find a sharp sword!",
    "You gain 50 experience points!",
    "You find a mysterious key!"
]
negative_outcomes = [
    "It's trapped! Lose 15 health.",
    "Poisoned! Lose 10 health.",
    "Cursed! Lose 10 gold.",
    "A monster attacks! Lose 20 health."
]
even_outcomes = ["Nothing happens."]
combat_outcomes = [
    "A goblin leaps from the shadows! Fight?",
    "A skeleton rises to attack! Engage?",
    "A giant rat lunges at you! Battle?",
    "A wraith forms from the shadows! Combat?"
]

# Player class
class Player:
    def __init__(self):
        self.health = 100
        self.strength = 10
        self.gold = 0
        self.experience = 0
        self.inventory = []
        self.position = (0, 0)  # Start at top-left
        self.previous_door = None

    def is_alive(self):
        return self.health > 0

    def combat(self):
        monster_health = random.randint(20, 50)
        monster_strength = random.randint(5, 15)
        print(f"You enter combat! Monster has {monster_health} health and {monster_strength} strength.")
        while self.health > 0 and monster_health > 0:
            damage = random.randint(1, self.strength)
            monster_health -= damage
            print(f"You deal {damage} damage. Monster health: {max(0, monster_health)}")
            if monster_health <= 0:
                print("You win the combat!")
                gain = random.choice(["You gain 30 gold!", "You gain 100 experience!", "You find a potion!"])
                print(gain)
                if "gold" in gain:
                    self.gold += 30
                elif "experience" in gain:
                    self.experience += 100
                elif "potion" in gain:
                    self.inventory.append("Healing Potion")
                return True
            damage = random.randint(1, monster_strength)
            self.health -= damage
            print(f"Monster deals {damage} damage. Your health: {max(0, self.health)}")
        if self.health <= 0:
            print("You lose the combat and die.")
            return False
        return True

# Main game
def play_game():
    maze = Maze()
    player = Player()
    visited = set()

    print("Welcome to the Dungeon Adventure! Explore the maze, make choices, and find the exit.")

    while player.is_alive():
        y, x = player.position
        room_id = y * maze.width + x

        if (y, x) == maze.exit_room:
            print("You have found the hidden exit room! You escape the dungeon!")
            print(f"Final stats: Health {player.health}, Strength {player.strength}, Gold {player.gold}, Experience {player.experience}, Inventory: {player.inventory}")
            break

        if (y, x) not in visited:
            visited.add((y, x))
            print("\n" + room_descriptions[room_id])

            # Room choice
            choice_text = choices[room_id]
            print(f"Do you want to {choice_text} (yes/no)?")
            try:
                decision = input().strip().lower()
            except EOFError:
                print("Input stream closed. Exiting game.")
                break
            yes_options = ['yes', 'y']
            no_options = ['no', 'n']
            if decision not in yes_options + no_options:
                print("Please enter 'yes', 'y', 'no', or 'n'.")
                continue

            if decision in yes_options:
                # 1/100 death chance on choice
                if random.randint(1, 100) == 1:
                    print("Catastrophic failure! You die instantly.")
                    player.health = 0
                    break

                rand = random.random()
                if rand < 0.1:  # 10% chance for combat
                    combat_choice = random.choice(combat_outcomes)
                    print(combat_choice)
                    try:
                        fight_dec = input("Fight? (yes/no): ").strip().lower()
                    except EOFError:
                        print("Input stream closed. Exiting game.")
                        break
                    yes_options = ['yes', 'y']
                    no_options = ['no', 'n']
                    if fight_dec not in yes_options + no_options:
                        print("Please enter 'yes', 'y', 'no', or 'n'.")
                        continue
                    if fight_dec in yes_options:
                        if not player.combat():
                            break
                    else:
                        print("You flee, but take 10 damage.")
                        player.health -= 10
                elif rand < 0.75:  # 65% positive
                    outcome = random.choice(positive_outcomes)
                    print(outcome)
                    if 'gold' in outcome:
                        player.gold += 20
                    elif 'health' in outcome:
                        player.health += 10
                    elif 'potion' in outcome:
                        player.inventory.append('Healing Potion')
                    elif 'strength' in outcome:
                        player.strength += 1
                    elif 'sword' in outcome:
                        player.inventory.append('Sword')
                        player.strength += 2
                    elif 'experience' in outcome:
                        player.experience += 50
                    elif 'key' in outcome:
                        player.inventory.append('Key')
                elif rand < 0.95:  # 20% negative
                    outcome = random.choice(negative_outcomes)
                    print(outcome)
                    if 'health' in outcome:
                        loss = int(outcome.split('Lose ')[1].split(' ')[0])
                        player.health -= loss
                    elif 'gold' in outcome:
                        player.gold = max(0, player.gold - 10)
                else:  # 5% even
                    print(random.choice(even_outcomes))

                if not player.is_alive():
                    break

        # Doors
        neighbors = maze.get_neighbors(y, x)
        if not neighbors:
            print("Error: No valid doors available. Ending game.")
            break
        print("Available doors:")
        door_options = {}
        for i, (dir_name, ny, nx) in enumerate(neighbors, 1):
            door_options[str(i)] = (dir_name, ny, nx)
            print(f"{i}. {dir_name}")

        # Choose door
        try:
            choice = input("Choose a door (number): ").strip()
        except EOFError:
            print("Input stream closed. Exiting game.")
            break
        if choice not in door_options:
            print(f"Please enter a number between 1 and {len(door_options)}.")
            continue
        dir_name, ny, nx = door_options[choice]
        # 1/100 death chance on door
        if random.randint(1, 100) == 1:
            print("A deadly trap triggers as you open the door! You die.")
            player.health = 0
            break
        player.previous_door = dir_name
        player.position = (ny, nx)

    if player.is_alive():
        print("Congratulations on escaping!")
    else:
        print("Game over. You died.")
    print(f"Final stats: Health {player.health}, Strength {player.strength}, Gold {player.gold}, Experience {player.experience}, Inventory: {player.inventory}")

if __name__ == "__main__":
    try:
        play_game()
    except KeyboardInterrupt:
        print("\nGame interrupted by user. Exiting.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")