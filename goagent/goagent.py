#! /usr/bin/env python

import urllib2

urllib2.urlopen(
    urllib2.Request(
        'https://mail.google.com/fetch.py',
        data='methd=GET&url=http://twitter.com/&&body=',
        headers={'Host': 'goagent.appspot.com'}
    )
)
