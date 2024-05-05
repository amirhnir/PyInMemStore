import threading
import time
import pickle

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class PyInMemStore(metaclass=SingletonMeta):
    def __init__(self, persistence_file="data.pickle"):
        self.data = {}
        self.lock = threading.Lock()
        self.persistence_file = persistence_file
        self.load_from_disk()
        self.start_expiry_timer()

    def execute_command(self, command):
        command_parts = command.split()
        command_name, *args = command_parts

        if command_name in ['SET', 'GET', 'DELETE', 'EXPIRE', 'TTL', 'HELP', 'PERSIST']:
            return getattr(self, command_name)(*args)
        else:
            return f"Error: Unknown command '{command_name}'.\nIf you need assistance, type HELP for guidance. "

    def SET(self, key, value):
        with self.lock:
            self.data[key] = {'value': value, 'expiry_time': None}

    def GET(self, key):
        with self.lock:
            return self.data.get(key, {}).get('value', None)

    def DELETE(self, key):
        with self.lock:
            self.data.pop(key, None)

    def EXPIRE(self, key, seconds):
        with self.lock:
            if key in self.data:
                self.data[key]['expiry_time'] = time.time() + int(seconds)

    def TTL(self, key):
        with self.lock:
            if key in self.data:
                expiry_time = self.data[key]['expiry_time']
                if expiry_time is None:
                    return -1
                elif expiry_time > time.time():
                    return int(expiry_time - time.time())
                else:
                    self.data.pop(key, None)
                    return -2
            else:
                return -2

    def PERSIST(self):
        if self.persistence_file:
            with open(self.persistence_file, 'wb') as file:
                pickle.dump(self.data, file)

    def HELP(self):
        return """
        Available Commands:
        - SET key value: Stores the value at the specified key. Overwrites any existing value.
        - GET key: Returns the value associated with the key. If the key does not exist, return None.
        - DELETE key: Removes the key from the data store if it exists.
        - EXPIRE key seconds: Sets a key's time to live in seconds. After the time expires, the key
          will automatically be deleted.
        - TTL key: Returns the remaining time to live (in seconds) of a key that has a timeout.
          Return -1 if the key exists but does not have a timeout. Return -2 if the key does not exist.
        - PERSIST: Manually persist the current state of the data store to disk.
        - HELP: Display this help message.

        Note: The command names are case-sensitive.

        Note: Instead of using command-line syntax, you can also call methods directly by importing pyinmemstore.py file.
              Example: For SET command, use PyInMemStore().SET('key', 'value')
                       For GET command, use PyInMemStore().GET('key')
        """

    def load_from_disk(self):
        try:
            with open(self.persistence_file, 'rb') as file:
                self.data = pickle.load(file)
        except (FileNotFoundError, pickle.UnpicklingError):
            pass

    def start_expiry_timer(self):
        timer = threading.Timer(1, self.check_expiry_loop)
        timer.daemon = True
        timer.start()

    def check_expiry_loop(self):
        with self.lock:
            current_time = time.time()
            expired_keys = [key for key, data in self.data.items() if data['expiry_time'] and data['expiry_time'] <= current_time]
            for key in expired_keys:
                self.data.pop(key)
        self.start_expiry_timer()
