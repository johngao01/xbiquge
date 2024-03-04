import requests
from lxml import etree

novel_url = 'https://www.xbiquge.bz/book/36327/'
novel_title = '诡秘之主'
headers = {
    'authority': 'www.xbiquge.bz',
    'referer': novel_url,
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
}
response = requests.get(novel_url, headers=headers)
response.encoding = 'gbk'
tree = etree.HTML(response.text)
urls = tree.xpath('//div[@id="list"]//a/@href')
for url in urls:
    url = novel_url + url
    response = requests.get(url, headers=headers)
    response.encoding = 'gbk'
    tree = etree.HTML(response.text)
    print(url, end='\t')
    title = tree.xpath('//div[@class="bookname"]/h1/text()')[0]
    print(title)
    content = tree.xpath('//div[@id="content"]/text()')
    with open(f'{novel_title}/{title}.txt', 'w', encoding='utf-8') as f:
        for _ in content[1:]:
            _ = _.strip()
            f.write("\t" + _)
            f.write("\n\n")
