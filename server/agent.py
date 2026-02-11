import os
import json
from queue import Queue, Empty
from threading import Thread
from dotenv import load_dotenv
from openai import OpenAI
from tools.memory.core_memory import CoreMemory
from tools.memory.chat_memory import ChatMemory
from tool_specs import tool_specs
from utils.timer import timer


class Agent:
    def __init__(self, message_queue):
        load_dotenv()
        self.client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
        )
        self.model = "gpt-5-nano"
        
        with open('system_prompt.txt', 'r') as FILE:
            system_prompt_os = FILE.read()
            
        self.chat_memory = ChatMemory(system_prompt_os, CoreMemory.agent_memory)
        
        self.tools_metadata = []
        self.tools = {}
        for spec in tool_specs:
            self.tools_metadata.append(spec['metadata'])
            self.tools[spec['name']] = spec['tool']
            
        self.message_queue = message_queue
        self.tool_queue = Queue()

    @timer
    def agent_step(self, user_message, img=None):
        if user_message is None or user_message == '':
            return
        
        self.chat_memory.append({
            "role": "user",
            "content": user_message
        })
        
        while True:
            chat_completion = self.client.chat.completions.create(
                model=self.model,
                temperature=1,
                messages=self.chat_memory.get_chat_memory(),
                tools=self.tools_metadata,
                tool_choice="auto"
            )
            response = chat_completion.choices[0]
            
            # update the messages with the agent's response
            self.chat_memory.append(response.message.dict())
            
            # if NOT calling a tool (responding to the user), return 
            if not response.message.tool_calls:
                self.message_queue.put({
                    'content': response.message.content.replace('\n', '|'),
                    'final': True
                })
                break

            # if calling a tool, execute the tool
            else:
                # parse the arguments from the LLM function call
                for tool_call in response.message.tool_calls:
                    print(f'TOOL CALL: {tool_call.function}')
                    tool_thread = Thread(target=self.__call_tool, args=(tool_call,))
                    tool_thread.start()
                    
                    while True:
                        returned_content = self.tool_queue.get()
                        if not returned_content['done']:
                            prompt = 'Kindly inform user the status of the request in progress. '\
                                     + f'The tool running is {tool_call.function.name} with the '\
                                     + f'parameters {json.loads(tool_call.function.arguments)}. '\
                                     + f'This is the status: {returned_content['text']}. Otherwise '\
                                     + 'do not engage the user for furter feedback on the request.'
                            self.__comment(prompt)
                        else:
                            break

                    # add the tool call response to the message history 
                    self.chat_memory.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id, 
                        "name": tool_call.function.name, 
                        "content": returned_content['text']
                    })
                    
    def __call_tool(self, tool_call):
        arguments = json.loads(
            tool_call.function.arguments
        )

        # Inject tool queue to parameters
        arguments['tool_queue'] = self.tool_queue

        func = self.tools[tool_call.function.name]
        returned_content = func(**arguments)
        self.tool_queue.put(returned_content)
        
    def __comment(self, prompt):
        chat_completion = self.client.chat.completions.create(
            model=self.model,
            temperature=1,
            messages=[
                {
                    "role": "assistant", 
                    "content": prompt
                }
            ],
        )
        response = chat_completion.choices[0]
        # self.chat_memory.append(response.message.dict())
        self.message_queue.put({
            'content': response.message.content.replace('\n', '|'), 
            'final': False
        })


        
    
    