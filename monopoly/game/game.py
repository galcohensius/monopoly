""" Function that wraps one game of monopoly:
1. Setting up the board,
2. Players
3. Making moves by all players
"""
from typing import Tuple

from monopoly.game.game_utils import _check_end_game_conditions, setup_players, setup_game
from monopoly.game.move_result import MoveResult
from settings import SimulationSettings


def monopoly_game(game_number_and_seeds: Tuple[int, int]) -> None:
    """
    Simulate one game of Monopoly:

    1. Setting up the board
    2. Initializing players
    3. Running turns until one of:
       I. Win: Only one player remains non-bankrupt
       II. All Rich: all non-bankrupt players have more cash than `never_bankrupt_cash`
       III. Turn limit reached (`SimulationSettings.n_moves`)
    """
    game_number, game_seed = game_number_and_seeds
    board, dice, events_log, bankruptcies_log = setup_game(game_number, game_seed)
    players = setup_players(board, dice)  # Set up players with their behavior settings, starting money and properties.
    
    for turn_n in range(1, SimulationSettings.n_moves + 1):
        events_log.add(f"= GAME {game_number} Turn {turn_n} =")

        if _check_end_game_conditions(players, events_log, game_number, turn_n):
            break
        
        # Players make their moves
        for player in players:
            if not player.is_bankrupt:
                move_result, move_log = player.make_a_move(board, players, dice, events_log, game_number, turn_n)
                events_log.add(move_log)
                if move_result == MoveResult.BANKRUPT:
                    bankruptcies_log.add(f"{game_number}\t{player}\t{turn_n}")
    
    board.log_current_map(events_log)  # log the final game state
    events_log.save()
    if bankruptcies_log.content:
        bankruptcies_log.save()
