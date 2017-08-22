# -*- coding: utf-8 -*-

import ConfigParser, os
import logging as log
log.getLogger(__name__)

REQUIRED_PARAMS = ['access_token', 'short_name']
OPTIONAL_PARAMS = {'pages_path': '~/tgpost/', 
                   'author_name': 'TgPost',
                   'author_url': 'https://t.me/br0ziliy'}

class TgPostConfig(object):

    def __init__(self, user_name=None, config_file='~/.tgpost.cfg', debug=True):
        # TODO: docs
        self.config = {}
        self.config_file = config_file
        self.parser = ConfigParser.ConfigParser()
        self.user_name = user_name
        loglevel = log.INFO
        if debug:
            loglevel = log.DEBUG
        log.basicConfig(format='>>> %(levelname)s %(message)s', level=loglevel)

    def set_name(self, name):
        self.user_name = name

    def get_config(self):
        user_name = self.user_name
        log.debug("Trying to get config for [{}]".format(user_name))
        log.debug('Opening config file {} for reading'.format(self.config_file))
        self._read_config_file()
        short_names = self.parser.sections()
        log.debug('Got sections: {}'.format(short_names))
        if len(short_names) == 0:
            log.debug("No accounts found in config")
            if user_name:
                log.debug("Initializing for {}".format(user_name))
                self._create_config(user_name)
            else:
                user_name = self._random_name()
                log.info('Using generated name: {}'.format(user_name))
                self._create_config(user_name)
        elif not user_name:
            # TODO: ask which user_name to post from
            user_name = short_names[0]
            self.user_name = user_name
        elif not user_name in short_names:
            log.debug('Account {} not found, initializing \
config'.format(user_name))
            self._create_config(user_name)
        log.info("Configuring for [{}]".format(user_name))
        self._read_config_file()
        conf_hash = {}
        for item in REQUIRED_PARAMS:
            try:
                conf_hash[item] = self.parser.get(user_name,item)
            except ConfigParser.NoOptionError:
                log.error('Please specify {} for {} in {}'.format(item,
                                                                  user_name,
                                                                  self.config_file))
                raise SystemExit(1)
        for item in OPTIONAL_PARAMS.keys():
            try:
                conf_hash[item] = self.parser.get(user_name, item)
            except ConfigParser.NoOptionError:
                log.debug('Using default for {}: {}'.format(item, OPTIONAL_PARAMS[item]))
                conf_hash[item] = OPTIONAL_PARAMS[item]
        self.config = conf_hash
        return self.config

    def _get_param(self,param):
        log.debug("Getting {} from [{}]".format(param, self.user_name))
        ret = None
        self._read_config_file()
        try:
            ret = self.parser.get(self.user_name, param)
        except ConfigParser.NoSectionError:
            log.error("Section [{}] not found in the config file".format(self.user_name))
            raise SystemExit(1)
        except ConfigParser.NoOptionError:
            log.error("Option {} not found in section [{}] in the config \
file".format(param, self.user_name))
            raise SystemExit(1)
        return ret

    def _set_param(self, param, value):
        log.debug("Setting {} to {} in [{}]".format(param, value, self.user_name))
        self._read_config_file()
        self.parser.set(self.user_name, param, value)
        with open(os.path.expanduser(self.config_file), 'wb') as configfile:
            self.parser.write(configfile)

    def _create_config(self, short_name):
        print "Creating [{}]".format(short_name)
        self.parser.add_section(short_name)
        self.parser.set(short_name, 'access_token', None)
        self.parser.set(short_name, 'short_name', short_name)

        for item in OPTIONAL_PARAMS.keys():
            value = OPTIONAL_PARAMS[item] # default value
            response = raw_input("Enter value for {} [{}]:".format(item, OPTIONAL_PARAMS[item]))
            if response:
                value = response
            self.parser.set(short_name, item, value)
        with open(os.path.expanduser(self.config_file), 'wb') as configfile:
            self.parser.write(configfile)

    def _random_name(self):
        # slightly modified https://stackoverflow.com/a/43593593
        import random
        
        # We create a set of digits: {0, 1, .... 9}
        digits = set(range(10))
        # We generate a random integer, 1 <= first <= 9
        first = random.randint(1, 9)
        # We remove it from our set, then take a sample of
        # 7 distinct elements from the remaining values
        last_7 = random.sample(digits - {first}, 7)
        num = str(first) + ''.join(map(str, last_7))
        return "tgpost{}".format(num)

    def _read_config_file(self):
        self.parser.read(os.path.expanduser(self.config_file))

    def __getitem__(self, item):
        return self._get_param(item)

    def __setitem__(self, item, value):
        return self._set_param(item, value)
