# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
import time
import os
import paramiko
from urllib.request import urlretrieve
from lxml import etree
from nationStatics.items import NationstaticsItem
import string, random


class ExampleSpider(RedisSpider):
    name = 'phone'
    # allowed_domains = ['stats.gov.cn']
    # start_urls = ['http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/index.html']
    redis_key = "phone:start_urls"
    os.makedirs('./image/', exist_ok=True)

    def __init__(self, *args, **kwargs):
        domain = kwargs.pop('domain', '')
        self.allowed_domains = filter(None, domain.split(','))
        super(ExampleSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        print(response.xpath("//div[@id='infolist']/table[@class='small-tbimg ac_container']/tr")[0:6])
        print(len((response.xpath("//div[@id='infolist']/table[@class='small-tbimg ac_container']/tr")[0:6])))
        for each in response.xpath("//div[@id='infolist']/table[@class='small-tbimg ac_container']/tr")[0:6]:
            link1 = each.xpath("./td[@class='t']/a[@class='t ac_linkurl']/@href").extract_first()
            strlink = str(link1)

            if strlink != None:
                if strlink[0:2] != 'ht':
                    strlink = "https:" + strlink
                else:
                    yield scrapy.Request(link1, callback=self.parse_item)
                if strlink[0:5] == 'https':
                    yield scrapy.Request(link1, callback=self.parse_item)

    def parse_item(self, response):
        item = NationstaticsItem()
        item["type"] = "二手手机"
        ran = random.randint(1, 30)
        item["begintime"] = str(int(time.time()) + ran)
        rec = etree.HTML(response.text)
        title = rec.xpath("//div[@class='detail-title']/h1/text()")
        if title:
            item["title"] = str(title[0])
        else:
            item["title"] = ""
        price = rec.xpath("//div[@class='infocard__container__item__main']/span/text()")
        pricelist = price[0].split()
        if price:
            item["price"] = str(pricelist[0])
        else:
            item["price"] = ""
        man = rec.xpath(
            "//div[@class='shopinfo__title']/h2/text()")
        if man:
            item["man"] = str(man[0])
        else:
            item["man"] = ""

        num_start = ['134', '135', '136', '137', '138', '139', '150', '151', '152', '158', '159', '157', '182', '187',
                     '188', '147', '130', '131', '132', '155', '156', '185', '186', '133', '153', '180', '189']
        start = random.choice(num_start)
        end = ''.join(random.sample(string.digits, 8))
        res = start + end
        item["phone"] = str(res)

        desc = rec.xpath(
            "//div[@class='descriptionBox detail-desc__content__desc__box']/div[@class='foldingbox']/article[@class='description_con']/text()")
        if desc:
            item["desc"] = str(desc[0])
        else:
            item["desc"] = ""

        new_start = ['1', '2', '3', '4']
        item["new_old"] = random.choice(new_start)

        if "苹果" in title:
            item["pinpai"] = 1
        elif "iphone" in title:
            item["pinpai"] = 1
        elif "三星" in title:
            item["pinpai"] = 2
        elif "小米" in title:
            item["pinpai"] = 3
        elif "乐视" in title:
            item["pinpai"] = 4
        elif "华为" in title:
            item["pinpai"] = 5
        elif "联想" in title:
            item["pinpai"] = 6
        elif "锤子" in title:
            item["pinpai"] = 7
        elif "诺基亚" in title:
            item["pinpai"] = 8
        elif "HTC" in title:
            item["pinpai"] = 9
        else:
            item["pinpai"] = 14

        urlname = ""
        num = 0
        urlArr = []
        preUrlArr = []
        numArr = []
        for each in response.xpath("//div[@class='switch__small-img']/ul[@class='switch__small-img__main _reset_box']/li"):
            imgUrl = each.xpath("./img/@src").extract_first()

            print(imgUrl)
            imgUrl = "http:" + imgUrl
            capta = ''
            words = ''.join((string.ascii_letters, string.digits))
            for i in range(5):
                capta += random.choice(words).lower()
            print(capta)
            # 下载图片到本地
            imgname = int(time.time())
            urlretrieve(imgUrl, './image/' + 'pre_' + str(imgname) + capta + '.jpg')
            # 本地图片上传到sftp远程服务器
            transport = paramiko.Transport(('*.*.*.*', 22))
            transport.connect(username='root', password='password')

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

        item["urlArr"] = urlArr
        item["preUrlArr"] = preUrlArr
        item["numArr"] = numArr
        item["imgUrl"] = urlname
        item["num"] = num
        yield item

    @staticmethod
    def strformat(self, str1):
        return str(str1).replace(u'\xa0', u'').replace(" ", "").strip()
