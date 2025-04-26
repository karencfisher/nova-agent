from tavily import TavilyClient
from dotenv import load_dotenv
from typing import Annotated
import os


load_dotenv()
api_key = os.getenv("TAVILY_API_KEY")
client = TavilyClient(api_key=api_key)

def search(query: Annotated[str, "The search query"]) -> str:
    return client.qna_search(query)





