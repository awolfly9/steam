#-*- coding: utf-8 -*-

from scrapy.selector import Selector
from bs4 import BeautifulSoup

with open('games/220.html', 'r')as f:
    text = f.read()
    f.close()

    soup = BeautifulSoup(text, 'lxml')

    sel = Selector(text = text)
    title = sel.xpath('//div[@class="apphub_AppName"]/text()').extract_first()
    print('title:%s' % title)
    price = sel.xpath('//div[@class="game_purchase_action"]/div/div/text()').extract_first()
    print('price:%s' % price)

    metacritic_score = sel.xpath('//div[@class="score high"]/text()').extract_first()
    print('metacritic_score:%s' % metacritic_score)

    reviews_recent_positive = sel.xpath('//div[@class="user_reviews"]/div[2]/div[2]/span[2]/text()').extract_first()
    print('reviews_recent_positive:%s' % reviews_recent_positive)

    reviews_recent_positive_percent = sel.xpath(
            '//div[@class="user_reviews"]/div[2]/div[2]/span[3]/text()').extract_first()
    print('reviews_recent_positive_percent:%s' % reviews_recent_positive_percent)

    reviews_overall_positive = sel.xpath(
            '////div[@class="user_reviews"]/div[3]/div[2]/span[2]/text()').extract_first()
    print('reviews_overall_positive:%s' % reviews_overall_positive)

    reviews_overall_positive_percent = sel.xpath(
            '//div[@class="user_reviews"]/div[3]/div[2]/span[3]/text()').extract_first()
    print('reviews_overall_positive_percent:%s' % reviews_overall_positive_percent)

    tags = soup.find(attrs = {'class': 'glance_tags popular_tags'})
    print('tags:%s' % tags.text)

    review_all = sel.xpath('//label[@for="review_type_all"]/span/text()').extract_first()
    print('review_all:%s' % review_all)

    review_positive = sel.xpath('//label[@for="review_type_positive"]/span/text()').extract_first()
    print('review_positive:%s' % review_positive)

    review_negative = sel.xpath('//label[@for="review_type_negative"]/span/text()').extract_first()
    print('review_negative:%s' % review_negative)

    review_purchase_steam = sel.xpath('//label[@for="purchase_type_steam"]/span/text()').extract_first()
    print('review_purchase_steam :%s' % review_purchase_steam )

    review_purchase_cd_key = sel.xpath('//label[@for="purchase_type_cd_key"]/span/text()').extract_first()
    print('review_purchase_cd_key:%s' % review_purchase_cd_key)

    review_chinese_language = sel.xpath('//label[@for="review_language_mine"]/span/text()').extract_first()
    print('review_chinese_language:%s' % review_chinese_language)

    achievements = sel.xpath('//div[@id="achievement_block"]/div/text()').extract_first()
    print('achievements:%s' % achievements)

    curators = ''

    category = soup.find(name = 'div', attrs = {'class': 'breadcrumbs'})
    print('category:%s' % category.text)

    genre = sel.xpath('//div[@class="block_content"]/div/div/a/text()').extract_first()
    print('genre:%s' % genre)

    developer = sel.xpath('//div[@class="block_content"]/div/div/a[2]/text()').extract_first()
    print('developer:%s' % developer)

    publisher = sel.xpath('//div[@class="block_content"]/div/div/a[3]/text()').extract_first()
    print('publisher:%s' % publisher)

    release_date = sel.xpath('//div[@class="block_content"]/div/div/b[5]/text()').extract_first()
    print('release_date:%s' % release_date)

    description = sel.xpath('//div[@class="game_description_snippet"]/text()').extract_first()
    print('description:%s' % description)
