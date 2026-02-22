import json

from .base_agent import BaseAgent
from chat_context.chat_memory import ChatMemory
from tools.memory.core_memory import CoreMemory
from intents.prompt_augmentation import PromptAugmentation


class MainAgent(BaseAgent):
    def __init__(self, message_queue, api_key, model='gpt-5-nano'):
        self.model = model

        with open('system_prompt.txt', 'r') as FILE:
            system_prompt = FILE.read()

        chat_memory = ChatMemory(
            system_prompt, 
            CoreMemory.agent_memory,
            persist=True)
        
        super(MainAgent, self).__init__(
            message_queue, 
            api_key, 
            chat_memory, 
            model=model,
            reasoning_level='medium', 
            tools=['all']
        )
    
    def preprocess_messages(self, messages, reasoning_level):
        if messages[-1]['role'] == 'user':
            user_message = messages[-1]
            structured_prompt = user_message.copy()
            augmented_prompt = PromptAugmentation.make_structured_prompt(
                user_message['content'])
            structured_prompt['content'] = json.dumps(augmented_prompt)
            messages = messages[:-1] + [structured_prompt]

            intent = augmented_prompt['metadata']['intent']
            if intent['label'] in ['support', 'chitchat']:
                reasoning_level = 'minimal'

        return messages, reasoning_level
