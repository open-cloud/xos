import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import sys


class XosUI(unittest.TestCase):
    """Test cases for XOS"""

    url = 'http://127.0.0.1:8000/'

    def setUp(self):
        if(hasattr(self, 'browser') and self.browser == 'firefox'):
            self.driver = webdriver.Firefox()
        elif(hasattr(self, 'browser') and self.browser == 'chrome'):
            self.driver = webdriver.Chrome()
        else:
            self.driver = webdriver.PhantomJS()

        self.driver.set_window_size(1120, 550)
        self.driver.get(self.url)

    def tearDown(self):
        self.driver.close()
        self.driver.quit()

    def doLogin(self):
        username = self.driver.find_element_by_css_selector('#id_username')
        password = self.driver.find_element_by_css_selector('#id_password')
        sign_in = self.driver.find_element_by_css_selector('.btn.btn-primary')

        username.send_keys('padmin@vicci.org')
        password.send_keys('letmein')
        sign_in.click()

    def test_login_page(self):
        """
        Test that the login page has the login form
        """

        login_container = self.driver.find_element_by_css_selector('body.login #content-main')
        assert login_container
        username = login_container.find_element_by_css_selector('#id_username')
        password = login_container.find_element_by_css_selector('#id_password')
        sign_in = login_container.find_element_by_css_selector('.btn.btn-primary')
        assert username
        assert password
        assert sign_in

    def test_login_function(self):
        """
        Test that login is working
        """
        self.doLogin()

        # if we have a sidebar the login has worked
        sidebar = self.driver.find_element_by_css_selector('#sidebar-wrapper')
        assert sidebar


if __name__ == "__main__":
    if len(sys.argv) > 1:
        XosUI.browser = sys.argv[1]
        if(sys.argv[2]):
            XosUI.url = sys.argv[2]
            del sys.argv[2]
        del sys.argv[1]
    unittest.main()
