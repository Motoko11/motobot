from json import dump, load
from os import remove, rename


class Database:
    def __init__(self, database_path=None):
        self.database_path = database_path
        self.data = {}
        self.load_database()

    def load_database(self):
        if self.database_path is not None:
            try:
                f = open(self.database_path, 'r')
                self.data = load(f)
            except:
                pass

    def get_val(self, name, default=None):
        return self.data.get(name, default)

    def set_val(self, name, val):
        self.data[name] = val

        if self.database_path is not None:
            temp_name = self.database_path + '.temp',
            f = open(temp_name, 'w')
            dump(f, self.data, indent=2)
            f.close()
            remove(self.database_path)
            rename(temp_name, self.database_path)
