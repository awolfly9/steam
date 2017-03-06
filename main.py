#-*- coding: utf-8 -*-

import logging
import os
import sys
import utils

from scrapy import cmdline

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')

    if not os.path.exists('log'):
        os.makedirs('log')

    logging.basicConfig(
            filename = 'log/game.log',
            format = '%(levelname)s %(asctime)s: %(message)s',
            level = logging.DEBUG
    )
    while True:
        utils.log('*******************run spider start...*******************')

        # cmdline.execute('scrapy crawl game_urls'.split())
        cmdline.execute('scrapy crawl game_info'.split())
