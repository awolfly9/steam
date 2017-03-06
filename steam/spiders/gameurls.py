#-*- coding: utf-8 -*-

import re
import config
import utils

from scrapy.spiders import Spider
from scrapy import Request
from scrapy.selector import Selector
from sqlhelper import SqlHelper


class GameUrls(Spider):
    name = 'game_urls'

    start_urls = ['http://store.steampowered.com/search/?sort_by=Released_DESC&page=%s' % n for n in range(1, 1058)]

    def __init__(self, *a, **kw):
        super(GameUrls, self).__init__(*a, **kw)

        self.dir_game = 'log/%s' % self.name
        self.sql = SqlHelper()
        self.init()

        utils.make_dir(self.dir_game)

    def init(self):
        command = (
            "CREATE TABLE IF NOT EXISTS {} ("
            "`id` INT(8) NOT NULL AUTO_INCREMENT,"
            "`type` CHAR(10) NOT NULL,"
            "`name` TEXT NOT NULL,"
            "`url` TEXT NOT NULL,"
            "`is_crawled` CHAR(5) DEFAULT 'no',"
            "`page` INT(5) NOT NULL ,"
            "PRIMARY KEY(id)"
            ") ENGINE=InnoDB".format(config.steam_game_urls_table))
        self.sql.create_table(command)

    def start_requests(self):
        for i, url in enumerate(self.start_urls):
            yield Request(
                    url = url,
                    headers = {
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Encoding': 'gzip, deflate',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Connection': 'keep-alive',
                        'Host': 'store.steampowered.com',
                        'Upgrade-Insecure-Requests': '1',
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:51.0) Gecko/20100101 '
                                      'Firefox/51.0',
                    },
                    meta = {
                        'url': url,
                        'page': i + 1,
                    },
                    dont_filter = True,
                    callback = self.parse_all,
                    errback = self.error_parse,
            )

    def parse_all(self, response):
        # file_name = '%s/%s.html' % (self.dir_game, response.meta.get('page'))
        # self.save_page(file_name, response.body)

        self.log('parse_all url:%s' % response.url)

        game_list = response.xpath('//div[@id="search_result_container"]/div[2]/a').extract()
        count = 0
        for game in game_list:
            sel = Selector(text = game)
            url = sel.xpath('//@href').extract_first()

            id, type = self.get_id(url)
            # id = sel.xpath('//@data-ds-appid').extract_first()
            name = sel.xpath('//div[@class="col search_name ellipsis"]/span/text()').extract_first()

            msg = (None, type, name, url, 'no', response.meta.get('page'))
            command = ("INSERT IGNORE INTO {} "
                       "(id, type, name, url, is_crawled, page)"
                       "VALUES(%s, %s, %s, %s, %s, %s)".format(config.steam_game_urls_table))

            self.sql.insert_data(command, msg)

    def error_parse(self, faiture):
        request = faiture.request
        utils.log('error_parse url:%s meta:%s' % (request.url, request.meta))

    def get_id(self, url):
        type = ''
        if '/sub/' in url:
            pattern = re.compile('/sub/(\d+)/')
            type = 'sub'
        elif '/app/' in url:
            pattern = re.compile('/app/(\d+)/', re.S)
            type = 'app'
        elif '/bundle/' in url:
            pattern = re.compile('/bundle/(\d+)/', re.S)
            type = 'bundle'
        else:
            pattern = re.compile('/(\d+)/', re.S)
            type = 'other'
            utils.log('get_id other url:%s' % url)

        id = re.search(pattern, url)
        if id:
            id = id.group(1)
            return id, type

        utils.log('get_id error url:%s' % url)
        return 0, 'error'

    def save_page(self, file_name, data):
        with open(file_name, 'w') as f:
            f.write(data)
            f.close()
