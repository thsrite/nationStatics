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
    name = 'tongcheng'
    # allowed_domains = ['stats.gov.cn']
    # start_urls = ['http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/index.html']
    redis_key = "tongcheng:start_urls"
    os.makedirs('./image/', exist_ok=True)

    def __init__(self, *args, **kwargs):
        domain = kwargs.pop('domain', '')
        self.allowed_domains = filter(None, domain.split(','))
        super(ExampleSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        print(response.xpath("//div[@class='list-box']/ul[@class='house-list']/li[@class='house-cell']")[0:6])
        for each in response.xpath("//div[@class='list-box']/ul[@class='house-list']/li[@class='house-cell']")[0:6]:
            link1 = each.xpath("./div[@class='des']/h2/a/@href").extract_first()
            yield scrapy.Request(link1, callback=self.parse_item)

    def parse_item(self, response):
        item = NationstaticsItem()
        item["type"] = "房屋出租"
        item["begintime"] = str(int(time.time()))
        base64_str = re.search("base64,(.*?)'\)", response.text).group(1)
        b = base64.b64decode(base64_str)
        font = TTFont(io.BytesIO(b))
        bestcmap = font['cmap'].getBestCmap()
        newmap = dict()
        for key in bestcmap.keys():
            value = int(re.search(r'(\d+)', bestcmap[key]).group(1)) - 1
            key = hex(key)
            newmap[key] = value
        # 把页面上自定义字体替换成正常字体
        response_ = response.text
        for key, value in newmap.items():
            key_ = key.replace('0x', '&#x') + ';'
            if key_ in response_:
                response_ = response_.replace(key_, str(value))
        # 获取标题
        rec = etree.HTML(response_)
        title = rec.xpath("//div[@class='house-title']/h1[@class='c_333 f20 strongbox']/text()")
        if title:
            item["title"] = str(title[0])
        else:
            item["title"] = ""
        price = rec.xpath("//div[@class='house-pay-way f16']/span[@class='c_ff552e']/b[@class='f36 strongbox']/text()")
        if price:
            item["price"] = str(price[0])
        else:
            item["price"] = ""
        man = rec.xpath(
            "//div[@class='house-basic-desc']/div[@id='bigCustomer']/p[@class='agent-name f16 pr']/a[@class='c_000']/text()")
        if man:
            item["man"] = str(man[0])
        else:
            item["man"] = ""
        phone = rec.xpath("//div[@class='house-chat-phonenum']/p[@class='phone-num strongbox']/text()")
        print(phone)
        if phone:
            item["phone"] = str(phone[0])
        else:
            item["phone"] = ""
        desc = rec.xpath("//ul[@class='introduce-item']/li[2]/span[@class='a2']/text()")
        desc1 = "".join(desc)
        if desc:
            item["desc"] = str(desc1).replace(' ', '')
        else:
            item["desc"] = ""
        urlname = ""
        for each in rec.xpath("//ul[@class='f14']/li"):
            keys = each.xpath("./span[@class='c_888 mr_15']/text()")
            values = each.xpath("./span[2]/text()")
            if keys:
                keys = each.xpath("./span[@class='c_888 mr_15']/text()")[0]
                if (keys == '租赁方式：'):
                    if values:
                        item["zlfs"] = self.strformat(values[0])
                    else:
                        item["zlfs"] = ""
                if (keys == '房屋类型：'):
                    if values:
                        fwlx = self.strformat(values[0])
                        print(fwlx[0])
                        print(fwlx[2])
                        # item["shi"] = fwlx[0]
                        # item["ting"] = fwlx[2]
                        # item["wei"] = fwlx[4]
                        if int(fwlx[0]) + int(fwlx[2]) > 5:
                            item["room_type"] = 1
                        elif int(fwlx[0]) + int(fwlx[2]) == 5:
                            item["room_type"] = 2
                        elif int(fwlx[0]) == 3 and int(fwlx[2]) == 1:
                            item["room_type"] = 3
                        elif int(fwlx[0]) == 2 and int(fwlx[2]) == 2:
                            item["room_type"] = 4
                        elif int(fwlx[0]) + int(fwlx[2]) == 3:
                            item["room_type"] = 5
                        elif int(fwlx[0]) + int(fwlx[2]) == 2:
                            item["room_type"] = 6
                        elif int(fwlx[0]) + int(fwlx[2]) == 1:
                            item["room_type"] = 7
                        print(item["room_type"])
                    else:
                        item["room_type"] = ""
                        # item["shi"] = ""
                        # item["ting"] = ""
                        # item["wei"] = ""
        num = 0
        url = ""
        urlArr=[]
        preUrlArr=[]
        numArr=[]
        for each in response.xpath("//div[@class='basic-pic-list pr']/ul[@id='leftImg']/li"):
            imgUrl = each.xpath("./img/@src").extract_first()

            print(imgUrl)
            if imgUrl[0:2] != 'ht':
                imgUrl = "https:" + imgUrl
            print(imgUrl)
            capta = ''
            words = ''.join((string.ascii_letters, string.digits))
            for i in range(5):
                capta += random.choice(words).lower()
            print(capta)
            # 下载图片到本地
            imgname = int(time.time())
            urlretrieve(imgUrl, './image/' + 'pre_' + str(imgname) + capta + '.jpg')
            # 本地图片上传到sftp远程服务器
            transport = paramiko.Transport(('47.105.207.207', 22))
            transport.connect(username='root', password='Zhu@Hog@0117')

            sftp = paramiko.SFTPClient.from_transport(transport)  # 如果连接需要密钥，则要加上一个参数，hostkey="密钥"

            sftp.put('./image/' + 'pre_' + str(imgname) + capta + '.jpg',
                     '/var/www/html/attachment/information/201903/' + 'pre_' + str(
                         imgname) + capta + '.jpg')  # 将本地的文件上传至服务器
            sftp.put('./image/' + 'pre_' + str(imgname) + capta + '.jpg',
                     '/var/www/html/attachment/information/201903/' + str(imgname) + capta + '.jpg')  # 将本地的文件上传至服务器

            transport.close()  # 关闭连接

            url = '/attachment/information/201903/' + str(imgname) + capta + '.jpg'
            urlname = '/attachment/information/201903/' + 'pre_' + str(imgname) + capta + '.jpg'
            urlArr.append(url)
            preUrlArr.append(urlname)
            numArr.append(num)
            num = num + 1

        item["urlArr"]=urlArr
        item["preUrlArr"]=preUrlArr
        item["numArr"]=numArr
        item["imgUrl"] = urlname
        item["num"] = num
        yield item

    def strformat(self, str1):
        return str(str1).replace(u'\xa0', u'').replace(" ", "").strip()
