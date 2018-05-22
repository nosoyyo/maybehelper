import os
import re
import jfw
import tweepy
import logging
import urlmarker
from math import fmod, floor
from datetime import datetime
from conf_mgmt import twitterConf
from sortedcontainers import SortedList, SortedDict
from errors import TooManyHyperLinks, UnauthorizedUser


def flatten(x): return [y for l in x for y in flatten(
    l)] if type(x) is list else [x]


# init
logging.basicConfig(
    filename='log/bot.log',
    level=logging.INFO,
    format='%(asctime)s%(filename)s[line:%(lineno)d] %(levelname)s %(message)s')


class TwitterUser():
    def __init__(self, username=None):
        if username:
            self.conf = self.getConfByName(username)
        else:
            self.conf = self.current()
        self._auth = tweepy.OAuthHandler(
            self.conf.consumer_key, self.conf.consumer_secret)
        self._auth.set_access_token(
            self.conf.access_token, self.conf.access_token_secret)
        self.api = tweepy.API(self._auth)

    def getConfByName(self, username):
        _users_dict = {'nosoyyo_oyyoson': 'dev', 'Faxport_EN': 'prod'}
        return twitterConf(_users_dict[username])

    def current(self):
        with open('tdev', 'r') as env:
            flag = env.read(1)
            if flag is '1':
                self.dev = True
                return twitterConf('dev')
            elif flag is '0':
                self.dev = False
                return twitterConf('prod')

    def switch(self):
        with open('tdev', 'r') as env:
            flag = env.read(1)
            if flag is '1':
                with open('tdev', 'w') as flag:
                    flag.write('0')
                return '推特切换到正式环境！谨慎操作😨'
            elif flag is '0':
                print('0')
                with open('tdev', 'w') as flag:
                    flag.write('1')
                return '推特切换到测试环境！随意操作🤓'

    def twit(self, tweet):
        try:
            if 'tailored' in tweet.__dict__.keys() and\
                    isinstance(tweet.tailored, SortedDict):
                return self.multiTwit(tweet)
            elif 'photo_file' in tweet.__dict__.keys():
                self.api.update_with_media(tweet.photo_file)
                # os.remove(tweet.photo_file)
                return self.conf.preview_url + self.api.me().status.id_str
            else:
                logging.info('与推特服务器通讯中...')
                self.api.update_status(tweet.tailored)
                return self.conf.preview_url + self.api.me().status.id_str
        except tweepy.error.TweepError as e:
            return e.reason

    def multiTwit(self, tweet):
        multi = tweet.tailored
        first = self.api.update_status(tweet.tailored[0]).id
        last = ''
        for n in range(1, len(multi)):
            if last:
                last = self.api.update_status(
                    tweet.tailored[n], last).id
            else:
                last = self.api.update_status(
                    tweet.tailored[n], first).id
        return self.conf.preview_url+str(first)

    def delete(self, tweet=None, link=None):
        if tweet:
            id_str = tweet.id_str
        elif link:
            id_str = str(link.split('/')[-1])
        else:
            return '😡😡😡没推删啥？？？'
        logging.debug('删除一条推特 {}...'.format(id_str))
        try:
            self.api.destroy_status(id_str)
            logging.info('成功删除 {}...'.format(id_str))
            return '{} succesfully deleted.'.format(id_str)
        except tweepy.error.TweepError as e:
            return e.reason

    def savePhoto(self, bot, photo_file_obj):
        '''
            when called by bot.photo, will pass a `dir` with this
            TwitterUser obj as TwitterUser.dir
        '''
        suffix = photo_file_obj.file_path.split('.')[-1]
        filename = self.dir + datetime.now().__str__().replace(':', '-') + '.' + suffix
        photo_file_obj.download(filename)
        return filename


