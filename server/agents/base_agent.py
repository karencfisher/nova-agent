import json
from queue import Queue
from threading import Thread
from openai import OpenAI

from utils.timer import timer
from tools.tool_specs import tool_specs


class BaseAgent:
    def __init__(self, message_queue, api_key, chat_memory,
                 model='gpt-5-nano', reasoning_level='minimal', tools=[]):
        self.reasoning_level = reasoning_level
        self.chat_memory = chat_memory

        self.client = OpenAI(api_key=api_key)
        self.model = model
        
        # Builds agent's tool collection
        self.tools_metadata = []
        self.tools = {}
        for spec in tool_specs:
            # If tools limited, skip unapproved tools
            if tools != ['all'] and spec['name'] not in tools:
                continue
            self.tools_metadata.append(spec['metadata'])
            self.tools[spec['name']] = spec['tool']
            
        self.message_queue = message_queue
        self.tool_queue = Queue()

    @timer
    def agent_step(self, user_message):
        assert self.chat_memory is not None, 'Not implemented'

        if user_message is None or user_message == '':
            return
        
        self.chat_memory.append({
            "role": "user",
            "content": user_message
        })
        
        while True:
            messages, reasoning_level = self.preprocess_messages(
                self.chat_memory.get_chat_memory(), 
                self.reasoning_level
            )
            response = self.call_LLM(messages, reasoning_level)
            response = self.postprocess_response(response)
            
            # update the messages with the agent's response
            self.chat_memory.append(response.message.model_dump())
            
            # if NOT calling a tool (responding to the user), return 
            if not response.message.tool_calls:
                self.message_queue.put({
                    'content': response.message.content.replace('\n', '|'),
                    'final': True
                })
                break

            # if calling a tool, execute the tool
            else:
                if response.message.content is None:
                    print('Response was None')
                else:
                    self.message_queue.put({
                        'content': response.message.content.replace('\n', '|'),
                        'final': False
                    })

                # parse the arguments from the LLM function call
                for tool_call in response.message.tool_calls:
                    print(f'TOOL CALL: {tool_call.function}')
                    tool_thread = Thread(target=self.__call_tool, args=(tool_call,))
                    tool_thread.start()
                    
                    while True:
                        returned_content = self.tool_queue.get()
                        if not returned_content['done']:
                            self.message_queue.put({
                                'content': returned_content['text'],
                                'final': False
                        })
                        else:
                            break

                    # add the tool call response to the message history 
                    self.chat_memory.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id, 
                        "name": tool_call.function.name, 
                        "content": returned_content['text']
                    })

    def preprocess_messages(self, messages, reasoning_level):
        return messages, reasoning_level
    
    def call_LLM(self, messages, reasoning_level):
        assert self.chat_memory is not None, 'Not implemented'
        
        print(f'\nPrompt: {messages[-1]}')
        chat_completion = self.client.chat.completions.create(
            model=self.model,
            temperature=1,
            reasoning_effort=reasoning_level,
            messages=messages,
            tools=self.tools_metadata,
            tool_choice="auto"
        )
        return chat_completion.choices[0]
    
    def postprocess_response(self, response):
        return response
                    
    def __call_tool(self, tool_call):
        arguments = json.loads(
            tool_call.function.arguments
        )

        # Inject tool queue 
        arguments['tool_queue'] = self.tool_queue

        func = self.tools[tool_call.function.name]
        returned_content = func(**arguments)
        self.tool_queue.put(returned_content)
        


        
    
    