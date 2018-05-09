import unittest
from twitter import Tweet, TwitterUser
from sortedcontainers import SortedList, SortedDict


test_text_0 = 'Telegram has recently shut down its highly-publicized Initial Coin Offering (ICO). While reasons are presently unclear, tightening regulations are likely a major cause. Others are claiming Telegram’s already raised the money they once wanted. https://www.bitsonline.com/telegram-cancels-ico/'

test_text_1 = "['https://github.com/codysoyland/surlex0', 'https://github.com/codysoyland/surlex1', 'https://github.com/codysoyland/surlex2', 'https://github.com/codysoyland/surlex3', 'https://github.com/codysoyland/surlex4', 'https://github.com/codysoyland/surlex5', 'https://github.com/codysoyland/surlex6', 'https://github.com/codysoyland/surlex7', 'https://github.com/codysoyland/surlex8', 'https://github.com/codysoyland/surlex9']"

test_text_2 = "['https://github.com/codysoyland/surlex0', 'https://github.com/codysoyland/surlex1', 'https://github.com/codysoyland/surlex2', 'https://github.com/codysoyland/surlex3', 'https://github.com/codysoyland/surlex4']"

test_text_3 = '''The new governor of South Korea’s Financial Supervisory Service, Yoon Suk-heun said FSS will consider easing cryptocurrency regulations. “The FSC inspects policies, while the FSS examines and supervises financial institutions but with the oversight of the FSC.”
#DailyFAS
https://coinjournal.net/s-korea-new-fss-governor-to-ease-cryptocurrency-regulation/'''

test_text_4 = '''The new governor of South Korea’s Financial Supervisory Service, The new governor of South Korea’s Financial Supervisory Service, The new governor of South Korea’s Financial Supervisory Service, The new governor of South Korea’s Financial Supervisory Service, The new governor of South Korea’s Financial Supervisory Service, Yoon Suk-heun said FSS will consider easing cryptocurrency regulations. “The FSC inspects policies, while the FSS examines and supervises financial institutions but with the oversight of the FSC.”
#DailyFAS
https://coinjournal.net/s-korea-new-fss-governor-to-ease-cryptocurrency-regulation/'''

t3 = Tweet(test_text_3)
# t4 = Tweet(test_text_4)


class TestTwitterUser(unittest.TestCase):

    def test_init(self):
        print('test0')
        self.user = TwitterUser()


class Test3(unittest.TestCase):

    def test_init(self):
        t = t3
        self.maxDiff = None
        print('test1')
        self.assertTrue(isinstance(t, Tweet))
        self.assertEqual(t.washed, 'The new governor of South Korea’s Financial Supervisory Service, Yoon Suk-heun said FSS will consider easing cryptocurrency regulations. “The FSC inspects policies, while the FSS examines and supervises financial institutions but with the oversight of the FSC.”\n#DailyFAS\nhttps://coinjournal.net/s-korea-new-fss-governor-to-ease-cryptocurrency-regulation/')
        print(t.tailored)

    def test_attrs(self):
        t = t3
        attrs = ['_raw', '_raw_chars', 'n_pages', 'nsp', 'offset', 'pool', 'raw_urls',
                 'raw_urls_chars', 'shortens', 'shortens_chars', 'tailored', 'washed', 'washed_chars']
        for attr in attrs:
            print('is {} in t.__dict__? {}'.format(
                attr, attr in t.__dict__))
            print('test2')
            self.assertIn(attr, t.__dict__)

    def test_pagination(self):
        print('test3')
        t = t3
        dividers = [n*280 for n in range(1, t.n_pages)]
        self.assertEqual(len(dividers), 1)
        self.assertEqual(dividers[0], 280)

        indices = SortedList(
            set(dividers + [key for key in t.offset.keys()]))
        self.assertEqual(indices, SortedList([0, 4, 8, 17, 20, 26, 34, 44, 56, 65, 70, 79, 84, 88, 93, 102, 109, 124,
                                              137, 142, 146, 155, 165, 171, 175, 179, 188, 192, 203, 213, 226, 230, 235, 239, 249, 252, 256, 262, 272, 280]))

        pages = SortedDict()
        for i in range(0, t.n_pages):
            # first page
            if i is 0:
                page = indices[0:indices.index(dividers[0])-1]
                self.assertEqual(page, [0, 4, 8, 17, 20, 26, 34, 44, 56, 65, 70, 79, 84, 88, 93, 102, 109, 124, 137,
                                        142, 146, 155, 165, 171, 175, 179, 188, 192, 203, 213, 226, 230, 235, 239, 249, 252, 256, 262])
            # last page
            elif i is t.n_pages - 1:
                page = indices[indices.index(dividers[i-1])-1:]
            else:
                page = indices[indices.index(
                    dividers[i-1]):indices.index(dividers[i])]
            pages[i] = page
        for key in pages:
            for item in pages[key]:
                if item not in t.offset:
                    pages[key].remove(item)
        self.assertNotEqual(len(pages), 0)

        t.pagination = SortedDict()
        for i in range(t.n_pages):
            temp_key_list = [key for key in pages[i]]
            page_pool = []
            for key in temp_key_list:
                page_pool.append(t.offset[key])
            t.pagination[i] = ' '.join(page_pool)

        self.assertIn('pagination', t.__dict__)
        for i in range(t.n_pages):
            self.assertLess(len(t.pagination[i]), 280)
