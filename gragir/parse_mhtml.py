import logging
import zipfile
import email

from book import Item, Book

def validateMht(fileName):
    return True

def parseMht(mht, book):
    logger = logging.getLogger(__name__)

    mhtContent = email.message_from_bytes(mht)

    parts = mhtContent.get_payload()
    # Multiple parts, usually? If single 'str' part, then convert to a list.
    if not type(parts) is list: 
        parts = [mhtContent] 

    logger.info('   Number of parts: {}'.format(len(parts)))

    # Save all parts to files.
    for p in parts: # walk() for a tree, but I'm guessing MHT is never nested?
            #??? cs = p.get_charset() # Expecting "utf-8" for root HTML, None for all other parts.						
            ct = p.get_content_type()
                 # String coerced to lower case of the form maintype/subtype, else get_default_type().			
            fp = p.get("content-location") or "index.html" # File path. Expecting root HTML is only part with no location.

            logger.info('       Content type: {}, Location: {}, Size: {}'
                        .format(ct, fp, len(p.get_payload())))

            book.content[fp] = Item(fp, ct, p.get_payload(decode=True))


def parseMhtFile(zip, mhtInfo, book):
    logger = logging.getLogger(__name__)
    logger.info('Parsing {}, size: {}, csize: {} '
                .format(mhtInfo.filename,
                        mhtInfo.file_size, 
                        mhtInfo.compress_size))

    with zip.open(mhtInfo) as mht:
        parseMht(mht.read(), book)


def parseMhtmlZip(zip, book):
    logger = logging.getLogger(__name__)
    for zipMember in zip.infolist():
        if validateMht(zipMember):
            parseMhtFile(zip, zipMember, book)
        else:
            logger.error("Unexpected file in zip: {}".format(zipMember))
            raise Exception("Unexpected file in zip.")

def parseMhtmlZipFile(zipName, book):
    with zipfile.ZipFile(zipName, 'r') as zip:
        parseMhtmlZip(zip, book)
