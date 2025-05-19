from typing import List

from monopoly.board.board import Board
from monopoly.game.dice import Dice

from monopoly.player.player import Player
from monopoly.log import Log
from log_settings import LogSettings
from settings import SimulationSettings, GameSettings, GameMechanics


def assign_property(player, property_to_assign, board):
    """ Assigns a property to a player and updates the board state and check if a multiplier needs to be updated."""
    property_to_assign.owner = player
    player.owned.append(property_to_assign)
    board.recalculate_monopoly_multipliers(property_to_assign)
    player.update_lists_of_properties_to_trade(board)


def _check_end_game_conditions(players: List[Player], log: Log, game_number, turn_n) -> bool:
    """
    Return True when:
      1) fewer than 2 players remain, or
      2) all rich: all non-bankrupt players have > never_bankrupt_cash.
    Logs the reason before returning.
    """
    alive = [p for p in players if not p.is_bankrupt]
    n_alive = len(alive)

    # 1) fewer than 2 players left
    if n_alive < 2:
        log.add(f"Only {n_alive} alive player remains, game over")
        return True

    # 2) everyone is above the never_bankrupt_cash threshold
    threshold = SimulationSettings.never_bankrupt_cash
    if all(p.money > threshold for p in alive):
        log.add(
            f"== All Rich ==: GAME {game_number}, Turn {turn_n}: all non-bankrupt players have more than {threshold}$, this game will never end")
        return True
    return False


def log_game_state(board, log, players, game_number, turn_n):
    """ Current player's position, money and net worth, looks like this:
         For example: Player 'Hero': $1220 (net $1320), at 21 (E1 Kentucky Avenue)"""
    if turn_n % 10 == 1:
        log.add(f"\n== GAME {game_number} Turn {turn_n} === (houses/hotels available: {board.available_houses}/{board.available_hotels}) ==")
        for player_n, player in enumerate(players):
            if not player.is_bankrupt:
                log.add(f"- {player.name}: " +
                        f"${int(player.money)} (net ${player.net_worth()}), at {board.cells[player.position].name} ({player.position})")
        log.add("")
    else:
        log.add(f"\n= GAME {game_number} Turn {turn_n} =")


def setup_players(board, dice):
    players = [Player(player_name, player_setting)
               for player_name, player_setting in GameSettings.players_list]

    if GameSettings.shuffle_players:
        dice.shuffle(players)  # dice has a thread-safe copy of random.shuffle

    # Set up players starting money according to the game settings:
    # Supports either a dict (money per-player) or single value
    starting_money = GameSettings.starting_money
    if isinstance(starting_money, dict):
        for player in players:
            player.money = starting_money.get(player.name, 0)
    # If starting money is a single value, assign it to all players
    else:
        for player in players:
            player.money = starting_money

    # set up players' initial properties
    for player in players:
        property_indices = GameSettings.starting_properties.get(player.name, [])
        for cell_index in property_indices:
            assign_property(player, board.cells[cell_index], board)

    return players


def setup_game(game_number, game_seed):
    events_log = Log(LogSettings.EVENTS_LOG_PATH, disabled=not LogSettings.KEEP_GAME_LOG)
    events_log.add(f"GAME {game_number} of {SimulationSettings.n_games} (seed = {game_seed})")

    bankruptcies_log = Log(LogSettings.BANKRUPTCIES_PATH)

    # Initialize the board (plots, chance, community chest etc.)
    board = Board(GameSettings)
    dice = Dice(game_seed, GameMechanics.dice_count, GameMechanics.dice_sides, events_log)
    dice.shuffle(board.chance.cards)
    dice.shuffle(board.chest.cards)
    return board, dice, events_log, bankruptcies_log
