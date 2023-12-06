import scrapy
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from scrapy.crawler import CrawlerProcess
from mongo import *

class Spider_MD(scrapy.Spider):
    name = 'md_to_mongo'

    custom_settings = {
        'LOG_LEVEL': 'CRITICAL',  # Set the log level to CRITICAL
    }
    # allowed_domains = ['cks.nice.org.uk', "www.gov.uk", "www.nhs.uk"]
    allowed_domains = ['bnf.nice.org.uk']
    def __init__(self, url=None, depth_limit=3, *args, **kwargs):
        super(Spider_MD, self).__init__(*args, **kwargs)
        self.start_urls = [url] if url else []
        self.visited_urls = set()  # Set to store visited URLs
        self.depth_limit = int(depth_limit)

    def parse(self, response):
        # Extracting the URL and response body (HTML content)
        url = response.url

        # Check if the response is a PDF, if so, skip processing
        content_type = response.headers.get('Content-Type', b'').decode('utf-8').lower()
        if 'application/pdf' in content_type:
            self.logger.critical(f"Skipping PDF URL: {url}")
            return

        # If URL is already visited, skip parsing and following links
        if url in self.visited_urls:
            return
        else:
            self.visited_urls.add(url)  # Add URL to visited set
            self.logger.critical(f"Visited URL: {url}")

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

        # Remove script
        for script in soup.find_all('script'):
            script.decompose()



        # Remove content with class="Layout-module--eula--b468d"
        for eula_content in soup.find_all(class_='Layout-module--eula--b468d'):
            eula_content.decompose()

        # Extract title from the page
        title = soup.title.text if soup.title else "Untitled"
        print(f"Title: {title}")

        # remove head
        for head in soup.find_all('head'):
            head.decompose()

        # Convert parsed HTML to Markdown
        parsed_html = str(soup)
        markdown_content = md(parsed_html)
        # print(markdown_content)
        # print("--------------------------------------------------")
        # # Store data in MongoDB or print it for testing
        # self.logger.critical(f"Title: {title}")
        # # self.logger.critical(markdown_content)
        # self.logger.critical("--------------------------------------------------")

        # write to mongo 
        insert_data(title, url, markdown_content)

        # Follow links if not reached the depth limit and excluding header/footer, breadcrumbs links
        if response.meta.get('depth', 0) < self.depth_limit:
            for next_page in response.xpath('//a[not(ancestor::header) and not(ancestor::footer) and not(contains(@class, "breadcrumbs")) and not(ancestor::div[contains(@class, "Layout-module--eula--b468d")])]/@href').getall():
                yield response.follow(next_page, self.parse, meta={'depth': response.meta.get('depth', 0) + 1})

# URL to crawl
url_to_crawl = "https://bnf.nice.org.uk/treatment-summaries/"
depth_limit_to_use = 1  # Set your desired depth limit here

# Run spider
process = CrawlerProcess()
process.crawl(Spider_MD, url=url_to_crawl, depth_limit=depth_limit_to_use)
process.start()
