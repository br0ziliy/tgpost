#!/bin/env python

# -*- coding: utf-8 -*-
import argparse, os, json
import logging as log
log.getLogger(__name__)
from telegraph import Telegraph
from telegraph.exceptions import TelegraphException
from .config import TgPostConfig

class TgPost(object):
    def __init__(self, config):
        self.config = config
        self.short_name = config['short_name']
        self.access_token = config['access_token']
        self.author_name = config['author_name']
        self.author_url = config['author_url']
        self.pages_path = "{}/{}/".format(config['pages_path'],self.short_name)
        self.tg = None # initialized below
        self.initialize()

    def initialize(self):
        log.debug("Initializing for [{}]".format(self.short_name))
        token = self.access_token
        if not token or token == 'None':
            log.info("Getting access token for [{}]".format(self.short_name))
            tg = Telegraph()
            res = tg.create_account(short_name=self.short_name,
                                    author_name=self.author_name,
                                    author_url=self.author_url)
            self.access_token = tg.get_access_token()
            self.config['access_token'] = self.access_token
            self.tg = tg
            log.debug("Access token aquired: {}".format(self.access_token))
        else:
            log.info("Authenticating to Telegraph API...")
            self.tg = Telegraph(access_token=token)
            account_info = None
            try:
                account_info = self.tg.get_account_info()
            except TelegraphException as exc:
                log.error("Authentication failed, telegra.ph said: {}".format(exc))
                raise SystemExit(1)
            log.debug("Got following account info: {}".format(account_info))
        
    def publish(self, filename):
        content = None
        with open(filename, 'r') as f:
            content = f.read()
        f.close()
        title = raw_input("Enter post title: ")
        res = self.tg.create_page(title=title, html_content=content,
                                  author_name=self.author_name, author_url=self.author_url)
        # {u'can_edit': True, u'description': u'', u'title': u'Testing
        # telegra.ph API', u'url':
        # u'http://telegra.ph/Testing-telegraph-API-08-22', u'views': 0, u'a
        # uthor_name': u'TgPost', u'author_url': u'https://t.me/br0ziliy', u'path':
        # u'Testing-telegraph-API-08-22'}  
        log.debug("Created page: {}".format(res))

    def new_post(self, filename):
        md_file = "".join([self.pages_path,filename,".md"])
        log.info("Creating file {}".format(md_file))
        raise NotImplementedError('New post capabilities are not yet implemented')

    def edit_post(self,path):
        log.info("Editing http://telegra.ph/{}".format(path))
        title = raw_input("Enter post title: ")
        filename = raw_input("Enter content file: ")
        with open(filename, 'r') as f:
            content = f.read()
        f.close()

        res = self.tg.edit_page(path=path, title=title, html_content=content,
                                author_name=self.author_name, author_url=self.author_url,
                                return_content=True)
        log.debug("Edited page: {}".format(res))

    def init(self):
        return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Telegra.ph CLI interface")
    parser.add_argument('-d', '--debug', default=True, action='store_false')
    parser.add_argument('-c', '--config-file',
                        default=os.path.expanduser('~/.tgpost.cfg'),
                        type=argparse.FileType('a'))
    parser.add_argument('action', default='new', choices=['new_post', 'init',
                                                          'edit_post', 'send_post',
                                                          'publish', 'check'])
    parser.add_argument('param', nargs='*', default=None)
    args = parser.parse_args()
    config_file = args.config_file.name
    args.config_file.close()
    debug = args.debug
    action = args.action
    param = "-".join(args.param)
    if ' ' in param:
        # yeah, no spaces in my param pretty please
        param = "-".join(param.split(' '))

    tgpost_config = TgPostConfig(debug=debug)
    if action == 'init': # "init" is special case - it creates the actual
                         # configuration to start with
        tgpost_config.set_name(param)
    tgpost_config.get_config()
    method = None
    tgpost = TgPost(tgpost_config)

    try:
        method = getattr(tgpost, action)
    except AttributeError:
        raise NotImplementedError("Method {} not implemented".format(args.action))
    method(param)
