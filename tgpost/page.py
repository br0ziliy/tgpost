import markdown, os
import logging as log
log.getLogger(__name__)

class TgPage(object):

    def __init__(self, title, author_name=None, author_url=None, tags=[],
                 category=None, content=''):
        self.config = { 'title': title,
                        'author_name': author_name,
                        'author_url': author_url,
                        'tags': tags,
                        'category': category,
                        'content': content }

    def __getitem__(self, item):
        # TODO: unsafe, catch exception
        log.debug("Getting {}".format(item))
        return self.config[item]

    def __setitem__(self, item, value):
        log.debug("Setting {} to {}".format(item, value))
        if item in self.config.keys():
            self.config[item] = value
        else:
            raise AttributeError("{} is not in list of allowed \
attributes".format(item))

    def save(self, path):
        # TODO: this function signature should not contain 'path' in ideal world
        # The world is not ideal, and I'm too lazy, so let it be like this for
        # now
        title = self.config['title']
        filename = "{}.md".format('-'.join(title.split(' ')).lower())
        basepath = os.path.expanduser(path)
        # TODO: savepath will be different when categories are introduced
        savepath = "{}/{}".format(basepath, filename)
        log.debug("Saving {}".format(savepath))
        # below is not race-condition-safe: https://stackoverflow.com/a/273227
        if not os.path.exists(basepath):
            # TODO: catch exception here
            os.makedirs(basepath)
        if not os.path.exists(savepath):
            fh = file(savepath, 'w')
            # we cannot use yaml.dump(self.config)  here, as hashes are
            # unordered, and we care about the order.
            # TODO: this actually needs a nicer solution, not a heredoc.
            print self._yml_template()
            fh.write(self._yml_template())
            fh.close()
            log.info("{} created!".format(savepath))
        else:
            log.warning("{} already exists! Not overwriting.".format(savepath))

    def load(self, path):
        raise NotImplementedError("Post loading is not yet there...")

    def _yml_template(self):
        return """title: {title}
author_name: {author_name}
author_url: {author_url}
tags: {tags}
content:

{content}
""".format(**self.config)
