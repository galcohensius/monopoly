from dataclasses import dataclass
from typing import Callable, List

from monopoly.core.board import Board
from monopoly.core.move_result import MoveResult
from monopoly.core.player import Player
from monopoly.log import Log


@dataclass
class Card:
    text: str
    handler: Callable[['Player', 'Board', List['Player'], 'Log'], MoveResult]

    def apply(self, player: Player, board: Board, players: List[Player], log: Log) -> MoveResult:
        return self.handler(player, board, players, log)


def advance_to_x(player, board, players, log, target: int, collect_if_pass=True) -> MoveResult:
    log.add(f"{player} goes to {board.cells[target]}")
    if collect_if_pass and player.position > target:
        player.handle_salary(board, log)
    player.position = target
    return MoveResult.CONTINUE


def advance_to_nearest_utility(player: Player, board: Board, players: List[Player], log: Log) -> MoveResult:
    # utilities at (12, 28)
    if player.position < 12 or (player.position > 28):
        target = 12
    else:
        target = 28
    advance_to_x(player, board, players, log, target)
    return MoveResult.CONTINUE


def advance_to_nearest_railroad(player: Player, board: Board, players: List[Player], log: Log) -> MoveResult:
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
    return MoveResult.CONTINUE


def speeding_fine(player: Player, board: Board, players: List[Player], log: Log) -> MoveResult:
    log.add(f"{player} pays speeding fine $15")
    player.pay_money(15, "bank", board, log)
    return MoveResult.CONTINUE


def advance_to_go_handler(player, board, players, log):
    log.add(f"{player} goes to {board.cells[0]}")
    player.position = 0
    player.handle_salary(board, log)
    return MoveResult.CONTINUE


# Build the Chance deck using generic Card instances
CHANCE_CARDS: List[Card] = [
    Card("Advance to Go (Collect $200)", advance_to_go_handler),
    Card("Advance to Boardwalk", lambda p, b, pl, lg: advance_to_x(p, b, pl, lg, target=39, collect_if_pass=True)),
    Card("Advance to Illinois Avenue. If you pass Go, collect $200", lambda p, b, pl, lg: advance_to_x(p, b, pl, lg, target=24, collect_if_pass=True)),
    Card("Advance to St. Charles Place. If you pass Go, collect $200", lambda p, b, pl, lg: advance_to_x(p, b, pl, lg, target=11, collect_if_pass=True)),
    Card("Advance to Reading Railroad", lambda p, b, pl, lg: advance_to_x(p, b, pl, lg, target=5, collect_if_pass=True)),
    Card("Advance token to nearest Utility. If owned, throw dice and pay owner a total ten times amount thrown.", lambda p,b,pl, lg: advance_to_nearest_utility(p, b, pl, lg)),
    Card("Advance to the nearest Railroad. If owned, pay owner twice the rental to which they are otherwise entitled", )
    Card("Advance to the nearest Railroad. If owned, pay owner twice the rental to which they are otherwise entitled", )

    Card("Bank pays you dividend of $50", )
    Card("Get Out of Jail Free", )
    Card("Go Back 3 Spaces", )
    Card("Go to Jail. Go directly to Jail, do not pass Go, do not collect $200", )
    Card("Make general repairs on all your property. For each house pay $25. For each hotel pay $100", )
    Card("Speeding fine $15", speeding_fine),
    Card("Take a trip to Reading Railroad. If you pass Go, collect $200", )
    Card("You have been elected Chairman of the Board. Pay each player $50", )
    Card("Your building loan matures. Collect $150")
]

COMMUNITY_CHEST_CARDS = [ …]
