#!/usr/bin/env python3
# Encoding: UTF-8
"""
"""

# Standard library modules do the heavy lifting. Ours is all simple stuff.
# import base64
# import email.message
# import mimetypes
# import os
# import quopri

import sys
import logging
import argparse

import ebooklib.epub as ebooklib

from book import Book, Item
from parse_mhtml import parseMhtmlZipFile
from enrich_html import EnrichHtml
from prepare_epub import PrepareEpub

def parseArguments():
    """
    Usage:
            cd foo-unpacked/
            mht2fs.py ../foo.mht
    """
    parser = argparse.ArgumentParser(description="Convert to EPub.")
    parser.add_argument("zip", metavar="MHT", help='path to MHT file, use "-" for stdin/stdout.')
    parser.add_argument("epub", metavar="EPUB", help="directory to create to store parts in, or read them from.") #??? How to make optional, default to current dir?
    parser.add_argument("-d", "--debug", action="store_true", help="log debug messages.")
    parser.add_argument("-v", "--verbose", action="store_true", help="log info messages.")
    parser.add_argument("-q", "--quiet", action="store_true", help="log only errors.")
    args = parser.parse_args() # --help is built-in.

    return args

def configLogger(args):
    loggingLevel = logging.DEBUG if args.debug \
                        else logging.INFO if args.verbose \
                            else logging.WARNING
    # logging.basicConfig(
    #     format='%(asctime)s %(levelname)s: %(name)s - %(message)s',
    #     level=loggingLevel)
    logging.basicConfig(
        format='%(message)s',
        level=loggingLevel)
    

    fh = logging.FileHandler('gragir.log', mode='w')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt=logging.Formatter(fmt='%(asctime)s %(levelname)s: %(name)s - %(message)s'))
    #, datefmt='%H:%M:%S'
    #'%(asctime)s %(levelname)s: %(name)s - %(message)s')
    logger = logging.getLogger()
    logger.addHandler(fh)



    # for name in content.keys():

def createEpubHtml(item):
    html = ebooklib.EpubHtml()
    return html

def createEpubBook(book):
    logger = logging.getLogger(__name__)

    ebook = ebooklib.EpubBook()

    it = book.first
    while it:
        if it.content_type == 'text/html':
            html = createEpubHtml(it)
            ebook.add_item(html)
        elif it.content_type == 'image/html':
            html = createEpubHtml(it)
            ebook.add_item(html)
        
    writeEpubBook(book.file_name, ebook)

    #     class EpubImage(EpubItem):
    #     class EpubNav(EpubHtml):
    #     class EpubCoverHtml(EpubHtml):
    #     class EpubHtml(EpubItem):
    #     class EpubCover(EpubItem):
    #     class EpubNcx(EpubItem):
    #     class EpubItem(object):
    #     class EpubException(Exception):
    #     class Link(object):
    #     class Section(object):


    #     def set_identifier(self, uid)
    #     def set_title(self, title)
    #     def set_language(self, lang)
    #     def set_cover(self, file_name, content, create_page=True):
    #         """
    #         Set cover and create cover document if needed.

    #         :Args:
    #           - file_name: file name of the cover page
    #           - content: Content for the cover image
    #           - create_page: Should cover page be defined. Defined as bool value (optional). Default value is True.
    #         """

    #     def add_author(self, author, file_as=None, role=None, uid='creator'):
    #     def add_metadata(self, namespace, name, value, others=None):
    #     def set_unique_metadata(self, namespace, name, value, others=None):
    #         "Add metadata if metadata with this identifier does not already exist, otherwise update existing metadata."
    #     def add_item(self, item):

    #     def get_metadata(self, namespace, name):
    #     def get_item_with_id(self, uid):
    #         """
    #         Returns item for defined UID.

    #         >>> book.get_item_with_id('image_001')

    #         :Args:
    #           - uid: UID for the item

    #         :Returns:
    #           Returns item object. Returns None if nothing was found.
    #         """

    #     def get_item_with_href(self, href):
    #         """
    #         Returns item for defined HREF.

    #         >>> book.get_item_with_href('EPUB/document.xhtml')

    #         :Args:
    #           - href: HREF for the item we are searching for

    #         :Returns:
    #           Returns item object. Returns None if nothing was found.
    #         """

    #     def get_items(self):
    #     def get_items_of_media_type(self, media_type):
    #     def get_items_of_type(self, item_type):
    #         """
    #         Returns all items of specified type.

    #         >>> book.get_items_of_type(epub.ITEM_IMAGE)

    #         :Args:
    #           - item_type: Type for items we are searching for

    #         :Returns:
    #           Returns found items as tuple.
    #         """
    #         return (item for item in self.items if item.get_type() == item_type)


    #     def get_template(self, name):
    #    def set_template(self, name, value):
    #         """
    #         Defines templates which are used to generate certain types of pages. When defining new value for the template
    #         we have to use content of type 'str' (Python 2) or 'bytes' (Python 3).

    #         At the moment we use these templates:
    #           - ncx
    #           - nav
    #           - chapter
    #           - cover

    #         :Args:
    #           - name: Name for the template
    #           - value: Content for the template
    #         """

    
    #     def add_prefix(self, name, uri):
    #         """
    #         Appends custom prefix to be added to the content.opf document

    #         >>> epub_book.add_prefix('bkterms', 'http://booktype.org/')

    #         :Args:
    #           - name: namespave name
    #           - uri: URI for the namespace
    #         """

    return book

def writeEpubBook(name, book, options=None):
    """
    Creates epub file with the content defined in EpubBook.

    >>> makeEpub('book.epub', book)

    :Args:
      - name: file name for the output file
      - book: instance of EpubBook
      - options: extra opions as dictionary (optional)
    """
    logger = logging.getLogger(__name__)

    try:
        epub = ebooklib.EpubWriter(name, book, options)
        epub.process()
        epub.write()
    except Exception as e:
        logger.error("Exception {}.".format(e))


def main():
    """
    """
    args = parseArguments()
    configLogger(args)
    
    logger = logging.getLogger(__name__)
    logger.info("Parsing {}.".format(args.zip))

    book = Book(args.epub)

    parseMhtmlZipFile(args.zip, book)
    EnrichHtml.enrich(book)
    PrepareEpub.prepare(book)
    book.save_in_dir('test_out/test_save')
    #createDAG(book)
    #createEpubBook(book)


if __name__ == "__main__":
    main()
