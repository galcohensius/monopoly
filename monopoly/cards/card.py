from dataclasses import dataclass
from typing import Callable, List

from monopoly.game.move_result import MoveResult
from monopoly.player.other_notes import OtherNotes
from monopoly.player.player import Player
from monopoly.log import Log


@dataclass
class Card:
    text: str
    handler: Callable[['Player', "'Board'", List['Player'], 'Log'], MoveResult]

    def apply(self, player: Player, board, players: List[Player], log: Log) -> MoveResult:
        return self.handler(player, board, players, log)


def advance_to_x(player, board, players, log, target: int, collect_if_pass=True) -> MoveResult:
    log.add(f"{player} goes to {board.cells[target]}")
    if collect_if_pass and player.position > target:
        player.handle_salary(board, log)
    player.position = target
    return MoveResult.CONTINUE


def advance_to_nearest_utility(player: Player, board, players: List[Player], log: Log) -> MoveResult:
    # utilities at (12, 28)
    if player.position < 12 or (player.position > 28):
        target = 12
    else:
        target = 28
    advance_to_x(player, board, players, log, target)
    player.other_notes = OtherNotes.TEN_TIMES_DICE
    return MoveResult.CONTINUE


def advance_to_nearest_railroad(player: Player, board, players: List[Player], log: Log) -> MoveResult:
    # railroads at (5, 15, 25, 35)
    if player.position < 5 or (player.position > 35):
        target = 5
    elif player.position < 15:
        target = 15
    elif player.position < 25:
        target = 25
    else:
        target = 35
    advance_to_x(player, board, players, log, target)
    player.other_notes = OtherNotes.DOUBLE_RENT
    return MoveResult.CONTINUE

def go_back_3_spaces(player: Player, board, players: List[Player], log: Log) -> MoveResult:
    player.position -= 3
    log.add(f"{player} goes to {board.cells[player.position]}")
    return MoveResult.CONTINUE

def get_out_of_jail_free(player: Player, board, players: List[Player], log: Log) -> MoveResult:
    log.add(f"{player} now has a 'Get Out of Jail Free' card")
    player.get_out_of_jail_chance = True
    # We'll need to handle removing this card from the deck elsewhere
    return MoveResult.CONTINUE

def go_to_jail(player: Player, board, players: List[Player], log: Log) -> MoveResult:
    player.handle_going_to_jail("got GTJ card", log)
    return MoveResult.END_MOVE


def bank_pays(player: Player, board, players: List[Player], log: Log, amount: int) -> MoveResult:
    log.add(f"{player} gets ${amount}")
    player.money += amount
    return MoveResult.CONTINUE

def player_pays_bank(player: Player, board, players: List[Player], log: Log, amount: int) -> MoveResult:
    log.add(f"{player} pays ${amount}")
    player.pay_money(amount, "bank", board, log)
    return MoveResult.CONTINUE

def general_repairs(player: Player, board, players: List[Player], log: Log, house_cost: int, hotel_cost: int) -> MoveResult:
    repair_cost = sum(cell.has_houses * house_cost + cell.has_hotel * hotel_cost for cell in player.owned)
    log.add(f"Repair cost: ${repair_cost}")
    player.pay_money(repair_cost, "bank", board, log)
    return MoveResult.CONTINUE


def chairman_of_the_board(player: Player, board, players: List[Player], log: Log) -> MoveResult:
    for other_player in players:
        if other_player != player and not other_player.is_bankrupt:
            player.pay_money(50, other_player, board, log)
            if not player.is_bankrupt:
                log.add(f"{player} pays {other_player} $50")
    return MoveResult.CONTINUE


def collect_from_each_player(player: Player, board, players: List[Player], log: Log, amount: int) -> MoveResult:
    for other_player in players:
        if other_player != player and not other_player.is_bankrupt:
            other_player.pay_money(amount, player, board, log)
            if not other_player.is_bankrupt:
                log.add(f"{other_player} pays {player} ${amount}")
    return MoveResult.CONTINUE


