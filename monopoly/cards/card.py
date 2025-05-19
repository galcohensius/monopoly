from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from monopoly.player.player import Player
    from monopoly.board.board import Board

from monopoly.game.move_result import MoveResult
from monopoly.player.other_notes import OtherNotes


@dataclass
class Card:
    text: str
    handler: Callable[[Player, Board, List[Player]], Tuple[MoveResult, str]]
    
    def apply(self, player: Player, board, players: List[Player]) -> Tuple[MoveResult, str]:
        return self.handler(player, board, players)


def advance_to_x(player, board, players, target: int, collect_if_pass=True) -> tuple[MoveResult, str]:
    msg_parts: list[str] = []
    if collect_if_pass and player.position > target:
        salary_msg = player.handle_salary(board)
        msg_parts.append(salary_msg)
    player.position = target
    msg_parts.append(f"→ moves to {board.cells[target].name}")
    return MoveResult.CONTINUE, " ".join(msg_parts)


def advance_to_nearest_utility(player: Player, board, players: List[Player]) -> Tuple[MoveResult, str]:
    # utilities at (12, 28)
    if player.position < 12 or (player.position > 28):
        target = 12
    else:
        target = 28
    move_result, msg = advance_to_x(player, board, players, target)
    player.other_notes = OtherNotes.TEN_TIMES_DICE
    return move_result, msg + ", nearest_utility"


def advance_to_nearest_railroad(player: Player, board, players: List[Player]) -> Tuple[MoveResult, str]:
    # railroads at (5, 15, 25, 35)
    if player.position < 5 or (player.position > 35):
        target = 5
    elif player.position < 15:
        target = 15
    elif player.position < 25:
        target = 25
    else:
        target = 35
    move_result, msg = advance_to_x(player, board, players, target)
    player.other_notes = OtherNotes.DOUBLE_RENT
    return move_result, msg + ", nearest railroad"


def go_back_3_spaces(player: Player, board, players: List[Player]) -> Tuple[MoveResult, str]:
    player.position -= 3
    msg = f" → goes back 3 to {board.cells[player.position].name}"
    return MoveResult.CONTINUE, msg


def get_out_of_jail_free(player: Player, board, players: List[Player]) -> Tuple[MoveResult, str]:
    player.get_out_of_jail_chance = True
    return MoveResult.CONTINUE, f"{player} now has a 'Get Out of Jail Free' card"


def go_to_jail(player: Player, board, players: List[Player]) -> Tuple[MoveResult, str]:
    player.handle_going_to_jail()
    return MoveResult.END_MOVE, f"{player} goes to Jail"


def bank_pays(player: Player, board, players: List[Player], amount: int) -> Tuple[MoveResult, str]:
    player.money += amount
    return MoveResult.CONTINUE, ""


def player_pays_bank(player: Player, board, players: List[Player], amount: int) -> Tuple[MoveResult, str]:
    player.pay_money(amount, "bank", board)
    return MoveResult.CONTINUE, ""


def general_repairs(player: Player, board, players: List[Player], house_cost: int,
                    hotel_cost: int) -> Tuple[MoveResult, str]:
    repair_cost = sum(cell.has_houses * house_cost + cell.has_hotel * hotel_cost for cell in player.owned)
    player.pay_money(repair_cost, "bank", board)
    return MoveResult.CONTINUE, ""


def chairman_of_the_board(player: Player, board, players: List[Player]) -> Tuple[MoveResult, str]:
    for other_player in players:
        if other_player != player and not other_player.is_bankrupt:
            player.pay_money(50, other_player, board)
    return MoveResult.CONTINUE, ""


def collect_from_each_player(player: Player, board, players: List[Player], amount: int) -> Tuple[MoveResult, str]:
    msg_parts: list[str] = []
    for other_player in players:
        if other_player != player and not other_player.is_bankrupt:
            pay_money_msg = other_player.pay_money(amount, player, board)
            msg_parts.append(pay_money_msg)
    
    return MoveResult.CONTINUE, " ".join(msg_parts)


