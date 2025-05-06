""" Function that wraps one game of monopoly:
1. Setting up the board,
2. Players
3. Making moves by all players
"""
from typing import Tuple

from monopoly.core.move_result import MoveResult
from monopoly.core.game_utils import _check_end_game_conditions, log_players_and_board_state, \
    setup_players, setup_game
from settings import SimulationSettings


def monopoly_game(game_number_and_seeds: Tuple[int,int]) -> None:
    """ Simulation of one game.
    For convenience to set up a multi-thread,
    parameters are packed into a tuple: (game_number, game_seed):
    - "game number" is here to print out in the game log
    - "game_seed" to initialize random generator for the game
    """
    game_number, game_seed = game_number_and_seeds
    board, dice, events_log, bankruptcies_log = setup_game(game_number, game_seed)
    players = setup_players(board, dice)  # Set up players with their behavior settings, starting money and properties.

    # Play the game until:
    # 1. Win: Only 1 player did not bankrupt
    # 2. Several survivors: All non-bankrupt players have more cash than `never_bankrupt_cash`
    # 3. Turn limit reached
    for turn_n in range(1, SimulationSettings.n_moves + 1):
        events_log.add(f"\n== GAME {game_number} Turn {turn_n} ===")
        log_players_and_board_state(board, events_log, players)
        board.log_board_state(events_log)
        events_log.add("")

        if _check_end_game_conditions(players, events_log, game_number, turn_n):
            break

        # Players make their moves
        for player in players:
            if not player.is_bankrupt:
                move_result = player.make_a_move(board, players, dice, events_log)
                if move_result == MoveResult.BANKRUPT:
                    bankruptcies_log.add(f"{game_number}\t{player}\t{turn_n}")

    # log the final game state
    board.log_current_map(events_log)
    events_log.save()
    if bankruptcies_log.content:
        bankruptcies_log.save()