# Build the Chance deck using generic Card instances
CHANCE_CARDS: List[Card] = [
    Card("Advance to Go (Collect $200)", lambda p, b, pl, lg: advance_to_x(p, b, pl, lg, target=0, collect_if_pass=True)),
    Card("Advance to Boardwalk", lambda p, b, pl, lg: advance_to_x(p, b, pl, lg, target=39, collect_if_pass=True)),
    Card("Advance to Illinois Avenue. If you pass Go, collect $200", lambda p, b, pl, lg: advance_to_x(p, b, pl, lg, target=24, collect_if_pass=True)),
    Card("Advance to St. Charles Place. If you pass Go, collect $200", lambda p, b, pl, lg: advance_to_x(p, b, pl, lg, target=11, collect_if_pass=True)),
    Card("Advance to Reading Railroad", lambda p, b, pl, lg: advance_to_x(p, b, pl, lg, target=5, collect_if_pass=True)),
    Card("Advance token to nearest Utility. If owned, throw dice and pay owner a total ten times amount thrown.", advance_to_nearest_utility),
    Card("Advance to the nearest Railroad. If owned, pay owner twice the rental to which they are otherwise entitled", advance_to_nearest_railroad),
    Card("Advance to the nearest Railroad. If owned, pay owner twice the rental to which they are otherwise entitled", advance_to_nearest_railroad),
    Card("Bank pays you dividend of $50", lambda p, b, pl, lg: bank_pays(p, b, pl, lg, 50)),
    Card("Get Out of Jail Free", get_out_of_jail_free),
    Card("Go Back 3 Spaces", go_back_3_spaces),
    Card("Go to Jail. Go directly to Jail, do not pass Go, do not collect $200", go_to_jail),
    Card("Make general repairs on all your property. For each house pay $25. For each hotel pay $100", lambda p, b, pl, lg: general_repairs(p, b, pl, lg, 25, 100)),
    Card("Speeding fine $15", lambda p, b, pl, lg: player_pays_bank(p, b, pl, lg, 15)),
    Card("Take a trip to Reading Railroad. If you pass Go, collect $200", lambda p, b, pl, lg: advance_to_x(p, b, pl, lg, target=5, collect_if_pass=True)),
    Card("You have been elected Chairman of the Board. Pay each player $50", chairman_of_the_board),
    Card("Your building loan matures. Collect $150", lambda p, b, pl, lg: bank_pays(p, b, pl, lg, 150))
]

COMMUNITY_CHEST_CARDS = [
    Card("Advance to Go (Collect $200)", lambda p, b, pl, lg: advance_to_x(p, b, pl, lg, target=0, collect_if_pass=True)),
    Card("Bank error in your favor. Collect $200", lambda p, b, pl, lg: bank_pays(p, b, pl, lg, 200)),
    Card("Doctor's fee. Pay $50", lambda p, b, pl, lg: player_pays_bank(p, b, pl, lg, 50)),
    Card("From sale of stock you get $50", lambda p, b, pl, lg: bank_pays(p, b, pl, lg, 50)),
    Card("Get Out of Jail Free", get_out_of_jail_free),
    Card("Go to Jail. Go directly to jail, do not pass Go, do not collect $200", go_to_jail),
    Card("Holiday fund matures. Receive $100", lambda p, b, pl, lg: bank_pays(p, b, pl, lg, 100)),
    Card("Income tax refund. Collect $20", lambda p, b, pl, lg: bank_pays(p, b, pl, lg, 20)),
    Card("It is your birthday. Collect $10 from every player", lambda p, b, pl, lg: collect_from_each_player(p, b, pl, lg, 10)),
    Card("Life insurance matures. Collect $100", lambda p, b, pl, lg: bank_pays(p, b, pl, lg, 100)),
    Card("Pay hospital fees of $100", lambda p, b, pl, lg: player_pays_bank(p, b, pl, lg, 100)),
    Card("Pay school fees of $50", lambda p, b, pl, lg: player_pays_bank(p, b, pl, lg, 50)),
    Card("Receive $25 consultancy fee", lambda p, b, pl, lg: bank_pays(p, b, pl, lg, 25)),
    Card("You are assessed for street repair. $40 per house. $115 per hotel", lambda p, b, pl, lg: general_repairs(p, b, pl, lg, 40, 115)),
    Card("You have won second prize in a beauty contest. Collect $10", lambda p, b, pl, lg: bank_pays(p, b, pl, lg, 10)),
    Card("You inherit $100", lambda p, b, pl, lg: bank_pays(p, b, pl, lg, 100))
]
