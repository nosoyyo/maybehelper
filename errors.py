import logging


class TooManyHyperLinks(Exception):
    def __init__(self, n_links):
        logging.error('😤最多只让发 5 个链接啦推特！你发了{}个😤'.format(n_links))


class UnauthorizedUser(Exception):
    def __init__(self, tele_id):
        logging.error('user {} not allowed'.format(tele_id))
