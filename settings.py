""" Config file for monopoly simulation """
from dataclasses import dataclass
from typing import FrozenSet

HERO = "Tom"
PLAYER_2 = "Chunk"
# PLAYER_3 = "Bob"
# PLAYER_4 = "Charly"


@dataclass(frozen=True)
class GameMechanics:
    # Houses and hotel available for development
    available_houses = 36
    available_hotels = 12
    salary = 200  # Passing Go salary
    luxury_tax = 100
    # Income tax (cash or share of net worth)
    income_tax = 200
    income_tax_percentage = .1
    mortgage_value = 0.5  # how much cash a player gets for mortgaging a property (Default is 0.5)
    mortgage_fee = 0.1  # The extra a player needs to pay to unmortgage (Default is 0.1)
    exit_jail_fine = 50  # Fine to get out of jail without rolling doubles
    free_parking_money = False  # Controversial house rule to collect fines on Free Parking and give to whoever lands there
    # Dice settings
    dice_count = 2
    dice_sides = 6
    

@dataclass(frozen=True)
class SimulationSettings:
    n_games: int = 10_000  # Number of games to simulate
    n_moves: int = 1000  # Max Number of moves per game
    seed: int = 0  # Random seed to start simulation with
    multi_process: int = 4  # Number of parallel processes to use in the simulation
    
    # Cash that will be considered cannot go bankrupt. See this paper that estimates the probability that the game
    # will last forever. https://www.researchgate.net/publication
    # /224123876_Estimating_the_probability_that_the_game_of_Monopoly_never_ends
    never_bankrupt_cash: int = 10000


@dataclass(frozen=True)
class StandardPlayerSettings:
    unspendable_cash: int = 200  # Amount of money the player wants to keep unspent (money safety pillow)
    ignore_property_groups: FrozenSet[str] = frozenset()  # Group of properties do not buy, i.e.{"RED", "GREEN"}
    
    is_willing_to_make_trades: bool = False
    # agree to trades if the value difference is within these limits:
    trade_max_diff_absolute: int = 200  # More expensive - less expensive
    trade_max_diff_relative: float = 2.0  # More expensive / less expensive


@dataclass(frozen=True)
class HeroPlayerSettings(StandardPlayerSettings):
    """ here you can change the settings of the hero (the Experimental Player) """
    # ignore_property_groups: FrozenSet[str] = frozenset({"GREEN"})


