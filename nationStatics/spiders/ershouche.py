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
import string,random


class ExampleSpider(RedisSpider):
    name = 'ershouche'
    # allowed_domains = ['stats.gov.cn']
    # start_urls = ['http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/index.html']
    redis_key = "ershouche:start_urls"
    os.makedirs('./image/', exist_ok=True)

    def __init__(self, *args, **kwargs):
        domain = kwargs.pop('domain', '')
        self.allowed_domains = filter(None, domain.split(','))
        super(ExampleSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        for each in response.xpath("//div[@class='info_list']/ul[@class='car_list ac_container']/li")[0:6]:
            link1 = str(each.xpath("./div/a/@href").extract_first())
            link = link1[2:]
            yield scrapy.Request(link, callback=self.parse_item)

    def parse_item(self, response):
        item = NationstaticsItem()
        item["type"] = "二手车"
        ran = random.randint(61, 90)
        item["begintime"] = str(int(time.time()) + ran)
        # 获取标题
        rec = etree.HTML(response.text)
        title = rec.xpath("//div[@class='content_title']/p[@class='title_p']/text()")
        if title:
            item["title"] = str(title[0])
        else:
            item["title"] = ""
        price = rec.xpath("//div[@class='pricein']/span[@class='price_span']/span/text()")
        if price:
            item["price"] = str(price[0])
        else:
            item["price"] = ""
        man = rec.xpath(
            "//div[@class='saleinfo']/div[@class='contect']/span[@class='name']/a/text()")
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
        desc = rec.xpath("//div[@class='carmiaoshu']/div[@class='cardes_div']/p[@class='cardes']/text()")
        desc1 = "".join(desc)
        print(desc1)
        if desc:
            item["desc"] = str(desc1).replace(' ', '')
        else:
            item["desc"] = ""
        print(item["desc"])
        urlname = ""
        title_list = title[0].split(" ")
        if title_list[0] == '大众':
            item['pinpai'] = 1
        elif title_list[0] == '本田':
            item['pinpai'] = 2
        elif title_list[0] == '丰田':
            item['pinpai'] = 3
        elif title_list[0] == '别克':
            item['pinpai'] = 4
        elif title_list[0] == '奥迪':
            item['pinpai'] = 5
        elif title_list[0] == '奔驰':
            item['pinpai'] = 6
        elif title_list[0] == '宝马':
            item['pinpai'] = 7
        elif title_list[0] == '比亚迪':
            item['pinpai'] = 8
        elif title_list[0] == '现代':
            item['pinpai'] = 9
        elif title_list[0] == '雪佛兰':
            item['pinpai'] = 10
        elif title_list[0] == '奇瑞':
            item['pinpai'] = 11
        elif title_list[0] == '福特':
            item['pinpai'] = 12
        elif title_list[0] == '日产':
            item['pinpai'] = 13
        elif title_list[0] == '马自达':
            item['pinpai'] = 14
        elif title_list[0] == '金杯':
            item['pinpai'] = 15
        elif title_list[0] == '路虎':
            item['pinpai'] = 16
        else:
            item['pinpai'] = 17

        year = str(title_list[2])
        che_year = year[0:4]
        if int(che_year) < 2012:
            item["che_year"] = 1
        elif int(che_year) == 2012:
            item["che_year"] = 2
        elif int(che_year) == 2013:
            item["che_year"] = 3
        elif int(che_year) == 2014:
            item["che_year"] = 4
        elif int(che_year) == 2015:
            item["che_year"] = 5
        elif int(che_year) == 2016:
            item["che_year"] = 6

        gongli = rec.xpath("//ul[@class='baseinfor_ul'][1]/li[2]/span[2]/text()")
        gonglilist = gongli[0].split("万")
        item['gongli'] = str(gonglilist[0])

        new_start = ['1', '2', '3', '4']
        item["new_old"] = random.choice(new_start)

        num = 0
        urlArr = []
        preUrlArr = []
        numArr = []
        for each in response.xpath("//div[@id='content_sumary_img']/div[@class='g_thumb_main']/ul[@id='img_smalls']/li"):
            imgUrl = each.xpath("./img/@src").extract_first()

            print(imgUrl)
            if str(imgUrl)[0:4] != "http":
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
            # item["url"] = url
            # item["imgUrl"] = urlname
            num = num + 1

        item["urlArr"] = urlArr
        item["preUrlArr"] = preUrlArr
        item["numArr"] = numArr
        item["imgUrl"] = urlname
        item["num"] = num
        yield item

    def strformat(self, str1):
        return str(str1).replace(u'\xa0', u'').replace(" ", "").strip()
