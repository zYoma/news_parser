#!/usr/bin/env python3
# pip install beautifulsoup4
# pip install lxml
from bs4 import BeautifulSoup
# pip install flask
from flask import Flask
# pip install Flask-SSLify
from flask_sslify import SSLify
from flask import request
from flask import jsonify
from dozhd import dozhd
from yandex_pr import check_status
from dotenv import load_dotenv
#from pars import Bot
from sub import *
import requests
import json
import re
import logging
import os
import sys
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
IP = os.getenv("IP")

last_links = {}
URL = 'https://api.telegram.org/bot'+ TELEGRAM_TOKEN + '/'


def write_json(data, filename='answer.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def send_Message(chat_id, text, blog_url):
    url = URL + 'sendMessage'
    kb_markup = {'inline_keyboard': [
        [{'text': 'Читать дальше', 'url': blog_url, 'callback_data': 'var1'}]]}
    answer = {'chat_id': chat_id, 'text': text,
              'reply_markup': kb_markup, 'parse_mode': 'Markdown'}
    r = requests.post(url, json=answer)
    return r.json()


def send_Photo(chat_id, text, img, blog_url):
    url = URL + 'sendPhoto'
    kb_markup = {'inline_keyboard': [
        [{'text': 'Читать дальше', 'url': blog_url, 'callback_data': 'blog_url'}]]}
    answer = {'chat_id': chat_id, 'caption': text, 'photo': img,
              'reply_markup': kb_markup, 'parse_mode': 'Markdown'}
    r = requests.post(url, json=answer)
    return r.json()


def send_Message_Keybord(chat_id, text='BlaBla'):
    url = URL + 'sendMessage'
    kb_markup = {'resize_keyboard': True, 'keyboard': [
        [{'text': 'Игры'}, {'text': 'Новости'}], [{'text': 'дождь'}, {'text': 'ya'}]]}
    answer = {'chat_id': chat_id, 'text': text,
              'reply_markup': kb_markup, 'parse_mode': 'Markdown'}
    r = requests.post(url, json=answer)
    return r.json()


def editMessage(chat_id, text, message_id):
    url = URL + 'editMessageText'
    answer = {'chat_id': chat_id, 'text': text,
              'message_id': message_id, 'parse_mode': 'Markdown'}
    r = requests.post(url, json=answer)
    return r.json()


def editMessageCaption(chat_id, text, message_id):
    url = URL + 'editMessageCaption'
    answer = {'chat_id': chat_id, 'caption': text,
              'message_id': message_id, 'parse_mode': 'Markdown'}
    r = requests.post(url, json=answer)
    return r.json()


def get_html(url):
    r = requests.get(url, verify=False)
    return r.text


def lenta(html):
    lenta = {}
    soup = BeautifulSoup(html, 'lxml')
    glavnoe = soup.find('h2').find('a').text.strip()
    glav_url = soup.find('h2').find('a').get('href')
    glav_url = 'https://lenta.ru' + glav_url
    glavnoe = re.sub(r'^\d{2}:\d{2}', '', glavnoe)
    glavnoe = '*{}*\n'.format(glavnoe)
    news = soup.find(
        'section', class_='b-top7-for-main').find_all('div', class_='item')
    for i in news:
        a = i.find('a').get('href')
        a = 'https://lenta.ru' + a
        text = i.find('a').text.strip()
        text = re.sub(r'^\d{2}:\d{2}', '', text)
        text = '`{}`'.format(text)
        lenta[text] = a
    news = None
    return lenta, glavnoe, glav_url


def igromania(html):
    soup = BeautifulSoup(html, 'lxml')
    news = soup.find('div', id='uni_com_feed_cont').find_all(
        'div', class_='aubl_item')[:10]
    list = []
    for n in news:
        try:
            title = n.find('div', class_='aubli_data').find('a').text.strip()
        except:
            title = ''
        try:
            url = 'https://www.igromania.ru' + \
                n.find('div', class_='aubli_data').find('a').get('href')
        except:
            url = ''
        try:
            img = n.find('img').get('src')
        except:
            img = ''
        local_list = [title, url, img]
        list.append(local_list)

    return list


app = Flask(__name__)
sslify = SSLify(app)


@app.route(f'/{TELEGRAM_TOKEN}/', methods=['POST', 'GET'])
def index():
    global last_links
    if request.method == 'POST':
        r = request.get_json()
        if 'callback_query' in r:
            callback_data = r['callback_query']['data']
            callback_from_chat_id = r['callback_query'][
                'message']['chat']['id']
            callback_message_id = r['callback_query']['message']['message_id']
            chat_id = callback_from_chat_id
            message_id = callback_message_id
            first_name = r['callback_query']['from']['first_name']
            caption = r['callback_query']['message']['caption']
        else:
            chat_id = r['message']['chat']['id']
            first_name = r['message']['from']['first_name']
            message = r['message'].get('text')
            if message:

                if re.search(r'Игры', message):
                    game_list = []
                    game_list = igromania(
                        get_html(url='https://www.igromania.ru/news/'))
                    for news in game_list:
                        send_Photo(chat_id, news[0], news[2], news[1])
                        time.sleep(2)

                if re.search(r'ya', message):
                    status = check_status()
                    send_Message_Keybord(chat_id, status)
                elif re.search(r'Новости', message):
                    news, glavnoe, glav_url = lenta(
                        get_html(url='https://lenta.ru/'))
                    for key in news:
                        send_Message(chat_id, key, news[key])
                    send_Message(chat_id, glavnoe, glav_url)
                    news = {}
                    glavnoe = None
                    glav_url = None

                elif re.search(r'дождь', message):
                    links_dozhd, img_dozhd = dozhd(
                        get_html(url='https://tvrain.ru/news/'))

                    for key in links_dozhd:

                        if img_dozhd[key] == 'None':
                            send_Message(chat_id, links_dozhd[key], key)
                        else:
                            send_Photo(chat_id, links_dozhd[
                                       key], img_dozhd[key], key)

                        time.sleep(2)
                    links_dozhd = {}
                    img_dozhd = {}

                elif re.search(r'df', message):

                    result_df = df_h()
                    send_Message_Keybord(chat_id, result_df)

                elif re.search(r'top', message):

                    result_df = top()
                    send_Message_Keybord(chat_id, result_df)

                elif re.search(r'ban', message):

                    result_df = ban()
                    send_Message_Keybord(chat_id, result_df)

                else:
                    text = "`Привет, {}! Я только и умею, что отвечать данным сообщением.`".format(
                        first_name)
                    send_Message_Keybord(chat_id, text)

        write_json(r)
        return jsonify(r)
    return '<h1>Test Flask</h1>'


if __name__ == '__main__':
    app.run(host=IP, port=8443, debug=True,
            ssl_context=('webhook_cert.pem', 'webhook_pkey.pem'))
