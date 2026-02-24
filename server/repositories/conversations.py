import json

from DB.nova_db import NovaDB


class Conversations:
    dbn = NovaDB()

### conversations
    @classmethod
    def get_conversations(cls):
        sql = '''
SELECT id, title FROM conversations
ORDER BY updated_at DESC;
'''
        return cls.dbn.execute_sql(sql, returns_data=True)

    @classmethod
    def add_conversation(cls, title):
        sql = f'''
INSERT INTO conversations (title)
VALUES ({title});
'''
        return cls.dbn.execute_sql(sql)

    @classmethod
    def update_conversation(cls, id, new_title):
        sql = f'''
UPDATE conversations
SET title = {new_title}
WHERE id = {id};
'''
        return cls.dbn.execute_sql(sql)

    @classmethod
    def delete_conversation(cls, id):
        sql = f'''
UPDATE conversations
SET deleted = 1
WHERE id = {id};
'''
        return cls.dbn.execute_sql(sql)

### messages
    @classmethod
    def get_messages(cls, conv_id):
        sql = f'''
SELECT role, content, meta_json FROM message
WHERE conversation_id = {conv_id}
AND evicted = 0;
'''
        return cls.dbn.execute_sql(sql, returns_data=True)

    @classmethod
    def add_message(cls, conv_id, message):
        message_dict = json.loads(message)

        role = message_dict['role']
        if isinstance(message_dict['content'], dict):
            content = message_dict['content']['text']
            meta_json = json.dumps(message_dict['content']['metadata'])
        else:
            content = message_dict['content']
            meta_json = None

        sql = f'''
INSERT INTO messages (conversation_id, role, content, meta_json)
VALUES ({conv_id}, {role}, {content}, {meta_json});
'''
        return cls.dbn.execute_sql(sql)

    @classmethod
    def evict_messages(cls, conv_id, count):
        sql = f'''
UPDATE messages
SET evicted = 1
WHERE id in (
    SELECT id FROM messages
    WHERE conversation_id = {conv_id} 
        AND evicted = 0
        AND role != 'system'
    ORDER BY id ASC
    LIMIT {count}
);
''' 
        return cls.dbn.execute_sql(sql)
