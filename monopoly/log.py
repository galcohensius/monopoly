""" Class to keep a log of the game.
The challenge here was to make it thread-safe: simulator plays several games at a time,
but the game log should be written by "whole game" chunks. This is the reason games
will not be in order, as the order games start is different from the order they finish.
"""

import multiprocessing
from os import PathLike
from typing import Union


class Log:
    """ Class to handle logging of game events, Thread-safe: writes whole batches under a single lock. """
    lock = multiprocessing.Lock()

    def __init__(self,
                 log_file_name: Union[str, PathLike] = "log.txt",
                 disabled: bool = False):
        self.log_file_name = log_file_name
        self.content = []
        self.disabled = disabled

    def add(self, data):
        """ Add one line to the in‐memory buffer. """
        if self.disabled:
            return
        line = str(data).rstrip("\n") + "\n"
        self.content.append(line)

    def save(self):
        """ Write out the log to the file, then clear the in‐memory buffer. """
        if self.disabled or not self.content:
            return

        with self.lock:
            with open(self.log_file_name, "a", encoding="utf-8") as logfile:
                for line in self.content:
                    logfile.write(line)
        self.content.clear()

    def reset(self, first_line=""):
        """ Empty the log file. optionally write a single header line. """
        with self.lock:
            with open(self.log_file_name, "w", encoding="utf-8") as logfile:
                if first_line:
                    logfile.write(f"{first_line}\n")
        self.content.clear()
