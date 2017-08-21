#!/bin/env python

# -*- coding: utf-8 -*-
import ConfigParser, os
from telegraph import Telegraph

class TgPost(object):
    __slots__ = ('access_token', '_config')
    def _init_(self, access_token=None):
        self.access_token = access_token

    def init(self):
        raise NotImplementedError('Initialization not yet implemented')
        
    def post(self):
        raise NotImplementedError('Posting not yet implemented')

    def edit(self):
        raise NotImplementedError('Edit capabilities are not yet implemented')

if __name__ == "__main__":
    config = ConfigParser.ConfigParser()
    config.read(os.path.expanduser('~/.tgpost.cfg'))
    try:
        access_token = config.get('tgpost','access_token')
        short_name = config.get('tgpost', 'user_name')
    except ConfigParser.NoSectionError:
        print "Missing section [tgpost] in ~/.tgpost.cfg"
        raise SystemExit(1)
    except ConfigParser.NoOptionError:
        print "access_token and/or user_name options are not found in \
~/.tgpost.cfg, creating new user..."
        tg_post = TgPost()
        tg_post.init()
        raise SystemExit(1)
    try:
        pages_path = config.get('tgpost', 'pages_path')
        author_name = config.get('tgpost', 'author_name')
    except ConfigParser.NoOptionError:
        print "Using defaults for pages_path, author_name"
        pages_path = os.path.expanduser('~/tgpost/')
        author_name = os.environ['USER']
