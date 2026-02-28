import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import unittest
from pathlib import Path
import json

from repositories.conversations import Conversations
from DB.migrate import migrate_db
from DB.nova_db import NovaDB


def setUpModule():
    migrate_db('test_db.db', 'schema.sql', replace=True)
    Conversations.dbn = NovaDB('test_db.db')

class TestConversations(unittest.TestCase):
    def tearDown(self):
        db = Conversations.dbn
        db.execute_sql("DELETE FROM conversations;")
        db.execute_sql("DELETE FROM sqlite_sequence WHERE name='conversations';")
    
    def test_add_conversation(self):
        result = Conversations.add_conversation('conversation1')
        self.assertEqual(result['error'], None, f"Add 1 Error: {result['error']}" )
        result = Conversations.add_conversation('conversation2')
        self.assertEqual(result['error'], None, f"Add 2 Error: {result['error']}" )

        result = Conversations.get_conversations()
        self.assertEqual(result['error'], None, f"get Error: {result['error']}")
        self.assertEqual(len(result['data']), 2, 'Did not create 2 conversations')
        self.assertDictEqual(result['data'][0], {'id': 2, 'title': 'conversation2'})

    def test_update_conversation(self):
        Conversations.add_conversation('conversation1')

        result = Conversations.update_conversation(1, 'new title')
        self.assertEqual(result['error'], None, f"Error: {result['error']}")

        result = Conversations.get_conversations()
        self.assertDictEqual(result['data'][0], {'id': 1, 'title': 'new title'})

    def test_delete_undelete_conversation(self):
        Conversations.add_conversation('conversation1')
        Conversations.add_conversation('conversation2')

        result = Conversations.delete_conversation(1)
        self.assertEqual(result['error'], None, f"Delete Error: {result['error']}")

        result = Conversations.get_conversations()
        self.assertEqual(len(result['data']), 1)
        self.assertDictEqual(result['data'][0], {'id': 2, 'title': 'conversation2'})

        result = Conversations.undelete_conversation(1)
        self.assertEqual(result['error'], None, f"Undelete Error: {result['error']}")

        result = Conversations.get_conversations()
        self.assertEqual(len(result['data']), 2)


class TestDeletions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Conversations.add_conversation('conversation1')
        Conversations.add_conversation('conversation2')

    @classmethod
    def tearDownClass(cls):
        db = Conversations.dbn
        db.execute_sql("DELETE FROM conversations;")
        db.execute_sql("DELETE FROM sqlite_sequence WHERE name='conversations';")

    def tearDown(self):
        db = Conversations.dbn
        db.execute_sql("DELETE FROM messages;")
        db.execute_sql("DELETE FROM sqlite_sequence WHERE name='messages';")

    def test_add_messages(self):
        for conv_id in range(1, 3):
            for i in range(1, 4):
                msg = {'role': 'user', 'content': f'conversation{conv_id} - message{i}'}
                result = Conversations.add_message(conv_id, json.dumps(msg))
                self.assertEqual(result['error'], None, f"Failed add {conv_id}-{i}")
        
        for conv_id in range(1, 3):
            results = Conversations.get_messages(conv_id)
            self.assertEqual(results['error'], None, f"{conv_id}")
            self.assertEqual(len(results['data']), 3, f"Failed get conv {conv_id}")
            for i, result in enumerate(results['data']):
                msg = {'role': 'user', 'content': f'conversation{conv_id} - message{i+1}', 'meta_json': None}
                self.assertDictEqual(result, msg, f"Mismatch {conv_id}-{i+1}")

    def test_add_messages_meta_json(self):
        for i in range(1, 4):
            msg = {'role': 'user', 'content': {
                   'text': f'message {i}',
                   'metadata': {'key': f'key{i}', 'value': f'value{i}'}}, 
            }
            result = Conversations.add_message(1, json.dumps(msg))
            self.assertEqual(result['error'], None, f"Failed add msg{i}")

        results = Conversations.get_messages(1)
        for i, result in enumerate(results['data']):
            msg = {'role': 'user', 
                   'content': f'message {i+1}',
                   'meta_json': {'key': f'key{i+1}', 'value': f'value{i+1}'}
            }
            self.assertDictEqual(result, msg, f"Mismatch msg{i+1}")

    def test_evict_messages(self):
        for i in range(1, 11):
            msg = {'role': 'user', 'content': {
                   'text': f'message {i}',
                   'metadata': {'key': f'key{i}', 'value': f'value{i}'}}, 
            }
            result = Conversations.add_message(1, json.dumps(msg))
            self.assertEqual(result['error'], None, f"Failed add msg{i}")

        results = Conversations.get_messages(1)
        self.assertEqual(len(results['data']), 10)

        result = Conversations.evict_messages(1, 5)
        self.assertEqual(result['error'], None, f"Failed evict 5")

        results = Conversations.get_messages(1)
        self.assertEqual(len(results['data']), 5)

        result = Conversations.evict_messages(1, 2)
        self.assertEqual(result['error'], None, f"Failed evict 5")

        results = Conversations.get_messages(1)
        self.assertEqual(len(results['data']), 3)
        


if __name__ == "__main__":
    unittest.main()