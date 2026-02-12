import requests
import os
import json

from dotenv import load_dotenv
from utils.timer import timer
    

class SearchTool:
    def __init__(self, k=5, snippet_chars=400):
        self.k = k
        self.snippet_chars = snippet_chars

        load_dotenv()
        self.serpapi_key = os.getenv('SERPAPI_KEY')

    def __get_pages(self, query):
        url = 'https://serpapi.com/search.json'
        params = {
            'engine': 'google',
            'q': query,
            'num': self.k,
            'api_key': self.serpapi_key
        }
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code != 200:
                print(f"SerpAPI error: {resp.status_code} {resp.text}")
                return [{"error_response": resp.status_code, "body": resp.text}]
            data = resp.json()
            results = []

            i = 1
            for r in data.get('organic_results', [])[: self.k]:
                snippet = r.get('snippet')
                if not snippet:
                    continue

                results.append({
                    'index': i,
                    'title': r.get('title', ''),
                    'url': r.get('link', ''),
                    'snippet': snippet[:self.snippet_chars]
                })
                i += 1
                
            return results
        except Exception as e:
            print(f"SerpAPI request failed: {e}")
            return [{"error_response": 'serpapi_request_failed', "body": str(e)}]
    
    @timer
    def run(self, **kwargs):
        items = self.__get_pages(kwargs['query'])
        output = {
            'query': kwargs['query'],
            'results' : items
        }
        return json.dumps(output)

