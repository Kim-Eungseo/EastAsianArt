from search_scrape import SerperSearchEngineService, SearchResponse, RelatedPage

service = SerperSearchEngineService()

search_response: SearchResponse = service.search_google_search("국내 쇼핑")

related_pages: list[RelatedPage] = search_response.scrape_all_urls()
