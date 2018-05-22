#!/Users/daguo/miniconda3/bin/python3.6
# -*- coding: utf-8 -*-
__author__ = 'nosoyyo'
"""
Simple twitter bot.
"""
# local debugging
import jfw

import os
import psutil
import logging
from telegram.ext import (Updater, CommandHandler,
                          MessageHandler, Filters, CallbackQueryHandler)

from ru import RabonaUser
from conf_mgmt import botConf
from stagehub import stageHub, clearStaging, start_markup, editing_markup
from twitter import TwitterUser, Tweet, TooManyHyperLinks

# init
logging.basicConfig(
    filename='log/bot.log',
    level=logging.INFO,
    format='%(asctime)s%(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
logging.info('session started.')


def start(bot, update):
    ruser = RabonaUser(update.effective_user)
    lines = ''' Hi {}!
                这里是 maybehelper v0.4
                文字、图片，想发啥发啥，想怎么发怎么发😉
            '''.format(ruser.title)
    update.effective_user.send_message(lines, reply_markup=start_markup)


def whoami(bot, update):
    user = TwitterUser(update=update)
    tu, thome = user.conf.username, user.conf.home_url
    report = '''
                账号：{}
                测试地址：{}
            '''.format(tu, thome)
    update.message.reply_text(
        text=report,
        reply_markup=start_markup,
    )


def switch(bot, update):
    user = TwitterUser(update=update)
    result = user.switch()
    update.message.reply_text(
        text=result,
        reply_markup=start_markup,
    )


def handler(bot, update):
    if update.message.document:
        if update.message.document.mime_type.split('/')[0] == 'image':
            result = photo(bot, update)
            update.message.reply_text(result, reply_markup=start_markup)
    elif update.message.photo:
        result = photo(bot, update)
        update.message.reply_text(result, reply_markup=start_markup)
    else:
        text = update.message.text
        staging = stageHub(bot, update, 'read')

        if text == '就发这些咯🐦':
            result = twit(bot, update, staging)
            update.message.reply_text(result, reply_markup=start_markup)
        elif text == '开始发推！':
            update.message.reply_text('随便输入', reply_markup=editing_markup)
        elif text == "😄算了":
            start(bot, update)
        elif text == "看看都弄了些啥👀":
            stageHub(bot, update, 'view')
        elif text == '清空草稿😱':
            clearStaging(bot, update, mode='need_confirmation')
        elif text == '确定清空❕':
            clearStaging(bot, update, mode='clear_draft')
        else:
            if text:
                stageHub(bot, update, 'write', text)
                update.message.reply_text(
                    '收到 ' + text, reply_markup=editing_markup)


def twit(bot, update, content):
    user = TwitterUser(update=update)
    try:
        tweet = Tweet(content)
        logging.info('twitting {} ...'.format(tweet._raw))
        result = user.twit(tweet)
        logging.info('post success, now clearing staging')
        if result:
            clearStaging(bot, update, mode='after_post')
            return result
    except TooManyHyperLinks:
        return TooManyHyperLinks.msg


def photo(bot, update):
    ruser = RabonaUser(update.effective_user)
    user = TwitterUser(update=update)
    user.dir = ruser.dir
    photo_file_obj = bot.get_file(update.message.document.file_id)
    local_file_name = user.savePhoto(bot, photo_file_obj)
    try:
        update.message.reply_text('嚯，要发图片喔😯')
        tweet = Tweet(local_file_name)
        logging.info('twitting photo ...')
        update.message.reply_text('在发了喔😯')
        result = user.twit(tweet)
        update.message.reply_text('发好了喔😯')
        os.remove(local_file_name)
        return result
    except Exception as e:
        print(e)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logging.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(botConf('btct').TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('当前账号', whoami))
    dp.add_handler(CommandHandler('查看草稿', stageHub))
    dp.add_handler(CommandHandler('切换账号', switch))
    dp.add_handler(CallbackQueryHandler(stageHub))
    dp.add_handler(CommandHandler('开始发推！', handler))
    dp.add_handler(MessageHandler((Filters.text | Filters.photo | Filters.document),
                                  handler))
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    # supervisoring process by pid
    p = psutil.Process()
    with open('pid', 'w') as pidfile:
        pidfile.write(str(p.pid))

    main()
