#!/usr/bin/env python

import sys
import json
import dataset
import plistlib


def main():
    try:
        if len(sys.argv) != 2:
            raise ValueError("parse.py takes exactly one argument: the path to an iTunes plist. %s provided." % len(sys.argv[1:]))
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
    pass


def save(library):
    pass


if __name__ == "__main__":
    main()