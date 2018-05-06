#!/Users/daguo/miniconda3/bin/python3.6
# -*- coding: utf-8 -*-
__author__ = 'nosoyyo'
"""
Simple Bot to handle some SNS integrations.
This program is dedicated to the public domain under the CC0 license.
"""
# local debugging
import jfw

import telegram
from telegram.error import NetworkError, Unauthorized
from time import sleep
import logging

from conf_mgmt import botConf
# banned!!
# from btct import Thread, now, getLimit
from twitter import TwitterUser, Tweet, TooManyHyperLinks
from fb import FBUser, FBContent


# init
logging.basicConfig(
    filename='log/telebot.log',
    level=logging.INFO,
    format='%(asctime)s%(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
logging.info('session started.')


update_id = None


# general - welcome, start, help, who
def send(bot, update, text):
    bot.send_message(chat_id=update.message.chat_id, text=text)


def start(bot, update):
    lines = """                 🤓欢迎光临🤓\r
                可用命令：
                /start 显示本信息&常用命令
                /help 查看全部命令
                /who 显示当前登录账号

                🐦🐦🐦twitter🐦🐦🐦
                /st 切换 twitter 测试/正式环境"
                /twit <文字内容> 把 <文字内容> 发布到推特，命令后面接一个空格！
                /del <推特链接1> <推特链接2>... 删除一条或多条推特（❕无确认步骤，谨慎❕）

                📘📘📘facebook📘📘📘
                /sf 切换 facebook 测试/正式环境"
                /pf <文字内容> 把 <文字内容> 发布到脸书，命令后面接一个空格！
            """
    send(bot, update, lines)


def help(bot, update):
    text = "除了 bitcointalk.org 发布不了，别的都能干😂"
    send(bot, update, text)


def who():
    tuser = TwitterUser()
    tu, thome = tuser.conf.username, tuser.conf.home_url
    report = '''
                推特
                账号：{}
                测试地址：{}

                脸书：
                账号：{}
                测试地址：{}
            '''.format(tu, thome, None, None)
    return report


def twit(content):
    user = TwitterUser()
    try:
        tweet = Tweet(content)
        logging.info('twitting {} ...'.format(tweet.tailored))
        result = user.twit(tweet)
        return result
    except TooManyHyperLinks:
        return TooManyHyperLinks.msg


def delete(content):
    urls = Tweet.extractURL(content)
    if not urls:
        return '仅支持贴链接删除哦😯'
    else:
        for url in urls:
            username = content.split('/')[-3]
            user = TwitterUser(username)
            return user.delete(link=content)


def publishFB(content):
    user = FBUser()
    content = FBContent(content)
    logging.info('sending {} ...'.format(content.tailored))
    try:
        result = user.post(content)
        return result
    except Exception:
        logging.info('sending {} ...'.format(content.tailored))
    return 'todo'


'''
# bitcointalk.org
# banned
def which(bot, update, _id=thread_id):
    bot.send_message(chat_id=update.message.chat_id, text='稍等几秒...')
    nw = now()
    tl = getLimit()
    title = Thread(_id).title
    text = "\n 内容将发布到\n‘{}’".format(title)
    if nw - tl < 360:
        cd = '还有 {} 秒才能发布，等会儿吧😏'.format(360 - (nw - tl))
        bot.send_message(chat_id=update.message.chat_id, text=text + '\n' + cd)
    else:
        bot.send_message(chat_id=update.message.chat_id, text=text)

# banned
def doTheJob(content, _id=thread_id):
    thread = Thread(_id)
    result = thread.post(content)
    return result
'''


def main():
    """Run the bot."""
    global update_id
    # Telegram Bot Authorization Token
    bot = telegram.Bot(botConf('dev').TOKEN)

    # get the first pending update_id, this is so we can skip over it in case
    # we get an "Unauthorized" exception.
    try:
        update_id = bot.get_updates()[0].update_id
    except IndexError:
        update_id = None

    while True:
        try:
            handle(bot)
        except NetworkError:
            sleep(1)
        except Unauthorized:
            # The user has removed or blocked the bot.
            update_id += 1


def handle(bot):
    """Echo the message the user sent."""
    global update_id
    # Request updates after the last update_id
    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1

        if update.message:  # your bot can receive updates without messages
            if update.message.text == '/start':
                start(bot, update)
            elif update.message.text == '/help':
                help(bot, update)
            elif update.message.text == '/who':
                update.message.reply_text(who())

            elif update.message.text == '/st':
                tuser = TwitterUser()
                result = tuser.switch()
                send(bot, update, result)
            elif update.message.text == '/sf':
                fbuser = FBUser()
                result = fbuser.switch()
                send(bot, update, result)

            elif update.message.text.startswith('/twit'):
                content = update.message.text[6:]
                update.message.reply_text(twit(content))
            elif update.message.text.startswith('/del'):
                content = update.message.text[5:]
                update.message.reply_text(delete(content))

            # TODO
            elif update.message.text.startswith('/pf'):
                content = update.message.text[4:]
                update.message.reply_text(publishFB(content))
            else:
                update.message.reply_text('你输入了：' + update.message.text)


if __name__ == '__main__':
    main()
