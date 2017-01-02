from collections import defaultdict


class SessionEntry:
    def __init__(self):
        self.data = None

    def get(self, default=None):
        self.data = default if self.data is None else self.data
        return self.data

    def set(self, data):
        self.data = data


class Session:
    def __init__(self):
        self.data = defaultdict(SessionEntry)

    def get_entry(self, name):
        return self.data[name]
