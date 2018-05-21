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
clear_draft_kb = [['确定清空❕', '😄算了']]
clear_draft_markup = ReplyKeyboardMarkup(clear_draft_kb, ne_time_keyboard=True)


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
        logging.info('unknown case occured in stageHub.')


def clearStaging(bot, update, mode='clear_draft'):
    ruser = RabonaUser(update.effective_user)
    if mode == 'clear_draft':
        with open(ruser.dir + 'staging', 'w'):
            pass
        text = '草稿已清空嘻嘻'
    elif mode == 'after_post':
        with open(ruser.dir + 'staging', 'w'):
            pass
        text = '已经发送成功嘻嘻'
    elif mode == 'need_confirmation':
        update.effective_user.send_message(
            '未发布的推特将彻底消失😱\n确定❓', reply_markup=clear_draft_markup)
    update.effective_user.send_message(text=text, reply_markup=start_markup)
    logging.info('staging cleared.')
