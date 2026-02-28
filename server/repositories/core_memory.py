import json

from DB.nova_db import NovaDB


class CoreMemory:
    dbn = NovaDB()

    @classmethod
    def get_memories(cls, roles=['user', 'agent'], activated=True):
        sql = f'''
SELECT id, role, key, value FROM core_memories
WHERE role in {roles}
      AND activated = {int(activated)}
ORDER BY role, id;
'''
        return cls.dbn.execute_sql(sql, returns_data=True)
    
    @classmethod
    def get_memory_id(cls, memory, activated=True):
        sql = f'''
SELECT id FROM core_memories
WHERE role = {memory['role']}
      AND key = {memory['key']}
      AND activated = {int(activated)};
'''
        return cls.dbn.execute_sql(sql, returns_data=True)

    @classmethod
    def add_memory(cls, memory):
        memory_dict = json.loads(memory)
        sql = f'''
INSERT INTO core_memories (role, key, value)
VALUES ({memory_dict['role']}, {memory_dict['key'], {memory_dict['value']}})
ON CONFLICT(role, key)
DO UPDATE SET
    value = excluded.value,
    updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now');
'''
        return cls.dbn.execute_sql(sql)
    
    @classmethod
    def deactivate(cls, id):
        sql = f'''
UPDATE core_memories
SET is_active = 0
WHERE id = {id};
'''
        return cls.dbn.execute_sql(sql)
    
    @classmethod
    def activate(cls, id):
        sql = f'''
UPDATE core_memories
SET is_active = 1
WHERE id = {id};
'''
        return cls.dbn.execute_sql(sql)
    