@dataclass(frozen=True)
class GameSettings:
    """ Setting for the game (rules and player list) """
    mechanics: GameMechanics = GameMechanics()  # the rules of the game
    
    # Players and their behavior settings
    players_list = [
        (HERO, HeroPlayerSettings),
        (PLAYER_2, StandardPlayerSettings),
        # (PLAYER_3, StandardPlayerSettings),
        # (PLAYER_4, StandardPlayerSettings),
    ]
    
    # Randomly shuffle the order of players each game
    shuffle_players = True
    
    # Initial money (a single integer if it is the same for everybody or a dict of player names and cash)
    # for example, either starting_money = 1500 or a dictionary with player names as keys and int values
    starting_money = {
        HERO: 1000,
        PLAYER_2: (1000+1500),
        # PLAYER_3: 1500,
        # PLAYER_4: 1500
    }
    
    # Initial properties (a dictionary with player names as keys and a list of property numbers as values)
    # Property numbers correspond to indices in `board.cells`
    starting_properties = {
        HERO: [1,3, 5,15,25, 12, ],  # Purple, 3 Railroads, electric company
        PLAYER_2: [16,18,19, 11,13,14],   #  Orange, Pink
        # PLAYER_3: [],
        # PLAYER_4: []
    }
    
    # self.cells.append(Cell("GO"))
    #         self.cells.append(Property("A1 Mediterranean Avenue", 60, 2, 50, (10, 30, 90, 160, 250), BROWN))
    #         self.cells.append(CommunityChest("COM1 Community Chest"))
    #         self.cells.append(Property("A2 Baltic Avenue", 60, 4, 50, (20, 60, 180, 320, 450), BROWN))
    #         self.cells.append(IncomeTax("IT Income Tax"))
    #         # 5-9
    #         self.cells.append(Property("R1 Reading Railroad", 200, 25, 0, (0, 0, 0, 0, 0), RAILROADS))
    #         self.cells.append(Property("B1 Oriental Avenue", 100, 6, 50, (30, 90, 270, 400, 550), LIGHTBLUE))
    #         self.cells.append(Chance("CH1 Chance"))
    #         self.cells.append(Property("B2 Vermont Avenue", 100, 6, 50, (30, 90, 270, 400, 550), LIGHTBLUE))
    #         self.cells.append(Property("B3 Connecticut Avenue", 120, 8, 50, (40, 100, 300, 450, 600), LIGHTBLUE))
    #         # 10-14
    #         self.cells.append(Cell("JL Jail"))
    #         self.cells.append(Property("C1 St. Charles Place", 140, 10, 100, (50, 150, 450, 625, 750), PINK))
    #         self.cells.append(Property("U1 Electric Company", 150, 0, 0, (0, 0, 0, 0, 0), UTILITIES))
    #         self.cells.append(Property("C2 States Avenue", 140, 10, 100, (50, 150, 450, 625, 750), PINK))
    #         self.cells.append(Property("C3 Virginia Avenue", 160, 12, 100, (60, 180, 500, 700, 900), PINK))
    #         # 15-19
    #         self.cells.append(Property("R2 Pennsylvania Railroad", 200, 25, 0, (0, 0, 0, 0, 0), RAILROADS))
    #         self.cells.append(Property("D1 St. James Place", 180, 14, 100, (70, 200, 550, 700, 950), ORANGE))
    #         self.cells.append(CommunityChest("COM2 Community Chest"))
    #         self.cells.append(Property("D2 Tennessee Avenue", 180, 14, 100, (70, 200, 550, 700, 950), ORANGE))
    #         self.cells.append(Property("D3 New York Avenue", 200, 16, 100, (80, 220, 600, 800, 1000), ORANGE))
    #         # 20-24
    #         self.cells.append(FreeParking("FP Free Parking"))
    #         self.cells.append(Property("E1 Kentucky Avenue", 220, 18, 150, (90, 250, 700, 875, 1050), RED))
    #         self.cells.append(Chance("CH2 Chance"))
    #         self.cells.append(Property("E2 Indiana Avenue", 220, 18, 150, (90, 250, 700, 875, 1050), RED))
    #         self.cells.append(Property("E3 Illinois Avenue", 240, 20, 150, (100, 300, 750, 925, 1100), RED))
    #         # 25-29
    #         self.cells.append(Property("R3 B&O Railroad", 200, 25, 0, (0, 0, 0, 0, 0), RAILROADS))
    #         self.cells.append(Property("F1 Atlantic Avenue", 260, 22, 150, (110, 330, 800, 975, 1150), YELLOW))
    #         self.cells.append(Property("F2 Ventnor Avenue", 260, 22, 150, (110, 330, 800, 975, 1150), YELLOW))
    #         self.cells.append(Property("U2 Waterworks", 150, 0, 0, (0, 0, 0, 0, 0), UTILITIES))
    #         self.cells.append(Property("F3 Marvin Gardens", 280, 24, 150, (120, 360, 850, 1025, 1200), YELLOW))
    #         # 30-34
    #         self.cells.append(GoToJail("GTJ Go To Jail"))
    #         self.cells.append(Property("G1 Pacific Avenue", 300, 26, 200, (130, 390, 900, 1100, 1275), GREEN))
    #         self.cells.append(Property("G2 North Carolina Avenue", 300, 26, 200, (130, 390, 900, 1100, 1275), GREEN))
    #         self.cells.append(CommunityChest("COM3 Community Chest"))
    #         self.cells.append(Property("G3 Pennsylvania Avenue", 320, 28, 200, (150, 450, 1000, 1200, 1400), GREEN))
    #         # 35-39
    #         self.cells.append(Property("R4 Short Line", 200, 25, 0, (0, 0, 0, 0, 0), RAILROADS))
    #         self.cells.append(Chance("CH3 Chance"))
    #         self.cells.append(Property("H1 Park Place", 350, 35, 200, (175, 500, 1100, 1300, 1500), INDIGO))
    #         self.cells.append(LuxuryTax("LT Luxury Tax"))
    #         self.cells.append(Property("H2 Boardwalk", 400, 50, 200, (200, 600, 1400, 1700, 2000), INDIGO))
    
    