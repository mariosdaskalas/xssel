import requests
import re
import urllib.parse as urlparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Version 126.0.6478.114 (Official Build) (64-bit)
# https://storage.googleapis.com/chrome-for-testing-public/126.0.6478.62/linux64/chromedriver-linux64.zip

service = Service('/usr/local/bin/chromedriver')
options = webdriver.ChromeOptions()
options.add_argument('window-size=1920,1080')
options.add_argument('--headless')
driver = webdriver.Chrome(service=service, options=options)

url = "http://localhost:8090"

# Login Area [bWAPP]
driver.get(f'{url}/login.php')
username = driver.find_element(By.XPATH, "//input[@type='text']")
username.send_keys("admin")
password = driver.find_element(By.NAME, "password")
password.send_keys("letmein" + Keys.ENTER)


class Scanning:
    def __init__(self, url, ignored):
        self.targeting_url = url
        self.targeting_link = []
        self.session = requests.Session()
        self.count = 0
        self.ignored = ignored

    def extracting_link(self, url):
        response = self.session.get(url)
        return re.findall('(?:href=")(.*?)"', response.content.decode(errors="ignore"))

    def exploit_link(self):
        select_values = []

        for element in driver.find_elements(By.TAG_NAME, "option"):
            select_option = element.get_attribute("value")
            select_values.append(select_option)

        select_values = sorted(set(select_values), key=select_values.index)

        for i in select_values:
            select_element = driver.find_element(By.XPATH, f"//option[@value='{i}']")
            select_element.click()
            submit_button = driver.find_element(By.NAME, "form")
            submit_button.click()
            curr_link = driver.current_url
            print(curr_link)
            driver.get(f"{url}/portal.php")

    def crawling(self, url):

        links = self.extracting_link(url)
        for link in links:
            link = urlparse.urljoin(url, link)

            if "#" in link:
                link = link.split("#")[0]

            if self.targeting_url in link and link not in self.targeting_link and link not in self.ignored:
                self.targeting_link.append(link)
                self.count = self.count + 1
                response_req = requests.get(link)
                soup = BeautifulSoup(response_req.text, 'html.parser')
                form = soup.find('form')  # Find the first form element
                self.crawling(link)

    def forming(self, url):
        response = self.session.get(url)
        parsing_html = BeautifulSoup(response.content, features="html.parser")
        return parsing_html.findAll("form")

    def running(self):
        for link in self.targeting_link:
            forms = self.forming(link)