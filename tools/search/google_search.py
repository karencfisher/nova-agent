import requests
import os
import asyncio

from dotenv import load_dotenv
from collections import defaultdict

from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from openai import OpenAI

from tools.search.async_web_scraper import AsyncWebScraper
from tools.timer import timer
    

class SearchTool:
    def __init__(self, **kwargs):
        self.num_search = kwargs.get('num_search', 10)
        self.k_best = kwargs.get('k_best', 5)
        self.l2_threshold = kwargs.get('l2_threshold', 0.4)
        self.verbose = kwargs.get('verbose', False)
        self.db = None

        load_dotenv()
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.google_cx = os.getenv('GOOGLE_CSE_ID')

        self.embeddings = HuggingFaceEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
        
        load_dotenv()
        self.client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
        )

    def __get_pages(self, query):
        # call Google custom search engine to find websites
        url = 'https://www.googleapis.com/customsearch/v1'
        params = {"key": self.google_api_key,
                  "cx": self.google_cx,
                  "q": query,
                  "num": self.num_search}
        response = requests.get(url, params)

        if response.status_code != 200:
            return [{"error_response": response.status_code}]
        return response.json()['items']
    
    async def __get_documents_async(self, items):
        scraper = AsyncWebScraper(self.text_splitter)
        docs = await scraper.get_documents(items)
        return docs
    
    def __get_documents(self, items):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(self.__get_documents_async(items))
    
    def __store_documents(self, docs):
        # vectorize documents and select best k_best
        self.db = FAISS.from_documents(documents=docs, embedding=self.embeddings)

    def __get_selections(self, query):
        # vectorize documents and select best k_best
        selections = self.db.similarity_search_with_score(query, k=self.k_best)
        return selections
    
    def __get_summary(self, selections):
        # get references used, in ranked order
        hash = defaultdict(int)
        contents = []
        for selection in selections:
            hash[selection[0].metadata['reference']] += 1
            contents.append(selection[0].page_content)
            
        # Passages are sorted from most come from a page to least
        passage_counts = [(k, v) for k, v in hash.items()]
        passage_counts.sort(key=lambda x: x[1], reverse=True)
        references = '\n'.join([f'{link[0]} URL: {link[1]}' for link, _ in passage_counts])
        
        # LLM summarizes content of selections
        content = '\n'.join(contents)
        prompt = f'Write a detailed summary of the following information:\n{content}'
        chat_completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{'role': 'user', 'content': prompt}]
        )
        summary = chat_completion.choices[0]
        response = f"{summary}\n\n{references}"
        return response
    
    @timer
    def run(self, query):
        print(f'Searching for: {query}\n')
        items = self.__get_pages(query)   
        print(f'Found {len(items)} pages\ngetting documents\n')   
        docs = self.__get_documents(items)
        self.__store_documents(docs)
        print(f'Stored {len(docs)} documents\ngetting selections\n')
        selections = self.__get_selections(query)
        print(f'Got {len(selections)} selections\ngetting summary\n')
        output = self.__get_summary(selections)
        return output

