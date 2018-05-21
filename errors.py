class TooManyHyperLinks(Exception):
    def __init__(self, n_links):
        self.msg = '😤最多只让发 5 个链接啦推特！你发了{}个😤'.format(n_links)