class Tweet():
    def __init__(self, text=None):
        if self.isstatusurl(text):
            self.__dict__ = TwitterUser().api.get_status(
                text.split('/')[-1]).__dict__
        elif isinstance(text, str) and os.path.isfile(text):
            self.photo_file = text
        elif not text:
            print('想好发啥再戳我😡😡😡')
        else:
            self._raw = text
            self._raw_chars = len(self._raw)
            self.wash()
            self.divide()
            self.pool()

            urls = self.extractURL(self._raw)
            if urls:
                if len(urls) > 5:
                    raise TooManyHyperLinks
                else:
                    self.raw_urls = urls
                    logging.info('计算原文中 url 个数和字符数...')
                    self.raw_urls_chars = sum(
                        [len(url) for url in self.raw_urls])
                    logging.info('原文中{}个 url，共{}个字符'.format(
                        len(urls), self.raw_urls_chars))
                    logging.info('正在生成短链接...')
                    self.shorten()
                    logging.info('短链接搞定')
                    self.shortens_chars = sum(
                        [len(url) for url in self.shortens])
                    self.buildOffset()

            self.tailor()

    @classmethod
    def extractURL(self, text):
        return re.findall(urlmarker.WEB_URL_REGEX, text)

    @classmethod
    def isurl(self, text):
        url = self.extractURL(text)
        if len(url) != 1 or len(set([text] + url)) != 1:
            return False
        else:
            return True

    @classmethod
    def isstatusurl(self, text):
        if self.isurl(text):
            if 'twitter.com' in text and 'status' in text:
                return True
            else:
                return False
        else:
            return False

    def wash(self):
        '''
            remove newlines and more than one spaces
        '''
        text = self._raw
        workspace = []
        for i in range(1, len(text)):
            if not text[i-1].isspace():
                workspace.append(text[i-1])
            elif not text[i].isspace():
                workspace.append(text[i-1])
        text.replace('', ' ')
        if not text[-1].isspace():
            self.washed = ''.join(workspace) + text[-1]
        else:
            self.washed = ''.join(workspace)
        self.washed_chars = len(self.washed)

    def shorten(self):
        try:
            logging.debug('切换到开发账号...')
            dev_user = TwitterUser()
            logging.debug('开发账号切换成功，username: ' + dev_user.conf.username)
            logging.debug('生成中间 tweet...')
            middle_tweet = dev_user.api.update_status(self.raw_urls)
            logging.debug('获取短链...')
            self.shortens = [url['url']
                             for url in middle_tweet.entities['urls']]
            logging.debug('一切正常，删除中间 tweet...')
            middle_tweet.destroy()
            logging.debug('中间 tweet 已被删除...')
        except Exception as e:
            print('something wrong with shorten(), ' + e)

    def divide(self):
        if fmod(self.washed_chars, 280) != 0:
            self.n_pages = floor(self.washed_chars / 280) + 1
        else:
            self.n_pages = floor(self.washed_chars / 280)

    def pool(self):
        # newline separated parts
        self.nsp = [item for item in self.washed.split(
            '\n') if item is not None]
        self.pool = flatten([item.split(' ')
                             for item in self.nsp if item is not None])

    def buildOffset(self):
        self.offset = SortedDict({0: self.pool[0]})
        for i in range(1, len(self.pool)):
            self.offset.__setitem__(
                self.offset.keys()[i-1] + len(self.pool[i-1]) + 1, self.pool[i])

    def buildPages(self):
        dividers = [n*280 for n in range(1, self.n_pages)]
        indices = SortedList(
            set(dividers + [key for key in self.offset.keys()]))
        pages = SortedDict()
        for i in range(0, self.n_pages):
            # first page
            if i is 0:
                page = indices[0:indices.index(dividers[0])-1]
            # last page
            elif i is self.n_pages - 1:
                page = indices[indices.index(dividers[i-1])-1:]
            else:
                page = indices[indices.index(
                    dividers[i-1]):indices.index(dividers[i])]
            pages[i] = page

        # remove dividers that hasn't been existed
        for key in pages:
            for item in pages[key]:
                if item not in self.offset:
                    pages[key].remove(item)

        self.pagination = SortedDict()
        for i in range(self.n_pages):
            temp_key_list = [key for key in pages[i]]
            page_pool = []
            for key in temp_key_list:
                page_pool.append(self.offset[key])
            self.pagination[i] = ' '.join(page_pool)

    def tailor(self):
        # deal with urls
        if self.washed_chars > 280:
            # when text contains urls
            if not self.raw_urls:
                self.buildPages()
                self.tailored = self.pagination
            else:
                # when length still over 280
                if (self.washed_chars - self.raw_urls_chars) + self.shortens_chars > 280:
                    self.buildPages()
                    self.tailored = self.pagination
                else:
                    self.tailored = self.washed
        # simple case
        else:
            self.tailored = self.washed
