from uuid import uuid4
import os
import json
from utils.timer import timer

class ChatMemory:
    def __init__(self, sys_prompt, agent_memory, max_messages=100):
        self.chat_memory = [
            # system prompt 
            {
                "role": "system", "content": f'{sys_prompt}\n#MEMORY\n {json.dumps(agent_memory)}]'
            }
        ]    
        
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
        return self.chat_memory + self.messages
    
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
    
        


        
    