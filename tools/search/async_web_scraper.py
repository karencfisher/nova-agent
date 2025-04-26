''' 
Ansynchronous web scraping for search tool.
Thank you to ChatGPT for its assistance!
'''
import asyncio
import aiohttp
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import re

class AsyncWebScraper:
    def __init__(self, text_splitter):
        self.text_splitter = text_splitter

    async def process_item(self, session, item):
        ua = UserAgent
        header = {'User-Agent': str(ua.chrome)}
        try:
            async with session.get(item['link'], headers=header, timeout=5) as response:
                article_text = await response.text()
                soup = BeautifulSoup(article_text, 'html.parser')
                text = soup.get_text().strip()
                text = re.sub(r'\n+', '\n', text)
                documents = self.text_splitter.create_documents([text],
                                metadatas=[{'reference': (item['title'], item['link'])}])
                return documents
        except:
            # Handle timeout error here
            return []
        
    async def get_documents(self, items):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for item in items:
                task = asyncio.create_task(self.process_item(session, item))
                tasks.append(task)

            docs = []
            completed = 0
            for task in asyncio.as_completed(tasks):
                documents = await task
                try:
                    docs += documents
                except TypeError:
                    pass
                completed += 1
        return docs
