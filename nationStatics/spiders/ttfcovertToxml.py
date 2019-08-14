

# font = TTFont('58.ttf') # 打开本地的ttf文件
# font.saveXML('58.xml')  # 转换成xml

# from fontTools.ttLib import TTFont
# # # #
# # # # font = TTFont('58.ttf') #打开本地的ttf文件
# # # # bestcmap = font['cmap'].getBestCmap()
# # # # print(bestcmap)

import re
from fontTools.ttLib import TTFont

font = TTFont('58.ttf') #打开本地的ttf文件
bestcmap = font['cmap'].getBestCmap()
newmap = dict()
for key in bestcmap.keys():
    value = int(re.search(r'(\d+)', bestcmap[key]).group(1)) - 1
    key = hex(key)
    newmap[key] = value
print(newmap)