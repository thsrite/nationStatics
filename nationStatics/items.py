# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NationstaticsItem(scrapy.Item):
     REGION_ID= scrapy.Field()
     DIV_NAME= scrapy.Field()
     FULL_NAME= scrapy.Field()
     TYPE= scrapy.Field()
     #租赁方式
     zlfs = scrapy.Field()
     #房屋类型
     fwlx = scrapy.Field()
     #图片地址
     url = scrapy.Field()
     imgUrl=scrapy.Field()
     #标题
     title = scrapy.Field()
     #价格
     price = scrapy.Field()
     #发布人
     man = scrapy.Field()
     #手机号
     phone=scrapy.Field()
     #描述
     desc=scrapy.Field()
     #发布时间
     begintime=scrapy.Field()
     #房屋类型
     room_type=scrapy.Field()
     #图片数量
     num=scrapy.Field()
     #车品牌
     pinpai=scrapy.Field()
     #照片集合
     urlArr=scrapy.Field()
     #pre照片集合
     preUrlArr=scrapy.Field()
     #照片数量集合
     numArr=scrapy.Field()
     #爬虫类型
     type=scrapy.Field()
     #新旧程度
     new_old=scrapy.Field()
     #学历
     xueli=scrapy.Field()
     #公司名称
     contryname=scrapy.Field()
     #职业类型
     zhiyetype=scrapy.Field()
     #职业
     zhiye=scrapy.Field()
     #职业名称
     zhiyename=scrapy.Field()
     #工作年薪
     work_life=scrapy.Field()
     #福利
     fuli=scrapy.Field()
     #车年限
     che_year=scrapy.Field()
     #车公里数
     gongli=scrapy.Field()