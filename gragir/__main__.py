#!/usr/bin/env python3
# Encoding: UTF-8
"""
"""

# Standard library modules do the heavy lifting. Ours is all simple stuff.
import base64
import email, email.message
import mimetypes
# import os
# import quopri

import sys
import logging
import argparse

import zipfile

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

    # Validate command line.
    # if args.pack == args.unpack:
    #         sys.stderr.write("Invalid: must specify one action, either --pack or --unpack.\n")
    #         sys.exit(-1)

    return args

def validateMht(fileName):
    return True

def parseMht(mht, content):
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

            content[fp] = p.get_payload(decode=True)
            # Create directories as necessary.
            # if os.path.dirname(fp):
            #         os.makedirs(os.path.dirname(fp), exist_ok=True)

            # # Save part's body to a file.
            # open(fp, "wb").write(p.get_payload(decode=True))

def parseMhtFile(zip, mhtInfo, content):
    logger = logging.getLogger(__name__)
    logger.info('Parsing {}, size: {}, csize: {} '
                .format(mhtInfo.filename,
                        mhtInfo.file_size, 
                        mhtInfo.compress_size))

    with zip.open(mhtInfo) as mht:
        parseMht(mht.read(), content)


def parseZipFile(zip, content):
    for zipMember in zip.infolist():
        if validateMht(zipMember):
            parseMhtFile(zip, zipMember, content)
        else:
            pass


def configLogger(args):
    loggingLevel = logging.DEBUG if args.debug \
                        else logging.INFO if args.verbose \
                            else logging.WARNING
    logging.basicConfig(
        format='%(asctime)s %(levelname)s: %(name)s - %(message)s',
        level=loggingLevel)

# Just do it.
def main():
    """
    """
    args = parseArguments()
    configLogger(args)
    
    logger = logging.getLogger(__name__)
    logger.info("Parsing {}.".format(args.zip))

    content = {}

    with zipfile.ZipFile(args.zip, 'r') as zip:
        parseZipFile(zip, content)

    logger.info("Loaded {} parts.".format(len(content)))
    for name in content.keys():
        logger.info("{}".format(name))


if __name__ == "__main__":
    main()
