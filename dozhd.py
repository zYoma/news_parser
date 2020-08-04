from bs4 import BeautifulSoup
import re


def dozhd(html):
    links = {}
    imge = {}
    soup = BeautifulSoup(html, 'lxml')
    t=soup.find_all('div', class_ = 'newsline_tile__el')
    count = 0
    for i in t:
        if count < 10:
            a = i.find('a').get('href')
            domain = 'https://tvrain.ru'
            a = domain + a
            text = i.find('h3').find('a').text

            try:
                img = i.find('img').get('data-image')
                https = 'https:'
                img = https + img
            except:
                img = 'None'
            links[a]= text
            imge[a] = img
        count = count +1
        
    return links, imge
