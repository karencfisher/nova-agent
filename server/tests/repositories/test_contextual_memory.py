import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import unittest
from pathlib import Path
import json

from repositories.contextual_memory import ContextualMemory
from DB.migrate import migrate_db
from DB.nova_db import NovaDB


def setUpModule():
    migrate_db('test_db.db', 'schema.sql', replace=True)
    ContextualMemory.dbn = NovaDB('test_db.db')

class TestContextualMemory(unittest.TestCase):
    @classmethod
    def tearDown(cls):
        db = ContextualMemory.dbn
        db.execute_sql("DELETE FROM memory_items;")
        db.execute_sql("DELETE FROM sqlite_sequence WHERE name='memory_items';")

    def test_add_retrieve_1(self):
        # store one text and get it back
        text = '''
The user and assistant have discussed the weather on March 1, Sunday, in Moab.
It was cloudy but warm, in the sixties, but the user still felt too chilly to
ride her trike to town. They then discussed her current project.
'''
        result = ContextualMemory.add_memory(text)
        self.assertEqual(result['error'], None, f"Error saving: {result['error']}")

        result = ContextualMemory.retrieve_memories('what is the weather')
        self.assertEqual(result['error'], None, f"Error retrieving: {result['error']}")
        self.assertEqual(result['data'][0]['text'], text)
