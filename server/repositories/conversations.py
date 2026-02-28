import json

from DB.nova_db import NovaDB


class Conversations:
    dbn = NovaDB()

### conversations
    @classmethod
    def get_conversations(cls):
        sql = '''
SELECT id, title FROM conversations
WHERE deleted = 0
ORDER BY id DESC;
'''
        return cls.dbn.execute_sql(sql, returns_data=True)

    @classmethod
    def add_conversation(cls, title):
        sql = f'''
INSERT INTO conversations (title)
VALUES (?);
'''
        params = (title,)
        return cls.dbn.execute_sql(sql, params)

    @classmethod
    def update_conversation(cls, id, new_title):
        sql = f'''
UPDATE conversations
SET title = ?,
    updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
WHERE id = ?;
'''
        params = (new_title, id)
        return cls.dbn.execute_sql(sql, params)

    @classmethod
    def delete_conversation(cls, id):
        sql = f'''
UPDATE conversations
SET deleted = 1
WHERE id = ?;
'''
        params = (id,)
        return cls.dbn.execute_sql(sql, params)
    
    @classmethod
    def undelete_conversation(cls, id):
        sql = f'''
UPDATE conversations
SET deleted = 0
WHERE id = ?;
'''
        params = (id,)
        return cls.dbn.execute_sql(sql, params)

### messages
    @classmethod
    def get_messages(cls, conv_id):
        sql = f'''
SELECT role, content, meta_json FROM messages
WHERE conversation_id = ?
AND evicted = 0;
'''
        params = (conv_id,)
        results = cls.dbn.execute_sql(sql, params, returns_data=True)
        for result in results['data']:
            if result['meta_json'] is not None:
                result['meta_json'] = json.loads(result['meta_json'])
        return results

    @classmethod
    def add_message(cls, conv_id, message):
        message_dict = json.loads(message)

        role = message_dict['role']
        if role == 'user' and isinstance(message_dict['content'], dict):
            content = message_dict['content']['text']
            meta_json = json.dumps(message_dict['content']['metadata'])
        else:
            content = message_dict['content']
            meta_json = None

        sql = f'''
INSERT INTO messages (conversation_id, role, content, meta_json)
VALUES (?, ?, ?, ?);
'''
        params = (conv_id, role, content, meta_json)
        return cls.dbn.execute_sql(sql, params)

    @classmethod
    def evict_messages(cls, conv_id, count):
        sql = f'''
UPDATE messages
SET evicted = 1
WHERE id in (
    SELECT id FROM messages
    WHERE conversation_id = ? 
        AND evicted = 0
        AND role != 'system'
    ORDER BY id ASC
    LIMIT ?
);
''' 
        params = (conv_id, count)
        return cls.dbn.execute_sql(sql, params)