# Build the Chance deck using generic Card instances
CHANCE_CARDS: List[Card] = [
    Card("Advance to Go (Collect $200)", lambda p, b, pl: advance_to_x(p, b, pl, target=0, collect_if_pass=True)),
    Card("Advance to Boardwalk", lambda p, b, pl: advance_to_x(p, b, pl, target=39, collect_if_pass=True)),
    Card("Advance to Illinois Avenue.", lambda p, b, pl: advance_to_x(p, b, pl, target=24, collect_if_pass=True)),
    Card("Advance to St. Charles Place.", lambda p, b, pl: advance_to_x(p, b, pl, target=11, collect_if_pass=True)),
    Card("Advance to Reading Railroad", lambda p, b, pl: advance_to_x(p, b, pl, target=5, collect_if_pass=True)),
    Card("Advance token to nearest Utility. If owned, pay diceX10", advance_to_nearest_utility),
    Card("Advance to the nearest Railroad.", advance_to_nearest_railroad),
    Card("Advance to the nearest Railroad.", advance_to_nearest_railroad),
    Card("Bank pays you dividend of $50", lambda p, b, pl: bank_pays(p, b, pl, 50)),
    Card("Get Out of Jail Free", get_out_of_jail_free),
    Card("Go Back 3 Spaces", go_back_3_spaces),
    Card("Go to Jail. Go directly to Jail, do not pass Go, do not collect $200", go_to_jail),
    Card("Make general repairs on all your property. For each house pay $25. For each hotel pay $100", lambda p, b, pl: general_repairs(p, b, pl, 25, 100)),
    Card("Speeding fine $15", lambda p, b, pl: player_pays_bank(p, b, pl, 15)),
    Card("Take a trip to Reading Railroad. If you pass Go, collect $200", lambda p, b, pl: advance_to_x(p, b, pl, target=5, collect_if_pass=True)),
    Card("You have been elected Chairman of the Board. Pay each player $50", chairman_of_the_board),
    Card("Your building loan matures. Collect $150", lambda p, b, pl: bank_pays(p, b, pl, 150))
]

COMMUNITY_CHEST_CARDS = [
    Card("Advance to Go (Collect $200)", lambda p, b, pl: advance_to_x(p, b, pl, target=0, collect_if_pass=True)),
    Card("Bank error in your favor. Collect $200", lambda p, b, pl: bank_pays(p, b, pl, 200)),
    Card("Doctor's fee. Pay $50", lambda p, b, pl: player_pays_bank(p, b, pl, 50)),
    Card("From sale of stock you get $50", lambda p, b, pl: bank_pays(p, b, pl, 50)),
    Card("Get Out of Jail Free", get_out_of_jail_free),
    Card("Go to Jail. Go directly to jail, do not pass Go, do not collect $200", go_to_jail),
    Card("Holiday fund matures. Receive $100", lambda p, b, pl: bank_pays(p, b, pl, 100)),
    Card("Income tax refund. Collect $20", lambda p, b, pl: bank_pays(p, b, pl, 20)),
    Card("It is your birthday. Collect $10 from every player", lambda p, b, pl: collect_from_each_player(p, b, pl, 10)),
    Card("Life insurance matures. Collect $100", lambda p, b, pl: bank_pays(p, b, pl, 100)),
    Card("Pay hospital fees of $100", lambda p, b, pl: player_pays_bank(p, b, pl, 100)),
    Card("Pay school fees of $50", lambda p, b, pl: player_pays_bank(p, b, pl, 50)),
    Card("Receive $25 consultancy fee", lambda p, b, pl: bank_pays(p, b, pl, 25)),
    Card("You are assessed for street repair. $40 per house. $115 per hotel", lambda p, b, pl: general_repairs(p, b, pl, 40, 115)),
    Card("You have won second prize in a beauty contest. Collect $10", lambda p, b, pl: bank_pays(p, b, pl, 10)),
    Card("You inherit $100", lambda p, b, pl: bank_pays(p, b, pl, 100))
]
