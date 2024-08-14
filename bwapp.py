import threading
import re
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException, NoSuchElementException, \
    NoAlertPresentException

# Version 126.0.6478.114 (Official Build) (64-bit)
# https://storage.googleapis.com/chrome-for-testing-public/126.0.6478.62/linux64/chromedriver-linux64.zip

service = Service('/usr/local/bin/chromedriver')
options = webdriver.ChromeOptions()
options.add_argument('window-size=1920,1080')
options.add_argument('--headless')
driver = webdriver.Chrome(service=service, options=options)

# http://localhost:8090
while True:
    url = input("Please give the url of bWAPP:\n")
    if re.match(r"^(http|https)://(?:localhost|(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))\S*$", url):
        print("The URL is an IP address!")
        break
    else:
        print("The URL is not an IP address! Try again.")

# Login Area [bWAPP]
driver.get(f'{url}/login.php')
username = driver.find_element(By.XPATH, "//input[@type='text']")
username.send_keys("admin")
password = driver.find_element(By.NAME, "password")
password.send_keys("letmein" + Keys.ENTER)

# Target Link
base_url = url
xss_list = ["/xss_get.php", "/xss_post.php", "/xss_json.php", "/xss_ajax_2-1.php",
            "/xss_ajax_1-1.php", "/xss_eval.php", "/xss_login.php"]

xss_names = ["[0]: Cross-Site Scripting - Reflected (GET)", "[1]: Cross-Site Scripting - Reflected (POST)",
             "[2]: Cross-Site Scripting - Reflected (JSON)", "[3]: Cross-Site Scripting - Reflected (AJAX/JSON)",
             "[4]: Cross-Site Scripting - Reflected (AJAX/XML)", "[5]: Cross-Site Scripting - Reflected (Eval)",
             "[6]: Cross-Site Scripting - Reflected (Login Form)"]

print("bWAPP - an extremely buggy web app !")
print("/ A3 - Cross-Site Scripting (XSS) /")
for item in xss_names:
    print(item)

while True:
    choice = input("Choose one option to exploit: ")
    if choice in ["0", "1", "2", "3", "4", "5", "6"]:
        driver.get(base_url + xss_list[int(choice)])
        break
    else:
        print("Wrong choice. Please try again.")

# Get method
try:
    forms = driver.find_element(By.TAG_NAME, "form")
    actions = forms.get_attribute("action")
    methods = forms.get_attribute("method")
    actions = urljoin(base_url, actions)
    print(f"Target: {base_url}")
    print(f"Actions: {actions}")
    print(f"Method: {methods}")
except NoSuchElementException:
    actions = None
    methods = None

# Initialization
tables = []
count = 0

# Helpful code
# multiple_text1 = driver.find_elements(By.XPATH, "//input[@type='text']")
# multiple_text2 = {f"itext_{i}": elem for i, elem in enumerate(multiple_text1)}
# multiple_text3 = {f"itext_name_{i}": field.get_attribute("name") for i, field in enumerate(multiple_text1)}

# Load payload list
with open("payloads.txt", "r") as file:
    lines = file.readlines()
    total_lines = len(lines)
    print(f"Total payloads: {total_lines}")

# Target input text if exists
for line in lines:
    driver.get(actions)
    try:
        for element in driver.find_elements(By.XPATH, "//input[@type='text']"):
            itext_name = element.get_attribute("name")
            element.send_keys(f"{line.strip()}")
    except NoSuchElementException:
        itext_name = None
    try:
        ipass = driver.find_element(By.XPATH, "//input[@type='password']")
        ipass_name = ipass.get_attribute("name")
        ipass.send_keys(f"{line.strip()}")
    except NoSuchElementException:
        ipass_name = None
    try:
        imail = driver.find_element(By.XPATH, "//input[@type='email']")
        imail_name = imail.get_attribute("name")
        imail.send_keys(f"{line.strip()}")
    except NoSuchElementException:
        imail_name = None
    try:
        isearch = driver.find_element(By.XPATH, "//input[@type='search']")
        isearch_name = isearch.get_attribute("name")
        isearch.send_keys(f"{line.strip()}")
    except NoSuchElementException:
        isearch_name = None
    try:
        itextarea = driver.find_element(By.XPATH, "//textarea")
        itextarea_name = itextarea.get_attribute("name")
        itextarea.send_keys(f"{line.strip()}")
    except NoSuchElementException:
        itextarea_name = None
    if actions == base_url + "xss_ajax_1-1.php":
        actions = base_url + "xss_ajax_1-1.php"
    else:
        try:
            isubmit = driver.find_element(By.XPATH, "//input[@type='submit']")
            isubmit_name = isubmit.get_attribute("name")
            isubmit.click()
        except NoSuchElementException:
            isubmit_name = None
        try:
            isubmit_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
            isubmit_btn_name = isubmit_btn.get_attribute("name")
            isubmit_btn.click()
        except NoSuchElementException:
            isubmit_btn_name = None
    if actions == base_url + "xss_ajax_2-1.php" or actions == base_url + "xss_ajax_2-2.php":
        actions = base_url + "xss_ajax_2-2.php"
        driver.get(actions + f"?{itext_name}={line.strip()}")
    else:
        pass
    if actions == base_url + "xss_eval.php":
        driver.get(actions + f"?date={line.strip()}")
    else:
        pass

    # XSS checker
    try:
        WebDriverWait(driver, 1).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.accept()
        print("[+] XSS Found!")
        count = count + 1
        tables.append(line.strip())
        print(f"{actions}: Injected: {line.strip()}")
    except TimeoutException:
        print("[+] XSS not Found!")
    except UnexpectedAlertPresentException as e:
        print(f"Unexpected alert: {e}")
        pass
    try:
        alert2 = driver.switch_to.alert
        alert2.accept()
        print("[+] XSS Found!")
    except NoAlertPresentException:
        pass

print("\n[+] Table Summary [+]")
print('\n'.join(tables))
print(f"Total XSS Count: {count}")
print(f"Success: {count}/{total_lines}={round((count/total_lines)*100, 2)}%")

driver.quit()
