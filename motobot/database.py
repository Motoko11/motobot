from pickle import load, dump, HIGHEST_PROTOCOL
from os import replace


class DatabaseEntry:
    def __init__(self, database):
        self.__database = database
        self.__data = None

    def get_val(self, default=None):
        return self.__data if self.__data is not None else default

    def set_val(self, value):
        self.__data = value
        self.__database.changed = True


class Database:
    def __init__(self, database_path=None):
        self.database_path = database_path
        self.data = {}
        self.changed = False
        self.load_database()

    def load_database(self):
        if self.database_path is not None:
            try:
                file = open(self.database_path, 'rb')
                self.data = load(file)
            except FileNotFoundError:
                self.changed = True
                self.write_database()

    def write_database(self):
        if self.database_path is not None and self.changed:
            temp_path = self.database_path + '.temp'
            file = open(temp_path, 'wb')
            dump(self.data, file, HIGHEST_PROTOCOL)
            file.close()
            replace(temp_path, self.database_path)
            self.changed = False

    def get_entry(self, name):
        if name not in self.data:
            self.data[name] = DatabaseEntry(self)
        return self.data[name]
