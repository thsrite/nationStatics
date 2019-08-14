import random
from scrapy import cmdline, item
import redis
pool = redis.ConnectionPool(host='127.0.0.1')
r=redis.Redis(connection_pool=pool)
# r.lpush("crawl21cpContentAll:start_urls","http://www.21cp.com/yuanliao/list/POM.htm")
# r.lpush("bulou:start_urls","http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/44.html")
for elem in r.keys():
    r.delete(elem)
pnnum = random.randint(2, 31)

r.lpush("phone:start_urls","https://qd.58.com/shouji/pn" + str(pnnum) + "/?utm_source=market&spm=u-2d2yxv86y3v43nkddh1.BDPCPZ_BT&PGTID=0d300024-0007-a066-3dfe-a41ca2c14eba&ClickID=1")
cmdline.execute(['scrapy','crawl','phone'])
