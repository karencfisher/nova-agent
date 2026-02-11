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
from utils.timer import timer
    

class SearchTool:
    def __init__(self, **kwargs):
        self.num_search = kwargs.get('num_search', 10)
        self.k_best = kwargs.get('k_best', 5)
        self.l2_threshold = kwargs.get('l2_threshold', 0.4)
        self.verbose = kwargs.get('verbose', False)
        self.db = None

        load_dotenv()
        self.serpapi_key = os.getenv('SERPAPI_KEY')

        self.embeddings = HuggingFaceEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
        
        load_dotenv()
        self.client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
        )

    def __get_pages(self, query):
        # Use SerpAPI as the primary and only external search provider.
        if self.serpapi_key:
            print('Using SerpAPI as primary search provider')
            return self.__serpapi_pages(query, self.serpapi_key)

        # No SerpAPI key provided — do not call Google CSE anymore.
        print('No SERPAPI_KEY configured. External search is disabled.')
        return [{"error_response": 'no_search_provider', "message": "Set SERPAPI_KEY in .env or configure a local crawler."}]

    def __serpapi_pages(self, query, api_key):
        # Simple SerpAPI fallback: returns list of items with 'title' and 'link'
        url = 'https://serpapi.com/search.json'
        params = {
            'engine': 'google',
            'q': query,
            'num': self.num_search,
            'api_key': api_key
        }
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code != 200:
                print(f"SerpAPI error: {resp.status_code} {resp.text}")
                return [{"error_response": resp.status_code, "body": resp.text}]
            data = resp.json()
            results = []
            for r in data.get('organic_results', [])[: self.num_search]:
                title = r.get('title') or r.get('position')
                link = r.get('link') or r.get('source')
                results.append({'title': title, 'link': link})
            return results
        except Exception as e:
            print(f"SerpAPI request failed: {e}")
            return [{"error_response": 'serpapi_request_failed', "body": str(e)}]
    
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
        if not docs:
            print("No documents retrieved to store (empty docs). Aborting indexing.")
            self.db = None
            return
        try:
            self.db = FAISS.from_documents(documents=docs, embedding=self.embeddings)
        except Exception as e:
            print(f"Error creating FAISS index: {e}")
            self.db = None
            return

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
    def run(self, **kwargs):
        items = self.__get_pages(kwargs['query'])
        if items[0].get('error_response') is not None:
            return(f'Search error: {items[0]["body"]}')
        print(f'Found {len(items)} pages, parsing pages\n')
        kwargs['tool_queue'].put({
            'done': False, 
            'text': f'Found {len(items)} pages\ngetting documents\n'
        })   
        docs = self.__get_documents(items)
        self.__store_documents(docs)
        if not self.db:
            print('No index available after storing documents; returning no results')
            return 'No documents could be indexed for this query.'
        print(f'Stored {len(docs)} documents\ngetting selections\n')
        kwargs['tool_queue'].put({
            'done': False, 
            'text': f'Stored {len(docs)} documents, getting selections\n'
        })  
        selections = self.__get_selections(kwargs['query'])
        print(f'Got {len(selections)} selections\ngetting summary\n')
        kwargs['tool_queue'].put({
            'done': False, 
            'text': f'Stored {len(docs)} summarizing results\n'
        })  
        output = self.__get_summary(selections)
        return {'done': True, 'text': output}

