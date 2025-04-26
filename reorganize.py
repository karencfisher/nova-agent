import json
from tools.memory.core_memory import ContextMemory

context_memory = ContextMemory()

with open('tools\\memory\\agent_memory.json', 'r', encoding='utf-8') as FILE:
    agent_memory = json.load(FILE)
    
with open('tools\\memory\\memories.json', 'r', encoding='utf-8') as FILE:
    memories = json.load(FILE)
    
for key, value in memories.items():
    context_memory.store_memory({
        'key': key,
        'content': value
    })
    
    del agent_memory['human'][key]
    print(f"Moved {key} to context memory")
    
with open('tools\\memory\\agent_memory.json', 'w', encoding='utf-8') as FILE:
    json.dump(agent_memory, FILE)
    
