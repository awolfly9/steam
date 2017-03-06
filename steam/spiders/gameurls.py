#-*- coding: utf-8 -*-

import re
import config
import utils

from scrapy.spiders import CrawlSpider, Spider
from scrapy.spiders import Rule
from scrapy import Request, FormRequest
from scrapy.linkextractors.sgml import SgmlLinkExtractor as sle
from scrapy.selector import Selector
from bs4 import BeautifulSoup
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

        self.game_count = 0

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
            count = count + 1

        self.game_count = self.game_count + count
        utils.log('game_list length:%s insert count:%s self.game_count:%s meta:%s' %
                  (str(len(game_list)), str(count), str(self.game_count), response.meta))

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

    def parse_game(self, response):
        self.log('parse_game:\n%s' % response.url)

        url = response.url
        pattern = re.compile('/app/(\d+)/', re.S)
        id = re.search(pattern, url)
        if id:
            id = id.group(1)

        file_name = '%s/%s.html' % (self.dir_game, id)
        self.save_page(file_name, response.body)

        soup = BeautifulSoup(response.body, 'lxml')
        sel = Selector(text = response.body)

        name = sel.xpath('//div[@class="apphub_AppName"]/text()').extract_first()
        #print('name:%s' % name)
        price = sel.xpath('//div[@class="game_purchase_action"]/div/div/text()').extract_first()
        #print('price:%s' % price)

        metacritic_score = sel.xpath('//div[@class="score high"]/text()').extract_first()
        #print('metacritic_score:%s' % metacritic_score)

        reviews_recent_positive = sel.xpath('//div[@class="user_reviews"]/div[2]/div[2]/span[2]/text()').extract_first()
        #print('reviews_recent_positive:%s' % reviews_recent_positive)

        reviews_recent_positive_percent = sel.xpath(
                '//div[@class="user_reviews"]/div[2]/div[2]/span[3]/text()').extract_first()
        #print('reviews_recent_positive_percent:%s' % reviews_recent_positive_percent)

        reviews_overall_positive = sel.xpath(
                '////div[@class="user_reviews"]/div[3]/div[2]/span[2]/text()').extract_first()
        #print('reviews_overall_positive:%s' % reviews_overall_positive)

        reviews_overall_positive_percent = sel.xpath(
                '//div[@class="user_reviews"]/div[3]/div[2]/span[3]/text()').extract_first()
        #print('reviews_overall_positive_percent:%s' % reviews_overall_positive_percent)

        tags = soup.find(attrs = {'class': 'glance_tags popular_tags'})
        #print('tags:%s' % tags.text)

        review_all = sel.xpath('//label[@for="review_type_all"]/span/text()').extract_first()
        #print('review_all:%s' % review_all)

        review_positive = sel.xpath('//label[@for="review_type_positive"]/span/text()').extract_first()
        #print('review_positive:%s' % review_positive)

        review_negative = sel.xpath('//label[@for="review_type_negative"]/span/text()').extract_first()
        #print('review_negative:%s' % review_negative)

        review_purchase_steam = sel.xpath('//label[@for="purchase_type_steam"]/span/text()').extract_first()
        #print('review_purchase_steam :%s' % review_purchase_steam)

        review_purchase_cd_key = sel.xpath('//label[@for="purchase_type_cd_key"]/span/text()').extract_first()
        #print('review_purchase_cd_key:%s' % review_purchase_cd_key)

        review_chinese_language = sel.xpath('//label[@for="review_language_mine"]/span/text()').extract_first()
        #print('review_chinese_language:%s' % review_chinese_language)

        achievements = sel.xpath('//div[@id="achievement_block"]/div/text()').extract_first()
        #print('achievements:%s' % achievements)

        curators = ''

        category = soup.find(name = 'div', attrs = {'class': 'breadcrumbs'})
        #print('category:%s' % category.text)

        genre = sel.xpath('//div[@class="block_content"]/div/div/a/text()').extract_first()
        #print('genre:%s' % genre)

        developer = sel.xpath('//div[@class="block_content"]/div/div/a[2]/text()').extract_first()
        #print('developer:%s' % developer)

        publisher = sel.xpath('//div[@class="block_content"]/div/div/a[3]/text()').extract_first()
        #print('publisher:%s' % publisher)

        release_date = sel.xpath('//div[@class="block_content"]/div/div/b[5]/text()').extract_first()
        #print('release_date:%s' % release_date)

        description = sel.xpath('//div[@class="game_description_snippet"]/text()').extract_first()
        #print('description:%s' % description)

        dlc_number = ''
        dlc_names = ''
        dlc_prices = ''
        language_number = ''
        languages = ''

        # msg = (id, name, price, metacritic_score, reviews_overall_positive, reviews_overall_positive_percent,
        #        reviews_recent_positive, reviews_recent_positive_percent, tags, review_all, review_positive,
        #        review_negative, review_purchase_steam, review_purchase_cd_key, review_chinese_language, achievements,
        #        curators, category, genre, developer, publisher, release_date, dlc_number, dlc_names, dlc_prices, url,
        #        language_number, languages, description, None)

        msg = (id, name, price, url)
        command = utils.get_insert_data_command(config.steam_game_table)

        self.sql.insert_data(command, msg)

    def parse_steam(self, response):
        file_name = 'log/steam_urls.txt'
        url = response.url + '\n'
        with open(file_name, 'a+') as f:
            f.write(url)
            f.close()

    def parse_game_by_number(self, response):
        self.log('parse_game_by_number:\n%s' % response.url)

    def parse_player(self, response):
        self.log('parse_player:\n%s' % response.url)

        url = response.url
        str(url).split('/')
        names = str(url).split('/')
        name = names[len(names) - 1]

        with open('players/%s.html' % name, 'w') as f:
            f.write(response.body)
            f.close()

    def save_page(self, file_name, data):
        with open(file_name, 'w') as f:
            f.write(data)
            f.close()
