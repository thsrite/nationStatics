import random
from scrapy import cmdline, item
import redis
pool = redis.ConnectionPool(host='127.0.0.1')
r=redis.Redis(connection_pool=pool)
# r.lpush("crawl21cpContentAll:start_urls","http://www.21cp.com/yuanliao/list/POM.htm")
# r.lpush("bulou:start_urls","http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/44.html")
for elem in r.keys():
    r.delete(elem)
pnnum = random.randint(1, 70)

r.lpush("zhaopin:start_urls","https://qd.58.com/job/pn" + str(pnnum) + "/?param6693=8|10&utm_source=market&spm=u-2d2yxv86y3v43nkddh1.BDPCPZ_BT&PGTID=0d100000-0007-a878-0909-0293a903cea7&ClickID=12")
cmdline.execute(['scrapy','crawl','zhaopin'])
