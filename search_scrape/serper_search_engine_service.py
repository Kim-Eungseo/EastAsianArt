import datetime
import json
from typing import Union, List
import requests
from config import SERPER_API_KEY
from search_scrape.search_response import SearchResponse


class SerperSearchEngineService:
    def __init__(self, api_key: str = SERPER_API_KEY):
        self.API_KEY = api_key
        self.SEARCH_URL = "https://google.serper.dev/search"
        self.NEWS_URL = "https://google.serper.dev/news"

    @staticmethod
    def make_google_range_query(
        query: str, start_date: datetime.date = None, end_date: datetime.date = None
    ) -> str:
        """
        Generates a Google search query that searches for the given query within the given date range.
        :param query: The search query.
        :param start_date: The start date of the date range.
        :param end_date: The end date of the date range.
        :return: The generated search query.
        """
        if not start_date and not end_date:
            return query
        elif start_date and not end_date:
            return f"{query} after:{start_date.strftime('%Y-%m-%d')}"
        elif end_date and not start_date:
            return f"{query} before:{end_date.strftime('%Y-%m-%d')}"

        return f"{query} after:{start_date.strftime('%Y-%m-%d')} before:{end_date.strftime('%Y-%m-%d')}"

    @staticmethod
    def make_google_filetype_query(query: str, filetype: str) -> str:
        """
        Generates a Google search query that searches for the given query with the given file type.
        :param query: The search query.
        :param filetype: The file type to search for.
        :return: The generated search query.
        """
        return f"{query} filetype:{filetype}"

    def search_google_search(self, query: str, num_results: int = 10) -> SearchResponse:
        """
        Searches Google for the given query and returns a SearchResponse object containing the search results.
        :param query: The search query.
        :param num_results: The number of search results to return. Default is 20.
        :return: A SearchResponse object containing the search results.
        """
        return self.__search(query, self.SEARCH_URL, num_results, search_type="search")

    def search_google_news(self, query: str, num_results: int = 10) -> SearchResponse:
        """
        Searches Google News for the given query and returns a SearchResponse object containing the search results.
        :param query: The search query.
        :param num_results: The number of search results to return. Default is 20.
        :return: A SearchResponse object containing the search results.
        """
        return self.__search(query, self.NEWS_URL, num_results, search_type="news")

    def __search(
        self, query: str, url: str, num_results: int = 10, search_type="search"
    ) -> SearchResponse:
        cached_response = SearchResponse.load_cached_data_serper(query, search_type)
        if cached_response:
            return cached_response

        payload = {"q": query, "gl": "kr", "hl": "ko", "num": num_results}

        search_response: SearchResponse = self.__request_search(payload, url)
        search_response.cache_self()
        return search_response

    def __bulk_search(
        self, queries: List[str], url: str, num_results: int = 10
    ) -> List[SearchResponse]:
        payloads = [
            {"q": query, "gl": "kr", "hl": "ko", "num": num_results}
            for query in queries
        ]

        return self.__request_search(payloads, url)

    def __request_search(
        self, payload: Union[dict, List], url: str
    ) -> Union[SearchResponse, List[SearchResponse]]:
        payload = json.dumps(payload)
        headers = {"X-API-KEY": self.API_KEY, "Content-Type": "application/json"}

        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return [SearchResponse(d) for d in data]

            return SearchResponse(data)
        else:
            raise Exception(f"Request failed with status code {response.status_code}")


if __name__ == "__main__":
    pass
