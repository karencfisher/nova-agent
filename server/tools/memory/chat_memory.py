from uuid import uuid4
import os
import json
from utils.timer import timer

class ChatMemory:
    def __init__(self, sys_prompt, agent_memory, max_messages=100):
        self.agent_memory = agent_memory
        self.sys_prompt = sys_prompt
        
        if os.path.exists('tools\\memory\\chat_messages.json'):
            with open('tools\\memory\\chat_messages.json', 'r', encoding='utf-8') as FILE:
                self.messages = json.load(FILE)
        else:
            self.messages = []
        self.max_messages = max_messages
    
    def append(self, data):
        self.messages.append(data)
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
        self.__write_messages()
        
    def get_chat_memory(self):
        system_block = [{
            "role": "system",
            "content": f'{self.sys_prompt}\n\n#CORE MEMORY\n {json.dumps(self.agent_memory)}]'
        }]
        return system_block + self.messages
    
    def get_last_message(self):
        if len(self.messages) > 0:
            return self.messages[-1]
        else:
            return None
           
    def __write_messages(self):
        messages = self.__filter_messages(self.messages)
        with open('tools\\memory\\chat_messages.json', 'w', encoding='utf-8') as FILE:
            json.dump(messages, FILE)
        
    def __filter_messages(self, messages):
        filtered_messages = [
            {
                'role': message['role'], 'content': message['content']
            }
            for message in messages if (
                message['role'] in ['user', 'assistant'] and 
                message['content'] is not None
            )
        ]
        return filtered_messages
    
        


        
    