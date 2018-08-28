



class Item(object):

    def __init__(self, url, content_type, payload):
        self.url = url
        self.content_type = content_type
        self.payload = payload
        self.needed_by = set()
        self.needs = set()

class Book(object):

    def __init__(self, file_name):
        self.file_name = file_name
        self.content = {}
        self.first = None

