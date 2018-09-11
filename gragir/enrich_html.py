import logging
import urllib.parse as urlparse
from bs4 import BeautifulSoup

from book import Item, Book


class EnrichHtml(object):

    @classmethod
    def enrich(cls, book):
        logger = logging.getLogger(__name__)
        logger.info("BEGIN Html Enrichment {} items.".format(len(book.content)))
        cls.parse(book)
        cls.createDAG(book)
        cls.populateContent(book)
        cls.createOrder(book)
        cls.print(book)
        logger.info("BEGIN Html Enrichment {} items.".format(len(book.content)))

    @classmethod
    def parse(cls, book):
        logger = logging.getLogger(__name__)
        for item in book.content.values():
            if item.content_type == 'text/html':
                logger.info("Parsing {} {}".format(item.content_type, item.url))
                item.soup = BeautifulSoup(item.payload, "lxml")
                if hasattr(item.soup, 'title') and item.soup.title:
                    item.title = item.soup.title.string
                else:
                    logger.info("No title for {}".format(item.url))
            else:
                logger.info("Skipping {} {}".format(item.content_type, item.url))

    @classmethod
    def createDAG(cls, book):
        logger = logging.getLogger(__name__)
        for item in book.content.values():
            if item.soup is not None:
                logger.info("Create DAG {}".format(item.url))

                links = item.soup.find_all('a')
                for link in links:
                    href = link.get('href')
                    if not href:
                        continue
                    parsed_href = urlparse.urlsplit(href)
                    url = \
                        urlparse.SplitResult(parsed_href.scheme,
                                            parsed_href.netloc,
                                            parsed_href.path,
                                            parsed_href.query,
                                            None).geturl()

                    if url in book.content:
                        book.content[url].needed_by.add(item.url)
                        item.needs.add(url)
                    elif href:
                        logger.info("   refered but no item exist: {}".format(url))

    @classmethod
    def populateContent(cls, book):
        logger = logging.getLogger(__name__)
        for item in book.content.values():
            if item.soup is not None:
                # Try to find content.
                item_content = item.soup.find_all('div', attrs={"id": "sbo-rt-content"})
                if len(item_content) == 1:
                    item.content = item_content[0]
                else:
                    logger.error("No content found: {}".format(item.url))
                    item.remove = True

    @classmethod
    def createOrder(cls, book):
        logger = logging.getLogger(__name__)
        for item in book.content.values():
            if item.soup is not None:
                # Try to get prev chapter.
                links = item.soup.find_all('a', attrs={"class": "prev nav-link"})
                if len(links):
                    item.prev = links[0].get('href')

                # Try to get next chapter.
                links = item.soup.find_all('a', attrs={"class": "next nav-link"})
                if len(links):
                    item.next = links[0].get('href')

        for item in book.content.values():
            if item.soup is not None \
                and not hasattr(item, 'prev') \
                and not hasattr(item, 'remove'):
                if book.first:
                    logger.error("Multiple begin points found. {} and {}"
                                .format(item.url, item.url))
                    raise Exception("Multiple begin points found.")
                else:
                    book.first = item

    @classmethod
    def getTitle(cls, item):
        if hasattr(item.soup, 'title') and item.soup.title:
            return item.soup.title.string
        else:
            return item.url


    @classmethod
    def print(cls, book):
        logger = logging.getLogger(__name__)
        item = book.first
        while item is not None:
            logger.info("Item: {}".format(cls.getTitle(item)))
            if hasattr(item, 'prev'):
                logger.info("   Prev: {}".format(item.prev))
            if hasattr(item, 'next'):
                logger.info("   Next: {}".format(item.next))
            for url in item.needs:
                logger.info("   Needs: {}".format(url))
            logger.info("")

            if hasattr(item, 'next'):
                item = book.content[item.next]
            else:
                item = None 

