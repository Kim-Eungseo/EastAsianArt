from typing import List
from enum import Enum

MAX_WORKERS = 10


class SourceType(Enum):
    SERPER = "serper"


class SearchResponse:
    """
    Attributes:
        original_data: The original data returned by the search engine.
        search_keyword: The search keyword used to fetch the search results.
        related_page_list: A list of RelatedPage objects containing the search results.
    """

    def __init__(
        self,
        original_data: dict,
        source_type: SourceType = SourceType.SERPER,
        segment_name: str = None,
    ):
        self.source_type = None
        self.related_page_list = None
        self.search_keyword = None
        self.original_data = None

        if source_type == SourceType.SERPER:
            self.init_serper(original_data, segment_name)

    def init_serper(self, original_data, segment_name=None):
        from search_scrape import RelatedPage

        def preprocess_original_data_serper(data):
            from urllib import parse

            if "organic" in data:
                for row in data["organic"]:
                    row["link"] = parse.unquote(row["link"])
            elif "news" in data:
                for row in data["news"]:
                    row["link"] = parse.unquote(row["link"])
            return data

        self.original_data = preprocess_original_data_serper(original_data)
        self.search_keyword = original_data.get("searchParameters", {}).get("q", "")
        if "organic" in original_data:
            self.related_page_list: List[RelatedPage] = [
                RelatedPage(row, self.search_keyword, segment_name)
                for row in original_data.get("organic", [])
            ]
        elif "news" in original_data:
            self.related_page_list: List[RelatedPage] = [
                RelatedPage(row, self.search_keyword)
                for row in original_data.get("news", [])
            ]
        self.source_type = SourceType.SERPER.value

    def scrape_all_urls(self) -> list:
        from search_scrape import RelatedPage
        from search_scrape.utils import scrape_article_urls
        from urllib import parse

        target_url_map: dict[str, RelatedPage] = {
            page.link: page for page in self.related_page_list
        }

        if not target_url_map:
            return self.related_page_list

        unmatched_articles = []
        for scraped_article in scrape_article_urls(list(target_url_map.keys())):
            parsed_url = parse.unquote(scraped_article.url)
            if parsed_url in target_url_map and scraped_article.full_data:
                target_url_map[parsed_url].set_raw_data(scraped_article.full_data)
                target_url_map[parsed_url].published_date = (
                    scraped_article.full_data.get("date", None)
                )
                target_url_map[parsed_url].text = scraped_article.article

            else:
                unmatched_articles.append(scraped_article)

        if unmatched_articles:
            for missed_article in unmatched_articles:
                from Levenshtein import distance

                distances = [
                    (distance(missed_article.url, url), url)
                    for url in target_url_map.keys()
                ]
                closest_url = min(distances, key=lambda x: x[0])[1]

                if (
                    target_url_map[closest_url].text == ""
                    and target_url_map[closest_url].raw_data is None
                ):
                    target_url_map[closest_url].text = missed_article.article
                    target_url_map[closest_url].published_date = (
                        missed_article.full_data.get("date", None)
                    )

        return self.related_page_list
