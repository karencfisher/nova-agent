from tools.memory.core_memory import CoreMemory, MemoryRetrieval                             
from tools.search.search import Search
from tools.browser.browser import Browser
from tools.get_time.get_time import GetTime


tool_specs = [
    {
        'name': 'get_time',
        'tool': GetTime.get_todays_date,
        'metadata': {
            "type": "function",
            "function": {
                "name": "get_time",
                "description": GetTime.description,
                "parameters": None
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
