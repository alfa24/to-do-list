import time


class MyListsPage(object):

    def __init__(self, test):
        self.test = test

    def go_to_my_lists_page(self):
        """перейти на мою страницу списков"""

        self.test.browser.get(self.test.live_server_url)
        self.test.browser.find_element_by_link_text('Мои списки').click()
        self.test.wait_for(lambda: self.test.assertEqual(
            self.test.browser.find_element_by_tag_name('h1').text,
            'Мои списки'
        ))
        time.sleep(10)
        return self
