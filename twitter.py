import re
import jfw
import tweepy
import logging
import urlmarker
from math import fmod, floor
from conf_mgmt import twitterConf
from errors import TooManyHyperLinks
from sortedcontainers import SortedList, SortedDict


# init
logging.basicConfig(
    filename='log/telebot_twitter.log',
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
            if 'tailored' in tweet.__dict__.keys():
                self.api.update_status(tweet.tailored)
                logging.info('与推特服务器通讯中...')
                return self.conf.preview_url + self.api.me().status.id_str
            else:
                return '[debug]原文未成功裁剪，一般是超了字数'
        except tweepy.error.TweepError as e:
            return e.reason

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


class Tweet():
    def __init__(self, text=None, _id=None):
        if _id:
            return TwitterUser().api.get_status(str(_id))
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
    def isURL(self, text):
        url = self.extractURL(text)
        if len(url) != 1 or len(set([text] + url)) != 1:
            return False
        else:
            return True

    def wash(self):
        '''
            remove newlines and more than one spaces
        '''
        text = self._raw.replace('\n', ' ')
        workspace = []
        for i in range(1, len(text)):
            if not text[i-1].isspace():
                workspace.append(text[i-1])
            elif not text[i].isspace():
                workspace.append(text[i-1])
        self.washed = ''.join(workspace) + text[-1]
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
            self.n_tweets = floor(self.washed_chars / 280) + 1
        else:
            self.n_tweets = floor(self.washed_chars / 280)

    def pool(self):
        self.pool = [item for item in self.washed.split(
            ' ') if item is not None]

    def buildOffset(self):
        self.offset = SortedDict({0: self.pool[0]})
        for i in range(1, len(self.pool)):
            self.offset.__setitem__(
                self.offset.keys()[i-1] + len(self.pool[i-1]) + 1, self.pool[i])

    def buildTweets(self):
        paging = [n*280 for n in range(1, self.n_tweets)]
        indices = sorted(paging + [int(key) for key in self.offset.keys()])
        dividers = []
        for page in paging:
            divider = indices[indices.index(page)-1]
            dividers.append(divider)

        # TODO:assembling
        tweets = {}
        for n, m in range(1, self.n_tweets), range(0, len(dividers)):
            tweets[str(n)] = ' '.join()
        return tweets

    def tailor(self):
        # deal with urls
        if self.washed_chars > 280:
            # when text contains urls
            if not self.raw_urls:
                # TODO start multi-tweet buildling process here
                return '😤想发{}字？等多条功能上线再说啦😤'.format(self.washed_chars)
            else:
                # when length still over 280
                if (self.washed_chars - self.raw_urls_chars) + self.shortens_chars > 280:
                    if len(self.shortens) is 1:
                        return '😤除了链接只能发 257 字符(128 汉字)哦😤'
                    else:
                        return '😤除了这{}个链接就还能发{}字了，你裁剪一下好吧😤'.format(len(self.shortens), 280 - len(self.shortens)*23)
                else:
                    self.tailored = self.washed

        # simple case
        else:
            self.tailored = self.washed
