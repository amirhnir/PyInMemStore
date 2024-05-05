import unittest
import time
import os
from pyinmemstore import PyInMemStore

class TestPyInMemStore(unittest.TestCase):
    def setUp(self):
        self.persistence_file = 'test_data.pickle'
        self.store = PyInMemStore(self.persistence_file)

    def tearDown(self):
        if os.path.exists(self.persistence_file):
            os.remove(self.persistence_file)

    def test_set_and_get(self):
        self.store.SET('test_key', 'test_value')
        result = self.store.GET('test_key')
        self.assertEqual(result, 'test_value')

    def test_delete(self):
        self.store.SET('test_key', 'test_value')
        self.store.DELETE('test_key')
        result = self.store.GET('test_key')
        self.assertIsNone(result)

    def test_expire_and_ttl(self):
        self.store.SET('test_key', 'test_value')
        self.store.EXPIRE('test_key', 2)
        ttl_result = self.store.TTL('test_key')
        self.assertGreaterEqual(ttl_result, 0)
        time.sleep(3)
        ttl_result_after_expire = self.store.TTL('test_key')
        self.assertEqual(ttl_result_after_expire, -2)
        result = self.store.GET('test_key')
        self.assertIsNone(result)

    def test_persist_and_load_from_disk(self):
        self.store.SET('test_key', 'test_value')
        self.store.PERSIST()
        loaded_store = PyInMemStore(self.persistence_file)
        result = loaded_store.GET('test_key')
        self.assertEqual(result, 'test_value')

if __name__ == '__main__':
    unittest.main()
