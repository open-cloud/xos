import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time


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

        self.driver.set_window_size(1920, 1280)
        self.driver.get(self.url)

    def tearDown(self):
        self.driver.quit()
        # self.driver.close()

    def doLogin(self):
        username = self.driver.find_element_by_css_selector('#id_username')
        password = self.driver.find_element_by_css_selector('#id_password')
        sign_in = self.driver.find_element_by_css_selector('.btn.btn-primary')

        username.send_keys('padmin@vicci.org')
        password.send_keys('letmein')
        sign_in.click()

    def goToPage(self, page):
        self.driver.get(self.url + '/admin/core/' + page)

    def listPageAssertion(self, page):
        self.doLogin()
        self.goToPage(page)
        title = self.driver.find_element_by_css_selector('#content > h2').text
        assert (title == 'Select %s to change' % page), 'Title is wrong!'

        add_button = self.driver.find_element_by_css_selector('.addlink.btn.btn-success')
        assert add_button

        table = self.driver.find_element_by_css_selector('table')
        rows = table.find_elements_by_css_selector('tbody tr')
        assert (len(rows) == 1), 'Elements are not printed in table!'

    def detailPageAssertion(self, page, expectedTabs):
        self.doLogin()
        self.goToPage(page)
        try:
            detail_link = self.driver.find_element_by_css_selector('table tbody tr td > a')
        except:
            # the user template is different, it has just one th (with the link) in the table,
            # not sure why or how to fix it
            detail_link = self.driver.find_element_by_css_selector('table tbody tr th > a')
        detail_link.click()

        title = self.driver.find_element_by_css_selector('#content > h2').text
        assert (title == 'Change %s' % page), 'Expected "%s" to be "%s"!' % (title, 'Change %s' % page)

        tabs = self.driver.find_elements_by_css_selector('#suit_form_tabs > li')
        assert (len(tabs) == expectedTabs), 'Found %s of %s expected tabs' % (len(tabs), expectedTabs)

        activeTab = self.driver.find_element_by_css_selector('#suit_form_tabs > li.active')
        assert (activeTab), 'No tab is active!'

        saveBtn = self.driver.find_element_by_css_selector('.btn.btn-success')
        assert saveBtn, 'Save button is missing'

        continueBtn = self.driver.find_element_by_css_selector('[name="_continue"]')
        assert continueBtn, 'Save and continue button is missing'

        addanotherBtn = self.driver.find_element_by_css_selector('[name="_addanother"]')
        assert addanotherBtn, 'Save and continue button is missing'

        deleteBtn = self.driver.find_element_by_css_selector('.btn.btn-danger')
        assert deleteBtn, 'Delete button is missing'

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

    def test_deployment_list(self):
        self.listPageAssertion('deployment')

    def test_deployment_detail(self):
        self.detailPageAssertion('deployment', 3)

    def test_site_list(self):
        self.listPageAssertion('site')

    def test_site_detail(self):
        self.detailPageAssertion('site', 6)

    def test_slice_list(self):
        self.listPageAssertion('slice')

    def test_slice_detail(self):
        self.detailPageAssertion('slice', 6)

    def test_user_list(self):
        self.listPageAssertion('user')

    def test_user_detail(self):
        self.detailPageAssertion('user', 5)

    def test_service_list(self):
        self.doLogin()
        self.driver.get(self.url + '/serviceGrid/')
        element = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'xos-table table'))
        )
        serviceGrid = self.driver.find_element_by_css_selector('service-grid')
        assert serviceGrid, "Service Grid not found"

        serviceList = serviceGrid.find_elements_by_css_selector('tbody')
        services = serviceList[1].find_elements_by_css_selector('tr')
        assert (len(services) == 4), 'Found %s of %s expected tabs' % (len(services), 4)

        addBtn = self.driver.find_element_by_css_selector('.btn.btn-success')
        assert addBtn, 'Add button is missing'

if __name__ == "__main__":
    if len(sys.argv) > 1:
        XosUI.browser = sys.argv[1]
        if(sys.argv[2]):
            XosUI.url = sys.argv[2]
            del sys.argv[2]
        del sys.argv[1]
    unittest.main()
