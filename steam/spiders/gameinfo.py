# coding=utf-8

import re
import config
import utils

from scrapy.spiders import CrawlSpider
from scrapy import Request, FormRequest
from scrapy.selector import Selector
from bs4 import BeautifulSoup
from sqlhelper import SqlHelper


class GameInfo(CrawlSpider):
    name = 'game_info'

    def __init__(self, *a, **kw):
        super(GameInfo, self).__init__(*a, **kw)

        self.dir_game = 'log/%s' % self.name
        self.sql = SqlHelper()
        self.init()

        utils.make_dir(self.dir_game)

        self.error_count = 0

    def init(self):
        command = (
            "CREATE TABLE IF NOT EXISTS {} ("
            "`id` INT(8) NOT NULL AUTO_INCREMENT,"
            "`name` TEXT NOT NULL,"
            "`price` INT(5) NOT NULL,"
            "`metacritic_score` FLOAT DEFAULT NULL,"
            "`user_reviews_count` INT(6) NOT NULL,"
            "`positive_user_reviews_count` INT(6) NOT NULL,"
            "`positive_percent` FLOAT NOT NULL ,"
            "`negative_user_reviews_count` INT(6) NOT NULL,"
            '`steam_user_reviews_count` INT(6) NOT NULL,'
            '`non_steam_user_reviews_count` INT(6) NOT NULL,'
            '`english_user_reviews_count` INT(6) NOT NULL,'
            '`non_english_user_reviews_count` INT(6) NOT NULL,'
            "`tag_list` TEXT DEFAULT NULL,"
            "`achievements_count` INT(4) DEFAULT NULL,"
            "`category` TEXT NOT NULL,"
            "`genre` TEXT NOT NULL,"
            "`developer` TEXT NOT NULL,"
            "`publisher` TEXT NOT NULL,"
            "`release_date` TEXT NOT NULL,"
            "`url` TEXT NOT NULL,"
            "`language_number` INT(3) DEFAULT NULL,"
            "`description` TEXT DEFAULT NULL,"
            "`save_time` TIMESTAMP NOT NULL,"
            "PRIMARY KEY(id)"
            ") ENGINE=InnoDB".format(config.steam_game_info_table))
        self.sql.create_table(command)

    def start_requests(self):
        command = "SELECT * FROM {} WHERE is_crawled = \'no\' AND type = \'app\'".format(config.steam_game_urls_table)
        data = self.sql.query(command)
        for i, item in enumerate(data):
            yield Request(
                    url = item[3],
                    dont_filter = True,
                    method = 'GET',
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
                        'item': item,
                        'id': item[0],
                    },
                    cookies = {
                        'mature_content': '1',
                    },
                    callback = self.parse_game,
                    errback = self.error_parse,
            )

    def parse_game(self, response):
        self.log('parse_game url:%s' % response.url)
        id = response.meta.get('id')

        # file_name = '%s/%s.html' % (self.dir_game, id)
        # self.save_page(file_name, response.body)

        if u'Please enter your birth date to continue' in response.body:
            self.log('Please enter your birth date to continue meta:%s' % response.meta)

            url = 'http://store.steampowered.com/agecheck/app/%s/' % str(id)
            return FormRequest(
                    url = url,
                    dont_filter = True,
                    method = 'POST',
                    formdata = {
                        'ageDay': str(range(1, 25)),
                        'ageMonth': 'January',
                        'ageYear': str(range(1980, 1995)),
                        'snr': '1_agecheck_agecheck__age-gate',
                    },
                    callback = self.parse_game
            )

        soup = BeautifulSoup(response.body, 'lxml')
        sel = Selector(text = response.body)

        name = sel.xpath('//div[@class="apphub_AppName"]/text()').extract_first()
        if name == '' or name == None:
            self.log('no get data meta:%s' % response.meta)
            return

        price = sel.xpath('//div[@class="game_purchase_price price"]/text()').extract_first()
        try:
            p = price.split('¥')
            price = int(p[1])
        except:
            price = -1

        # 该游戏在 metacritic 上的评分
        metacritic_score = sel.xpath('//div[@class="score high"]/text()').extract_first()
        try:
            metacritic_score = int(metacritic_score)
        except:
            metacritic_score = -1

        # 所有用户回复数量
        user_reviews_count = sel.xpath('//label[@for="review_type_all"]/span/text()').extract_first()
        user_reviews_count = self.count_to_int(user_reviews_count)

        # 好评的用户数量
        positive_user_reviews_count = sel.xpath('//label[@for="review_type_positive"]/span/text()').extract_first()
        positive_user_reviews_count = self.count_to_int(positive_user_reviews_count)

        # 好评的百分比
        if user_reviews_count != -1 and positive_user_reviews_count != -1:
            positive_percent = positive_user_reviews_count * 1.0 / user_reviews_count * 100
        else:
            positive_percent = 0

        # 差评的用户数量
        negative_user_reviews_count = sel.xpath('//label[@for="review_type_negative"]/span/text()').extract_first()
        negative_user_reviews_count = self.count_to_int(negative_user_reviews_count)

        # 在 steam 购买的用户的评论数
        steam_user_reviews_count = sel.xpath('//label[@for="purchase_type_steam"]/span/text()').extract_first()
        steam_user_reviews_count = self.count_to_int(steam_user_reviews_count)

        # 在其他平台购买的用户的评论数
        non_steam_user_reviews_count = sel.xpath('//label[@for="purchase_type_non_steam"]/span/text()').extract_first()
        non_steam_user_reviews_count = self.count_to_int(non_steam_user_reviews_count)

        # 英语评论的数量
        english_user_reviews_count = sel.xpath('//label[@for="review_language_mine"]/span/text()').extract_first()
        english_user_reviews_count = self.count_to_int(english_user_reviews_count)

        # 非英语的评论数量
        non_english_user_reviews_count = user_reviews_count - english_user_reviews_count

        # 该游戏的标签列表
        try:
            tags = soup.find(attrs = {'class': 'glance_tags popular_tags'})
            tag_list = tags.text.replace('\t', '')
            tag_list = tag_list.replace('\n', ',')
        except:
            tag_list = ''

        # 该游戏的成就数量
        achievements = sel.xpath('//div[@id="achievement_block"]/div/text()').extract_first()
        try:
            achievements_count = re.search('\d+', achievements, re.S).group(0)
            achievements_count = int(achievements_count)
        except:
            achievements_count = 0

        # 该游戏的分类 All Games > Action Games > Counter-Strike
        try:
            category = soup.find(name = 'div', attrs = {'class': 'breadcrumbs'}).text
            category = category.replace('\t', '')
            category = category.replace('\n', '')
        except:
            category = ''

        # 游戏类型
        genre = sel.xpath('//div[@class="block_content"]/div/div/a/text()').extract_first()

        # 游戏开发商
        developer = sel.xpath('//div[@class="block_content"]/div/div/a[2]/text()').extract_first()

        # 游戏发行商
        publisher = sel.xpath('//div[@class="block_content"]/div/div/a[3]/text()').extract_first()

        # 游戏发行日期
        release_date = sel.xpath('//div[@class="release_date"]/span/text()').extract_first()

        # 游戏支持的语言
        language_number = len(sel.xpath('//table[@class="game_language_options"]/tr').extract()) - 1

        # 游戏描述
        description = sel.xpath('//div[@class="game_description_snippet"]/text()').extract_first()

        # 抓取该游戏时间
        save_time = None

        msg = (id, name, price, response.url, metacritic_score, user_reviews_count, positive_user_reviews_count,
               positive_percent, negative_user_reviews_count, steam_user_reviews_count, non_steam_user_reviews_count,
               english_user_reviews_count, non_english_user_reviews_count, tag_list, achievements_count, category,
               genre, developer, publisher, release_date, language_number, description, save_time)

        command = ("INSERT IGNORE INTO {} "
                   "(id, name, price, url, metacritic_score, user_reviews_count, positive_user_reviews_count, "
                   "positive_percent, negative_user_reviews_count, steam_user_reviews_count, "
                   "non_steam_user_reviews_count, english_user_reviews_count, non_english_user_reviews_count, "
                   "tag_list, achievements_count, category, genre, developer, publisher, release_date, "
                   "language_number, description, save_time)"
                   "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
                   "%s)".format(config.steam_game_info_table))

        self.sql.insert_data(command, msg)

        command = "UPDATE {0} SET is_crawled=\'yes\' WHERE id=\'{1}\'".format(config.steam_game_urls_table, id)
        self.sql.execute(command)

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
            return id

        self.error_count = self.error_count + 1
        utils.log('get_id error url:%s' % url)
        return -self.error_count

    def count_to_int(self, data):
        try:
            ret = data
            ret = ret.replace('(', '')
            ret = ret.replace(')', '')
            ret = ret.replace(',', '')

            return int(ret)
        except:
            return -1

    def save_page(self, file_name, data):
        with open(file_name, 'w') as f:
            f.write(data)
            f.close()
