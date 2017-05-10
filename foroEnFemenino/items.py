# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ForoenfemeninoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    forum_url = scrapy.Field()
    forum_title = scrapy.Field()
    subject_url = scrapy.Field()
    subject_title = scrapy.Field()
    subject_user = scrapy.Field()
    subject_num_answer = scrapy.Field()
    subject_date_last_post = scrapy.Field()
    post_title = scrapy.Field()
    post_user_question = scrapy.Field()
    post_date_question = scrapy.Field()
    post_text_question = scrapy.Field()
    post_user_answer = scrapy.Field()
    post_date_answer = scrapy.Field()
    post_text_answer = scrapy.Field()
    user_question_sex = scrapy.Field()
    user_question_name = scrapy.Field()
    user_question_surname = scrapy.Field()
    user_question_age = scrapy.Field()
    user_question_location = scrapy.Field()
    pass
