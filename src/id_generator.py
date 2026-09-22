from threading import Lock

ID = int


class IDGenerator:
    def __init__(self):
        self._current_id = 1
        self._id_lock = Lock()

    def get_current_id(self) -> ID:
        with self._id_lock:
            return self._current_id

    def get_next_id(self) -> ID:
        with self._id_lock:
            current = self._current_id
            self._current_id += 1
            return current

    def reset(self, start: ID = 1):
        with self._id_lock:
            self._current_id = start
