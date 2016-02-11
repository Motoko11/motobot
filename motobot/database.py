from pickle import load, dump, HIGHEST_PROTOCOL
from os import replace, mkdir, listdir
from os.path import exists, isdir
from time import time
from math import floor


class DatabaseEntry:
    def __init__(self):
        self.__data = None

    def get_val(self, default=None):
        return self.__data if self.__data is not None else default

    def set_val(self, value):
        self.__data = value


class Database:
    MINUTELY = 60
    HOURLY = MINUTELY * 60
    DAILY = HOURLY * 24
    WEEKLY = DAILY * 7
    MONTHLY = WEEKLY * 4

    backup_extension = '.bak'

    def __init__(self, database_path=None, backup_folder=None, backup_frequency=DAILY):
        self.database_path = database_path
        self.backup_folder = backup_folder
        self.backup_frequency = backup_frequency
        self.data = {}
        self.load_database()

    def load_database(self):
        if self.database_path is not None:
            try:
                with open(self.database_path, 'rb') as file:
                    self.data = load(file)
            except FileNotFoundError:
                self.write_database()

    def write_database(self, path=None):
        if path is None:
            path = self.database_path

        if path is not None:
            temp_path = path + '.temp'
            with open(temp_path, 'wb') as file:
                dump(self.data, file, HIGHEST_PROTOCOL)
            replace(temp_path, path)
            self.backup()

    def backup(self):
        if self.backup_folder is not None:
            if not exists(self.backup_folder):
                mkdir(self.backup_folder)

            last_backup = self.last_backup()
            current_time = int(floor(time()))

            if last_backup + self.backup_frequency < current_time:
                path = '{}/{}.{}{}'.format(self.backup_folder, self.database_path, current_time, Database.backup_extension)
                self.write_database(path)

    def last_backup(self):
        last_backup = 0

        for file in listdir(self.backup_folder):
            if file.startswith(self.database_path) and file.endswith(Database.backup_extension):
                backup = int(file[len(self.database_path)+1:-len(Database.backup_extension)])
                last_backup = backup if backup > last_backup else last_backup
        return last_backup

    def get_entry(self, name):
        if name not in self.data:
            self.data[name] = DatabaseEntry()
        return self.data[name]
