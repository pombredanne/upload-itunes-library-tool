#!/usr/bin/env python

import sys
import xml
import json
import datetime
import plistlib
import dumptruck
import traceback
import scraperwiki
from collections import OrderedDict


class InvalidArgumentError(Exception):
    pass


class InvalidXMLFileError(Exception):
    pass


def main():
    try:
        if len(sys.argv) != 2:
            raise InvalidArgumentError("parse.py takes exactly one argument: the path to an iTunes plist. %s provided." % len(sys.argv[1:]))
        else:
            save(parse(extract(sys.argv[1])))

    except Exception, e:
        scraperwiki.status('error', type(e).__name__)
        print json.dumps({
            'error': {
                'type': type(e).__name__,
                'message': str(e),
                'trace': traceback.format_exc()
            }
        })

    else:
        scraperwiki.status('ok')
        print json.dumps({
            'success': {
                'type': 'ok',
                'message': "Imported iTunes library"
            }
        })


def extract(filename):
    try:
        p = plistlib.readPlist(filename)
    except xml.parsers.expat.ExpatError, e:
        raise InvalidXMLFileError("Invalid XML file supplied: %s" % filename)
    except IOError:
        raise InvalidXMLFileError("Invalid XML file supplied: %s" % filename)
    return p

def parse(library):

    distinguishedKinds = {
        2: 'Movies',
        3: 'TV Shows',
        4: 'Music',
        5: 'Books',
        6: 'Tones',
        10: 'Podcasts',
        17: 'Voice Memos',
        19: 'Purchased',
        22: 'iTunes DJ',
        26: 'Genius',
        205: 'Music Videos'
    }

    meta = [OrderedDict([
        ('itunes_version', library['Application Version']),
        ('export_date', library['Date'].isoformat()),
        ('id', library['Library Persistent ID']),
        ('location', library['Music Folder'])
    ])]
    
    playlists = []
    playlists_tracks = []
    for playlist in library['Playlists']:

        if 'Master' in playlist:
            playlist_type = 'Library'
        elif 'Distinguished Kind' in playlist and playlist['Distinguished Kind'] in distinguishedKinds:
            playlist_type = distinguishedKinds[playlist['Distinguished Kind']]
        elif 'Genius Track ID' in playlist:
            playlist_type = 'Genius'
        elif 'Smart Criteria' in playlist:
            playlist_type = 'Smart'
        else:
            playlist_type = 'Playlist'

        playlists.append(OrderedDict([
            ('id', playlist['Playlist ID']),
            ('name', playlist['Name']),
            ('type', playlist_type)
        ]))

        if 'Playlist Items' in playlist:
            for track in playlist['Playlist Items']:
                playlists_tracks.append(OrderedDict([
                    ('playlist_id', playlist['Playlist ID']),
                    ('track_id', track['Track ID'])
                ]))

    tracks = []
    for i, track in library['Tracks'].iteritems():
        if 'TV Show' in track:
            track_type = 'TV Show'
        elif 'Podcast' in track:
            track_type = 'Podcast'
        elif 'Movie' in track:
            track_type = 'Movie'
        elif 'Music Video' in track:
            track_type = 'Music Video'
        else:
            track_type = 'Music'

        tracks.append(OrderedDict([
            ('id', track['Track ID']),
            ('type', track_type),
            ('name', get(track, 'Name')),
            ('artist', get(track, 'Artist')),
            ('composer', get(track, 'Composer')),
            ('album', get(track, 'Album')),
            ('date_added', get(track, 'Date Added')),
            ('date_modified', get(track, 'Date Modified')),
            ('genre', get(track, 'Genre')),
            ('kind', get(track, 'Kind')),
            ('year', get(track, 'Year')),
            ('bit_rate', get(track, 'Bit Rate')),
            ('sample_rate', get(track, 'Sample Rate')),
            ('size', get(track, 'Size')),
            ('play_count', get(track, 'Play Count', 0)),
            ('date_last_played', get(track, 'Play Date UTC')),
            ('comments', get(track, 'Comments')),
            ('rating', get(track, 'Rating')),
            ('purchased', get(track, 'Purchased', False)),
            ('protected', get(track, 'Protected', False)),
            ('series', get(track, 'Series'))
        ]))

    return {
        'library': meta,
        'playlists': playlists,
        'playlists_tracks': playlists_tracks,
        'tracks': tracks
    }


def save(data):
    dt = dumptruck.DumpTruck(dbname="scraperwiki.sqlite")
    for table_name, rows in data.iteritems():
        dt.insert(rows, table_name)


def get(dictionary, key, otherwise=None):
    if key in dictionary:
        i = dictionary[key]
        if type(i) == datetime.datetime:
            return i.isoformat()
        else:
            return i
    else:
        return otherwise

if __name__ == "__main__":
    main()