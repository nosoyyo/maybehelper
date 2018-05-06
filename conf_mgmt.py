from config import Telegram_Bot_TOKEN, Telegram_DevBot_TOKEN, DevConf, ProdConf


# telegram
class botConf():
    def __init__(self, env):

        if env is 'dev':
            self.TOKEN = Telegram_DevBot_TOKEN
        else:
            self.TOKEN = Telegram_Bot_TOKEN


# twitter
class twitterConf():
    '''
        init
    '''

    def __init__(self, env='prod'):
        self.site = 'https://twitter.com/'
        if env is 'dev':
            self.dev = True
            self.username = DevConf.username
            self.screen_name = DevConf.screen_name
            self.consumer_key = DevConf.consumer_key
            self.consumer_secret = DevConf.consumer_secret
            self.access_token = DevConf.access_token
            self.access_token_secret = DevConf.access_token_secret
            self.home_url = self.site + self.screen_name
            self.preview_url = self.home_url + '/status/'
        elif env is 'prod':
            self.dev = False
            self.username = ProdConf.username
            self.screen_name = ProdConf.screen_name
            self.consumer_key = ProdConf.consumer_key
            self.consumer_secret = ProdConf.consumer_secret
            self.access_token = ProdConf.access_token
            self.access_token_secret = ProdConf.access_token_secret
            self.home_url = self.site + self.screen_name
            self.preview_url = self.home_url + '/status/'
        else:
            return 'something wrong with twitterConf initialization.'


# facebook
class fbConf():
    '''
        Prod/Dev switch here.
    '''

    def __init__(self):
        site = ''
        home_url = ''
        username = 'nosoyyo'
        preview_url = ''
