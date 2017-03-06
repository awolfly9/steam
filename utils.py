#-*- coding: utf-8 -*-

import logging
import traceback
import datetime
import platform
import os

from bs4 import CData
from bs4 import NavigableString


def make_dir(dir):
    log('make dir:%s' % dir)
    if not os.path.exists(dir):
        os.makedirs(dir)


def log(msg, level = logging.DEBUG):
    logging.log(level, msg)
    print('%s [level:%s] msg:%s' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), level, msg))

    if level == logging.WARNING or level == logging.ERROR:
        for line in traceback.format_stack():
            print(line.strip())

        for line in traceback.format_stack():
            logging.log(level, line.strip())


def get_first_text(soup, strip = False, types = (NavigableString, CData)):
    data = None
    for s in soup._all_strings(strip, types = types):
        data = s
        break
    return data


def get_texts(soup, strip = False, types = (NavigableString, CData)):
    texts = []
    for s in soup._all_strings(strip, types = types):
        texts.append(s)

    return texts


def get_platform():
    plat = platform.platform()
    if plat.find('Darwin') != -1:
        return 'mac'
    elif plat.find('Linux') != -1:
        return 'linux'
    else:
        return 'mac'


def get_date():
    return datetime.datetime.today().strftime('%Y-%m-%d')


def get_create_table_command(table_name):
    command = (
        "CREATE TABLE IF NOT EXISTS {} ("
        "`id` INT(8) NOT NULL AUTO_INCREMENT UNIQUE,"
        "`name` TEXT NOT NULL,"
        "`price` TEXT DEFAULT NULL,"
        # "`metacritic_score` TEXT DEFAULT NULL,"
        # "`reviews_overall_positive` TEXT NOT NULL,"
        # "`reviews_overall_positive_percent` TEXT NOT NULL,"
        # "`reviews_recent_positive` TEXT NOT NULL,"
        # "`reviews_recent_positive_percent` TEXT NOT NULL,"
        # "`tags` TEXT DEFAULT NULL,"
        # "`review_all` TEXT DEFAULT NULL,"
        # "`review_positive` TEXT DEFAULT NULL,"
        # "`review_negative` TEXT DEFAULT NULL,"
        # "`review_purchase_steam` TEXT DEFAULT NULL,"
        # "`review_purchase_cd_key` TEXT DEFAULT NULL,"
        # "`review_chinese_language` TEXT DEFAULT NULL,"
        # "`achievements` TEXT DEFAULT NULL,"
        # "`curators` TEXT DEFAULT NULL,"
        # "`category` TEXT NOT NULL,"
        # "`genre` TEXT NOT NULL,"
        # "`developer` TEXT NOT NULL,"
        # "`publisher` TEXT NOT NULL,"
        # "`release_date` TEXT NOT NULL,"
        # "`dlc_number` TEXT DEFAULT NULL,"
        # "`dlc_names` TEXT DEFAULT NULL,"
        # "`dlc_prices` TEXT DEFAULT NULL,"
        "`url` TEXT NOT NULL,"
        # "`language_number` TEXT DEFAULT NULL,"
        # "`languages` TEXT DEFAULT NULL,"
        # "`description` TEXT NOT NULL,"
        # "`save_time` TIMESTAMP NOT NULL,"
        "PRIMARY KEY(id)"
        ") ENGINE=InnoDB".format(table_name))

    # command = (
    #     "CREATE TABLE IF NOT EXISTS {} ("
    #     "`id` INT(8) NOT NULL AUTO_INCREMENT UNIQUE,"
    #     "`name` TEXT NOT NULL,"
    #     "`price` INT(4) DEFAULT NULL,"
    #     "`metacritic_score` INT(3) DEFAULT NULL,"
    #     "`reviews_overall_positive` INT(6) NOT NULL,"
    #     "`reviews_overall_positive_percent` CHAR(3) NOT NULL,"
    #     "`reviews_recent_positive` INT(6) NOT NULL,"
    #     "`reviews_recent_positive_percent` CHAR(3) NOT NULL,"
    #     "`tags` TEXT DEFAULT NULL,"
    #     "`review_all` INT(7) DEFAULT NULL,"
    #     "`review_positive` INT(7) DEFAULT NULL,"
    #     "`review_negative` INT(7) DEFAULT NULL,"
    #     "`review_purchase_steam` INT(7) DEFAULT NULL,"
    #     "`review_purchase_cd_key` INT(7) DEFAULT NULL,"
    #     "`review_chinese_language` INT(7) DEFAULT NULL,"
    #     "`achievements` INT(7) DEFAULT NULL,"
    #     "`curators` INT(5) DEFAULT NULL,"
    #     "`category` TEXT NOT NULL,"
    #     "`genre` TEXT NOT NULL,"
    #     "`developer` TEXT NOT NULL,"
    #     "`publisher` TEXT NOT NULL,"
    #     "`release_date` DATE NOT NULL,"
    #     "`dlc_number` INT(4) DEFAULT NULL,"
    #     "`dlc_names` TEXT DEFAULT NULL,"
    #     "`dlc_prices` TEXT DEFAULT NULL,"
    #     "`url` TEXT NOT NULL,"
    #     "`language_number` INT(2) DEFAULT NULL,"
    #     "`languages` TEXT DEFAULT NULL,"
    #     "`description` TEXT NOT NULL,"
    #     "`save_time` TIMESTAMP NOT NULL,"
    #     "PRIMARY KEY(id)"
    #     ") ENGINE=InnoDB".format(table_name))

    return command


def get_insert_data_command(table_name):
    command = ("INSERT IGNORE INTO {} "
               "(id, name, price, url)"
               "VALUES(%s, %s, %s, %s)".format(table_name))
    # command = ("INSERT IGNORE INTO {} "
    #            "(id, name, price, metacritic_score, reviews_overall_positive, reviews_overall_positive_percent, "
    #            "reviews_recent_positive, reviews_recent_positive_percent, tags, review_all, review_positive, "
    #            "review_negative, review_purchase_steam, review_purchase_cd_key, review_chinese_language, "
    #            "achievements, curators, category, genre, developer, publisher, release_date, dlc_number, dlc_names, "
    #            "dlc_prices, url, language_number, languages, description, save_time)"
    #            "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
    #            "%s, %s, %s, %s, %s, %s, %s)".format(table_name))

    return command
