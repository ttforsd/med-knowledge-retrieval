import scrapy
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from scrapy.crawler import CrawlerProcess
from mongo import * 

class Spider_MD(scrapy.Spider):
    name = 'md_to_mongo'
    custom_settings = {
        'DEPTH_LIMIT': 1, 
        "LOG_LEVEL": "CRITICAL",
    }

    def __init__(self, url=None, *args, **kwargs):
        super(Spider_MD, self).__init__(*args, **kwargs)
        self.start_urls = [url] if url else []
        self.visited_urls = set()  # Set to store visited URLs

    def parse(self, response):
        # Extracting the URL and response body (HTML content)
        url = response.url

        # If URL is already visited, skip parsing and following links
        if url in self.visited_urls:
            return
        else:
            self.visited_urls.add(url)  # Add URL to visited set
            self.logger.info(f"Visited URL: {url}")

        # Parse HTML content using BeautifulSoup
        soup = BeautifulSoup(response.body, 'html.parser')

        # Remove content with class="breadcrumbs"
        for breadcrumbs in soup.find_all(class_='breadcrumbs'):
            breadcrumbs.decompose()

        # Remove content within <header>
        for header in soup.find_all('header'):
            header.decompose()

        # Remove content within <footer>
        for footer in soup.find_all('footer'):
            footer.decompose()

        # Remove script tags
        for script in soup.find_all('script'):
            script.decompose()

        # Convert parsed HTML to Markdown
        parsed_html = str(soup)
        markdown_content = md(parsed_html)

        # Extract title from the page
        title = soup.title.text if soup.title else "Untitled"
        print(f"Title: {title}")
        # print(markdown_content)
        # print("--------------------------------------------------")
        # # Store data in MongoDB or print it for testing
        # self.logger.info(f"Title: {title}")
        # self.logger.info(markdown_content)
        self.logger.info("--------------------------------------------------")

        # Your MongoDB insertion code here
        # write to mongo 
        insert_data(title, url, markdown_content)

        # Follow links if not reached the depth limit and excluding header/footer links
        if response.meta.get('depth') < self.custom_settings['DEPTH_LIMIT']:
            for next_page in response.xpath('//a[not(ancestor::header) and not(ancestor::footer) and not(contains(@class, "breadcrumbs"))]/@href').getall():
                yield response.follow(next_page, self.parse)

# URL to crawl
url_to_crawl = "https://cks.nice.org.uk/topics/"

# Run spider
process = CrawlerProcess()
process.crawl(Spider_MD, url=url_to_crawl)
process.start()
