import os
import logging
from telegram import KeyboardButton,  ReplyKeyboardMarkup

from ru import RabonaUser


# init
logging.basicConfig(
    filename='log/bot.log',
    level=logging.INFO,
    format='%(asctime)s%(filename)s[line:%(lineno)d] %(levelname)s %(message)s')


start_keyboard = [['/当前账号', '/切换账号', '/查看草稿'], ['开始发推！']]
start_markup = ReplyKeyboardMarkup(start_keyboard, one_time_keyboard=False)
editing_keyboard = [[KeyboardButton('就发这些咯🐦'),
                     KeyboardButton('看看都弄了些啥👀')],
                    [KeyboardButton('清空草稿😱')],
                    [KeyboardButton("😄算了")]]
editing_markup = ReplyKeyboardMarkup(
    editing_keyboard, one_time_keyboard=True)


def stageHub(bot, update, arg='view', content=None):
    ruser = RabonaUser(update.effective_user)
    if 'staging' not in os.listdir(ruser.dir):
        with open(ruser.dir + 'staging', 'w'):
            logging.info(
                'no staging file in {}, just created one.'.format(ruser.dir))
        staging = ''
    else:
        with open(ruser.dir + 'staging', 'r') as f:
            staging = f.read()
    if arg == 'view':
        if staging:
            update.message.reply_text(staging, reply_markup=editing_markup)
        else:
            update.message.reply_text('啥也没啥，嘻嘻', reply_markup=start_markup)
    elif arg == 'read':
        return staging
    elif arg == 'write':
        with open(ruser.dir + 'staging', 'a') as f:
            f.write(content + '\n')
    else:
        query = update.callback_query
        print(query.data)
        if query.data == 'clear_staging_confirmed':
            clearStaging(bot, update)
        elif query.data == 'clear_staging_cancelled':
            query.message.delete()
            update.effective_user.send_message(
                text='继续编辑😁',
                reply_markup=start_markup,
            )
        else:
            pass


def clearStaging(bot, update, mode='clear_draft'):
    ruser = RabonaUser(update.effective_user)
    with open(ruser.dir + 'staging', 'w'):
        pass
    if mode == 'clear_draft':
        text = '草稿已清空嘻嘻'
    elif mode == 'after_post':
        text = '已经发送成功嘻嘻'
    update.effective_user.send_message(text=text, reply_markup=start_markup)
    logging.info('staging cleared.')
