#!/usr/bin/env python

import sys
import xml
import json
import dataset
import plistlib


class InvalidArgumentError(Exception):
    pass


class InvalidXMLFileError(Exception):
    pass


def main():
    try:
        if len(sys.argv) != 2:
            raise InvalidArgumentError("parse.py takes exactly one argument: the path to an iTunes plist. %s provided." % len(sys.argv[1:]))
        else:
            save(parse(sys.argv[1]))

    except Exception, e:
        print json.dumps({
            'error': {
                'type': type(e).__name__,
                'message': str(e)
            }
        })

    else:
        print json.dumps({
            'success': {
                'type': 'ok',
                'message': "Imported iTunes library"
            }
        })


def parse(filename):
    try:
        p = plistlib.readPlist(filename)
    except xml.parsers.expat.ExpatError, e:
        raise InvalidXMLFileError("Invalid XML file supplied: %s" % filename)
    except IOError:
        raise InvalidXMLFileError("Invalid XML file supplied: %s" % filename)


def save(library):
    pass


if __name__ == "__main__":
    main()