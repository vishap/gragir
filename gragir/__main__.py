#!/usr/bin/env python3
# Encoding: UTF-8
"""
"""

# Standard library modules do the heavy lifting. Ours is all simple stuff.
# import base64
# import email, email.message
# import mimetypes
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

def parseMhtFile(mhtFileName):
    logger = logging.getLogger(__name__)
    logger.info(mhtFileName)
    pass

def parseZipFile( zip ):
    for zipMember in zip.infolist():
        if validateMht(zipMember):
            parseMhtFile(zipMember.filename)
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

    with zipfile.ZipFile(args.zip, 'r') as zip:
        parseZipFile(zip)

if __name__ == "__main__":
    main() # Kindda useless if we're not using doctest or anything?
