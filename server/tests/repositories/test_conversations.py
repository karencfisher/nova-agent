import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import unittest
from unittest.mock import patch, MagicMock
from repositories.conversations import Conversations
import json

class TestConversations(unittest.TestCase):

    @patch('repositories.conversations.Conversations.dbn')
    def test_add_conversation(self, mock_db):
        # Arrange
        mock_db.execute_sql.return_value = None
        title = "Test Conversation"

        # Act
        Conversations.add_conversation(title)

        # Assert
        mock_db.execute_sql.assert_called_once()
        executed_sql = mock_db.execute_sql.call_args[0][0]
        self.assertIn(f"INSERT INTO conversations (title)\nVALUES ({title});", executed_sql)

    @patch('repositories.conversations.Conversations.dbn')
    def test_get_conversations(self, mock_db):
        # Arrange
        mock_db.execute_sql.return_value = [(1, "Conversation 1"), (2, "Conversation 2")]

        # Act
        result = Conversations.get_conversations()

        # Assert
        mock_db.execute_sql.assert_called_once()
        self.assertEqual(result, [(1, "Conversation 1"), (2, "Conversation 2")])

    @patch('repositories.conversations.Conversations.dbn')
    def test_update_conversation(self, mock_db):
        # Arrange
        mock_db.execute_sql.return_value = None
        conversation_id = 1
        new_title = "Updated Conversation Title"

        # Act
        Conversations.update_conversation(conversation_id, new_title)

        # Assert
        mock_db.execute_sql.assert_called_once()
        executed_sql = mock_db.execute_sql.call_args[0][0]
        self.assertIn(f"UPDATE conversations\nSET title = {new_title}\nWHERE id = {conversation_id};", executed_sql)

    @patch('repositories.conversations.Conversations.dbn')
    def test_add_messages_to_conversation_1(self, mock_db):
        # Arrange
        mock_db.execute_sql.return_value = None
        conv_id = 1
        messages = [
            {"role": "system", "content": "System message"},
            {"role": "user", "content": {"text": "User message 1", "metadata": {"key": "value1"}}},
            {"role": "assistant", "content": "Assistant message 1"},
            {"role": "user", "content": {"text": "User message 2", "metadata": {"key": "value2"}}},
            {"role": "assistant", "content": "Assistant message 2"},
            {"role": "user", "content": {"text": "User message 3", "metadata": {"key": "value3"}}},
            {"role": "assistant", "content": "Assistant message 3"},
            {"role": "user", "content": {"text": "User message 4", "metadata": {"key": "value4"}}},
            {"role": "assistant", "content": "Assistant message 4"},
            {"role": "user", "content": {"text": "User message 5", "metadata": {"key": "value5"}}}
        ]

        # Act
        for message in messages:
            Conversations.add_message(conv_id, json.dumps(message))

        # Assert
        self.assertEqual(mock_db.execute_sql.call_count, len(messages))
        for i, call in enumerate(mock_db.execute_sql.call_args_list):
            executed_sql = call[0][0]
            self.assertIn(f"INSERT INTO messages (conversation_id, role, content", executed_sql)

    @patch('repositories.conversations.Conversations.dbn')
    def test_add_messages_to_conversation_2(self, mock_db):
        # Arrange
        mock_db.execute_sql.return_value = None
        conv_id = 2
        messages = [
            {"role": "user", "content": "User message 1"},
            {"role": "assistant", "content": "Assistant message 1"},
            {"role": "user", "content": "User message 2"},
            {"role": "assistant", "content": "Assistant message 2"},
            {"role": "user", "content": "User message 3"},
            {"role": "assistant", "content": "Assistant message 3"},
            {"role": "user", "content": "User message 4"},
            {"role": "assistant", "content": "Assistant message 4"},
            {"role": "user", "content": "User message 5"},
            {"role": "assistant", "content": "Assistant message 5"}
        ]

        # Act
        for message in messages:
            Conversations.add_message(conv_id, json.dumps(message))

        # Assert
        self.assertEqual(mock_db.execute_sql.call_count, len(messages))
        for i, call in enumerate(mock_db.execute_sql.call_args_list):
            executed_sql = call[0][0]
            self.assertIn(f"INSERT INTO messages (conversation_id, role, content", executed_sql)

    @patch('repositories.conversations.Conversations.dbn')
    def test_get_messages_for_conversation_1(self, mock_db):
        # Arrange
        conv_id = 1
        mock_db.execute_sql.return_value = [
            ("system", "System message", None),
            ("user", "User message 1", '{"key": "value1"}'),
            ("assistant", "Assistant message 1", None),
            ("user", "User message 2", '{"key": "value2"}'),
            ("assistant", "Assistant message 2", None),
            ("user", "User message 3", '{"key": "value3"}'),
            ("assistant", "Assistant message 3", None),
            ("user", "User message 4", '{"key": "value4"}'),
            ("assistant", "Assistant message 4", None),
            ("user", "User message 5", '{"key": "value5"}')
        ]

        # Act
        result = Conversations.get_messages(conv_id)

        # Assert
        mock_db.execute_sql.assert_called_once()
        executed_sql = mock_db.execute_sql.call_args[0][0]
        self.assertIn(f"SELECT role, content, meta_json FROM message\nWHERE conversation_id = {conv_id}", executed_sql)
        self.assertEqual(len(result), 10)
        self.assertEqual(result[0][0], "system")
        self.assertEqual(result[1][2], '{"key": "value1"}')
        self.assertEqual(result[2][2], None)

    @patch('repositories.conversations.Conversations.dbn')
    def test_evict_messages_from_conversation_1(self, mock_db):
        # Arrange
        conv_id = 1
        mock_db.execute_sql.return_value = None
        evict_count = 3

        # Act
        Conversations.evict_messages(conv_id, evict_count)

        # Assert
        mock_db.execute_sql.assert_called_once()
        executed_sql = mock_db.execute_sql.call_args[0][0]
        self.assertIn(f"UPDATE messages\nSET evicted = 1\nWHERE id in (\n    SELECT id FROM messages\n    WHERE conversation_id = {conv_id}", executed_sql)
        self.assertIn(f"LIMIT {evict_count}", executed_sql)

    @patch('repositories.conversations.Conversations.dbn')
    def test_delete_conversation_2(self, mock_db):
        # Arrange
        mock_db.execute_sql.return_value = None
        conversation_id = 2

        # Act
        Conversations.delete_conversation(conversation_id)

        # Assert
        mock_db.execute_sql.assert_called_once()
        executed_sql = mock_db.execute_sql.call_args[0][0]
        self.assertIn(f"UPDATE conversations\nSET deleted = 1\nWHERE id = {conversation_id};", executed_sql)

    @patch('repositories.conversations.Conversations.dbn')
    def test_get_messages_for_deleted_conversation_2(self, mock_db):
        # Arrange
        conv_id = 2
        mock_db.execute_sql.return_value = []

        # Act
        result = Conversations.get_messages(conv_id)

        # Assert
        mock_db.execute_sql.assert_called_once()
        executed_sql = mock_db.execute_sql.call_args[0][0]
        self.assertIn(f"SELECT role, content, meta_json FROM message\nWHERE conversation_id = {conv_id}", executed_sql)
        self.assertEqual(result, [])

    @patch('repositories.conversations.Conversations.dbn')
    def test_undelete_conversation_2(self, mock_db):
        # Arrange
        mock_db.execute_sql.return_value = None
        conversation_id = 2

        # Act
        Conversations.undelete_conversation(conversation_id)

        # Assert
        mock_db.execute_sql.assert_called_once()
        executed_sql = mock_db.execute_sql.call_args[0][0]
        self.assertIn(f"UPDATE conversations\nSET deleted = 0\nWHERE id = {conversation_id};", executed_sql)

    @patch('repositories.conversations.Conversations.dbn')
    def test_get_messages_for_undeleted_conversation_2(self, mock_db):
        # Arrange
        conv_id = 2
        mock_db.execute_sql.return_value = [
            ("user", "User message 1", '{"key": "value1"}'),
            ("assistant", "Assistant message 1", None),
            ("user", "User message 2", '{"key": "value2"}')
        ]

        # Act
        result = Conversations.get_messages(conv_id)

        # Assert
        mock_db.execute_sql.assert_called_once()
        executed_sql = mock_db.execute_sql.call_args[0][0]
        self.assertIn(f"SELECT role, content, meta_json FROM message\nWHERE conversation_id = {conv_id}", executed_sql)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0][2], '{"key": "value1"}')

if __name__ == "__main__":
    unittest.main()