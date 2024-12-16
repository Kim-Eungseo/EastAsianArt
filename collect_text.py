# %%
from search_scrape import SerperSearchEngineService, SearchResponse, RelatedPage
from key_phrases import key_phrases

service = SerperSearchEngineService()

total_pages = []
for phrase in key_phrases:
    print(phrase)
    try:
        search_response: SearchResponse = service.search_google_news(
            phrase, num_results=100
        )
        related_pages: list[RelatedPage] = search_response.scrape_all_urls()
        total_pages.extend(related_pages)

    except Exception as e:
        import traceback

        traceback.print_exc()

# %%
