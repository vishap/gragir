import os
import logging
import urllib.parse as urlparse
from bs4 import BeautifulSoup

from book import Item, Book


class PrepareEpub(object):

    @classmethod
    def prepare(cls, book):
        logger = logging.getLogger(__name__)
        logger.info("BEGIN Prepare EPUB.")
        cls.localize_url(book)
        logger.info("END Prepare EPUB.")

    @classmethod
    def localize_url(cls, book):
        #logger = logging.getLogger(__name__)
        for item in book.content.values():
            if hasattr(item, 'remove'):
                continue
            category = item.content_type.split("/")[0]
            if category != 'text':
                cls._moveTo(book,item,category)
            else:
                cls._moveTo(book,item,"")

    @classmethod
    def _moveTo(cls, book, item, category):
        logger = logging.getLogger(__name__)
        parsed_url= urlparse.urlsplit(item.url)
        file_name = os.path.basename(parsed_url.path)
        if category:
            new_url = category + "/" + file_name 
        else:       
            new_url = file_name 
        if item.url != new_url \
            and new_url in book.content:
                new_url = cls._findUniqueName(book, category, file_name)

        logger.info("Renaming {} -> {}"
                    .format(item.url, new_url))

        for dependant in item.needed_by:
            if hasattr(dependant, 'soup'):
                base_link = urlparse.urlsplit(dependant.url)
                base_link.path = os.path.dirname(base_link.path)
                for a in dependant.soup.find_all('a'):
                    if cls._getAbsoluteUrl(base_link, a.attr.href) == item.url:
                        a.attr.href = new_url
                for img in dependant.soup.find_all('img'):
                    if cls._getAbsoluteUrl(base_link, img.attr.src) == item.url:
                        img.attrs.src = new_url
        item.url = new_url

    @classmethod
    def _getAbsoluteUrl(cls, base_link, link):
        parsed = urlparse.urlsplit(link)
        if parsed.netloc is None:
            parsed.scheme = base_link.scheme 
            parsed.netloc = base_link.netloc
        if  parsed.path[0] != '/':
            parsed.path = base_link.path + '/' + href.path
        return \
            urlparse.SplitResult(parsed.scheme,
                                parsed.netloc,
                                parsed.path,
                                parsed.query,
                                None).geturl()

    @classmethod
    def _findUniqueName(cls, book, category, filename):
        i = 0
        file_name_base, file_ext = os.path.splitext(filename)
        while True:
            i+=1
            if category:
                new_url = category + '/' + file_name_base + '_' + i + file_ext
            else: 
                new_url = file_name_base + '_' + i + file_ext
            if new_url not in book.content:
                break 
        return new_url

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

