from tools.memory.core_memory import CoreMemory, MemoryRetrieval                             
from tools.search.search import Search
from tools.browser.browser import Browser
from tools.society_of_mind.deep_thought import Thinking

tool_specs = [
    {  
        'name': 'deep_thought',
        'tool': Thinking.run,
        'metadata': {
            "type": "function",
            "function": {
                "name": "deep_thought",
                "description": Thinking.description,
                "parameters": {
                    "type": "object",
                    "properties": Thinking.properties,
                    "required": ["query"],
                },
            }
        }
    },
    {  
        'name': 'memory_save',
        'tool': CoreMemory.memory_save,
        'metadata': {
            "type": "function",
            "function": {
                "name": "memory_save",
                "description": CoreMemory.description,
                "parameters": {
                    "type": "object",
                    "properties": CoreMemory.properties,
                    "required": ["section", "memory_key", "memory_value"],
                },
            }
        }
    },
    {
        'name': 'memory_retrieve',
        'tool': MemoryRetrieval.memory_retrieve,
        'metadata': {
            "type": "function",
            "function": {
                "name": "memory_retrieve",
                "description": MemoryRetrieval.description,
                "parameters": {
                    "type": "object",
                    "properties": MemoryRetrieval.properties,
                    "required": ["query"],
                },
            }
        }
    },
    {  
        'name': 'search',
        'tool': Search.run,
        'metadata': {
            "type": "function",
            "function": {
                "name": "search",
                "description": Search.description,
                "parameters": {
                    "type": "object",
                    "properties": Search.properties,
                    "required": ["query"],
                },
            }
        }
    },
    {  
        'name': 'browser',
        'tool': Browser.run,
        'metadata': {
            "type": "function",
            "function": {
                "name": "browser",
                "description": Browser.description,
                "parameters": {
                    "type": "object",
                    "properties": Browser.properties,
                    "required": ["url"],
                },
            }
        }
    }
]
