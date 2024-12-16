import json
from typing import Iterator, Union
import requests
from io import BytesIO
from trafilatura import extract


class Article:
    def __init__(self, url: str, article: str, full_data: Union[dict, None] = None):
        self.url = url
        self.article = article
        self.full_data = full_data

    def __str__(self):
        return json.dumps(
            {"url": self.url, "article": self.article, "full_data": self.full_data},
            ensure_ascii=False,
            indent=2,
        )


def scrape_article_urls(url_list, threads=10, sleep_time=1) -> Iterator[Article]:
    """
    Download and process a list of article URLs using trafilatura.

    Parameters:
    url_list (list): List of URLs to download.
    threads (int): Number of threads to use for downloading.
    sleep_time (int): Sleep time between buffer loads.

    Returns:
    None
    """
    from trafilatura.downloads import (
        add_to_compressed_dict,
        buffered_downloads,
        load_download_buffer,
    )

    # Convert the input list to an internal format
    url_store = add_to_compressed_dict(url_list)

    # Processing loop
    while url_store.done is False:
        buffer_list, url_store = load_download_buffer(url_store, sleep_time=sleep_time)
        # Process downloads
        for url, result in buffered_downloads(buffer_list, threads):
            full_data = extract(result, with_metadata=True, output_format="json")
            if full_data:
                full_data = json.loads(full_data)
                yield Article(url, full_data.get("text", ""), full_data)


def download_pdf_to_bytesio(url) -> Union[BytesIO, None]:
    """
    Downloads a PDF file from the given URL and returns it as a BytesIO object.

    Args:
        url (str): The URL of the PDF file.

    Returns:
        BytesIO: A BytesIO object containing the PDF data, or None if the download fails.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept": "application/pdf",
    }

    try:
        # Send a GET request to the URL with headers
        response = requests.get(url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            # Store the content in a BytesIO object
            pdf_file = BytesIO(response.content)

            # Check if the content is a PDF file
            pdf_file.seek(0)
            if pdf_file.read(5) == b"%PDF-":
                pdf_file.seek(0)  # Reset the pointer to the beginning of the file
                return pdf_file
            else:
                return None
        else:
            return None
    except Exception as e:
        return None


if __name__ == "__main__":
    # test download_pdf_to_bytesio
    pdf_url = (
        "https://assets.kpmg.com"
        "/content/dam/kpmg/kr/pdf/2023/business-focus/kpmg-korea-ecommerce%20trends-20231129.pdf"
    )
    _pdf_file = download_pdf_to_bytesio(pdf_url)

    # save it to local
    with open("dummy.pdf", "wb") as file:
        file.write(_pdf_file.read())
