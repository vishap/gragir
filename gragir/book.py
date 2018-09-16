import os
import logging

class Item(object):

    def __init__(self, url, content_type, payload):
        self.url = url
        self.content_type = content_type
        self.payload = payload
        self.needed_by = set()
        self.needs = set()
        self.soup = None

    def save_file(self, directory):
        logger = logging.getLogger(__name__)
        if hasattr(self, 'remove'):
            return
        #
        #   Create file name.
        #
        if directory[-1] != '/':
            directory += '/'
        file_name = directory + self.url
        logger.info("Saved {}".format(file_name))
        #
        #   Ensure directory exist.
        #
        dir = os.path.dirname(file_name)
        if not os.path.exists(dir):
            os.makedirs(dir)
        #
        #   Save content.
        #
        if self.soup:
            with open( file_name, 'wb') as file:
                file.write(self.soup.prettify("utf-8"))
        else:
            with open( file_name, 'wb') as file:
                file.write(self.payload)

class Book(object):

    def __init__(self, file_name):
        self.file_name = file_name
        self.content = {}
        self.first = None

    def save_in_dir(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
        for item in self.content.values():
            item.save_file(directory)
