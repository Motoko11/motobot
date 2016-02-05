from pickle import load, dump, HIGHEST_PROTOCOL
from os import replace


class DatabaseEntry:
    def __init__(self):
        self.__data = None

    def get_val(self, default=None):
        return self.__data if self.__data is not None else default

    def set_val(self, value):
        self.__data = value


class Database:
    def __init__(self, database_path=None):
        self.database_path = database_path
        self.data = {}
        self.load_database()

    def load_database(self):
        if self.database_path is not None:
            try:
                with open(self.database_path, 'rb') as file:
                    self.data = load(file)
            except FileNotFoundError:
                self.write_database()

    def write_database(self):
        if self.database_path is not None:
            temp_path = self.database_path + '.temp'
            with open(temp_path, 'wb') as file:
                dump(self.data, file, HIGHEST_PROTOCOL)
            replace(temp_path, self.database_path)

    def get_entry(self, name):
        if name not in self.data:
            self.data[name] = DatabaseEntry()
        return self.data[name]
