from itertools import count
from threading import Lock
from copy import copy

ID = int


class IDGenerator:
    def __init__(self):
        self._id_generator = count(start=1)
        self._id_lock = Lock()

    def get_current_id(self) -> ID:
        with self._id_lock:
            return next(copy(self._id_generator))

    def get_next_id(self) -> ID:
        with self._id_lock:
            return next(self._id_generator)

    def reset(self, start: ID = 1):
        with self._id_lock:
            self._id_generator = count(start=start)
