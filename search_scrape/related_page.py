from dateutil import parser

from search_scrape.search_response import SourceType


class RelatedPage:
    def __init__(
        self,
        original_data: dict,
        searched_keyword: str,
        source_type: SourceType = SourceType.SERPER,
    ):

        # Only SERPER is supported now
        if source_type == SourceType.SERPER:
            self.source_type = source_type.value
            self.title = original_data.get("title", "")
            self.link = original_data.get("link", "")
            self.position: int = original_data.get("position", -1)
            self.original_data = original_data
            self.text = ""
            self.raw_data: dict | None = None
            self.searched_keyword = searched_keyword
            self.published_date = None

    def set_raw_data(self, raw_data):
        self.raw_data = raw_data

    def set_published_date(self, published_date):
        self.published_date = parser.parse(published_date).strftime("%Y-%m-%dT%H:%M:%S")
