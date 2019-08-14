# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
import base64
import time
import re
import io
import os
import paramiko
from urllib.request import urlretrieve
from lxml import etree
from fontTools.ttLib import TTFont
from nationStatics.items import NationstaticsItem
import string, random


class ExampleSpider(RedisSpider):
    name = 'zhaopin'
    # allowed_domains = ['stats.gov.cn']
    # start_urls = ['http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/index.html']
    redis_key = "zhaopin:start_urls"
    os.makedirs('./image/', exist_ok=True)

    def __init__(self, *args, **kwargs):
        domain = kwargs.pop('domain', '')
        self.allowed_domains = filter(None, domain.split(','))
        super(ExampleSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        for each in response.xpath("//div[@class='leftCon']/ul[@id='list_con']/li")[0:6]:
            link1 = each.xpath("./div/div/a/@href").extract_first()
            yield scrapy.Request(link1, callback=self.parse_item)

    def parse_item(self, response):
        item = NationstaticsItem()
        item["type"] = "招聘"
        ran = random.randint(31, 60)
        item["begintime"] = str(int(time.time()) + ran)

        # 获取标题
        rec = etree.HTML(response.text)
        title = rec.xpath("//div/span[@class='pos_title']/text()")
        if title:
            item["title"] = str(title[0]).lstrip()
        else:
            item["title"] = ""

        # 获取价格
        num_start = ['8', '2', '3', '4', '5', '6', '7']
        start = random.choice(num_start)
        item["price"] = start

        # 学历
        xueli_start = ['1', '2', '3', '4', '5', '6']
        xueli = random.choice(xueli_start)
        item["xueli"] = xueli

        #工作年限
        work_start = ['1', '2', '3', '4', '5', '6','7']
        work = random.choice(work_start)
        item["work_life"] = work

        #福利
        fuli_start = ['1,2,3', '2,4', '3,5', '1,4', '1,2,5', '1,2,3,4,5,6', '3,4,5,6,7','2,3,4,5,8','1,2,3,4,5,9']
        fuli = random.choice(fuli_start)
        item["fuli"] = str(fuli)

        # 职业类型
        type_start = ['wenyuan', 'caiwu', 'fuwuyuan', 'yewu']
        type1 = random.choice(type_start)
        item["zhiyetype"] = type1
        if type1 == 'fuwuyuan':
            item["zhiye"] = 52
            item["zhiyename"] = "服务员/收银员"
        elif type1 == 'yewu':
            item["zhiye"] = 53
            item["zhiyename"] = "销售/市场/业务员"
        elif type1 == 'wenyuan':
            item["zhiye"] = 54
            item["zhiyename"] = "文员/客服/助理"
        elif type1 == 'caiwu':
            item["zhiye"] = 61
            item["zhiyename"] = "财务/会计"

        #获取公司名称
        contryname = rec.xpath("//div[@class='comp_baseInfo_title']/div[@class='baseInfo_link']/a/text()")
        item["contryname"] = str(contryname)

        # 手机号
        num_start = ['134', '135', '136', '137', '138', '139', '150', '151', '152', '158', '159', '157', '182', '187',
                     '188', '147', '130', '131', '132', '155', '156', '185', '186', '133', '153', '180', '189']
        start = random.choice(num_start)
        end = ''.join(random.sample(string.digits, 8))
        res = start + end
        item["phone"] = str(res)

        desc = rec.xpath("//div[@class='intro']/div[@class='shiji']/p/text()")
        if desc:
            item["desc"] = str(desc[0])
        else:
            item["desc"] = ""

        yield item

    def strformat(self, str1):
        return str(str1).replace(u'\xa0', u'').replace(" ", "").strip()
