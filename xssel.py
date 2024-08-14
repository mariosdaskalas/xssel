from bs4 import BeautifulSoup
import requests
import re
import time
import datetime
import urllib.parse
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException, UnexpectedAlertPresentException, \
    NoAlertPresentException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import argparse
from urllib.parse import urlparse, parse_qs
import sys

service = Service('/usr/local/bin/chromedriver')
options = webdriver.ChromeOptions()
options.add_argument('window-size=1920,1080')
options.add_argument('--headless')
#options.add_argument('--disable-notifications')
#options.add_argument('--disable-popup-blocking')
#options.add_argument("--no-sandbox")
#options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=service, options=options)

# Login Area [bWAPP]
# driver.get(f'http://localhost:8090/login.php')
# username = driver.find_element(By.XPATH, "//input[@type='text']")
# username.send_keys("admin")
# password = driver.find_element(By.NAME, "password")
# password.send_keys("letmein" + Keys.ENTER)

parser = \
    argparse.ArgumentParser(epilog='Command : python3 xssel.py -l "http://www.sudo.co.il/xss/level0.php" -p load.txt'
                            )
parser.add_argument('-l',
                    help='Add URL for XSS exploitation',
                    required=False)
parser.add_argument('-u',
                    help='Add URL with parameter as ={xss}',
                    required=False)
parser.add_argument('-w',
                    help='Add url for POST request',
                    required=False)
parser.add_argument('-d',
                    help='Add data POST',
                    required=False)
parser.add_argument('-p',
                    help='Add file containing all the payloads',
                    required=True)
args = parser.parse_args()
url = args.l
target = args.u
post_data = args.d
links = args.w
load = args.p
lines = []
# Initialization
tables = []
count = 0


def prevent_xss():
    prevent = '''
*** Cross Site Scripting Prevention Tactics ***
    
- Try to filter input
Where the input of the user is received, filter as rigorously as possible based on valid input.

- Encode data
The output must be encoded to avoid being interpreted as is. This might apply on URL, HTML, Javascript.

- Content Security Policy (CSP)
As a last resort, someone can use CSP to lessen the seriousness of any Cross Site Scripting vulnerabilities.

- Usage of right response headers
HTTP responses should not contain Javascript and HTML code, thus someone can use the 'Content-Type'
headers, so Cross Site Scripting is reduced to its minimum.

*** Examples ***

- Encoding output regarding HTML contexts

<p> $iamnotsafe </p>
<p> <script>alert'pwned'</script> </p>
.textContent attribute converts HTML entities

>    &gt;
<    &lt;
'    &#x27;
"    &quot;
&    &amp;

- Encoding output regarding CSS contexts

Variables must only live in a CSS property value. All other locations are unsafe.
<style> p { property : "$iamsafe"; } </style>
<p style="property : $iamnotsafe">Danger!</p>

- Encoding output regarding URL contexts

<a href="http://example.com?test=$iamnotsafe">link example</a> - GET request
Fixing: link = "https://example.com?test=" + urlencode(parameter)

    '''
    return prevent


try:
    with open(load, "r") as file:
        lines = file.readlines()
        total_lines = len(lines)
        print(f"Total Payloads: {total_lines}")
except FileNotFoundError:
    print(f"File {load} does not exist.")
    print(f"Try again giving an existing payload file.")


def xss(link):
    global count
    global tables
    for line in lines:
        link = target.replace('{xss}', line)
        driver.get(link)
        try:
            WebDriverWait(driver, 1).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert.accept()
            print("[+] XSS Found!")
            print(f"{link}")
            count = count + 1
            tables.append(line.strip())
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
    print(f"Success: {count}/{total_lines}={round((count / total_lines) * 100, 2)}%")
    print(prevent_xss())


if target:
    xss(target)
else:
    pass
    #print("Failed. Please give a parameter as -u 'http://www.sudo.co.il/xss/level0.php?email={xss}#' -p load.txt")


def extract(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    suspicious = []
    holder = []
    for tag in soup.find_all(["input", "textarea", "img", "iframe"]):
        suspicious.append(tag)

    for tag in suspicious:
        if re.search("input", str(tag)):
            holder.append("input")
        elif re.search("textarea", str(tag)):
            holder.append("textarea")
        elif re.search("img", str(tag)):
            holder.append("img")
        elif re.search("iframe", str(tag)):
            holder.append("iframe")
        else:
            print("Not found!")
    holder_output = [i for n, i in enumerate(holder) if i not in holder[:n]]
    print(f"Suspicious tags found: {holder_output}")

    forms = soup.find_all("form")
    if forms:
        for form in forms:
            method = form.get("method")
            print(f"Form: {method}")
            inputs = form.find_all('input', type='text')
            inputs_names = [input.get('name') for input in inputs]

            params = {}
            input_values = ['payload']
            input_values *= len(inputs_names)
            for name, value in zip(inputs_names, input_values):
                params[name] = value

            url += '?' + urllib.parse.urlencode(params)
            print(f"Possible vulnerable url: {url}")
    else:
        print("No forms found!")
    print(f"Status Code: {response.status_code}")
    times = datetime.datetime.now()
    print("Started at: ", times)
    return suspicious


# Initialization
tables = []
count = 0


def exploit(url):
    global count
    global tables
    for line in lines:
        driver.get(url)
        try:
            for element in driver.find_elements(By.XPATH, "//input[@type='text']"):
                itext_name = element.get_attribute("name")
                element.send_keys(f"{line.strip()}")
        except NoSuchElementException:
            itext_name = None
        try:
            imail = driver.find_element(By.XPATH, "//input[@type='email']")
            imail_name = imail.get_attribute("name")
            imail.send_keys(f"{line.strip()}")
        except NoSuchElementException:
            imail_name = None
        try:
            for element in driver.find_elements(By.XPATH, "//textarea"):
                itextarea_name = element.get_attribute("name")
                element.send_keys(f"{line.strip()}")
        except NoSuchElementException:
            itextarea_name = None
        try:
            isubmit = driver.find_element(By.XPATH, "//input[@type='submit']")
            isubmit_name = isubmit.get_attribute("name")
            isubmit.click()
        except NoSuchElementException:
            isubmit_name = None
        try:
            WebDriverWait(driver, 1).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert.accept()
            print("[+] XSS Found!")
            print(f"Payload: {line}")
            print(f"{url}")
            count = count + 1
            tables.append(line.strip())
        except TimeoutException:
            print("[+] XSS not Found!")
        try:
            alert2 = driver.switch_to.alert
            alert2.accept()
            print("[+] XSS Found!")
            time.sleep(10)
            alert2.accept()
        except NoAlertPresentException:
            pass


tables = []
count = 0


#

def redirecting():
    # suspicious = extract(url)
    # response = requests.head(url)
    # redirect_url = response.headers.get("Location")
    global tables
    global count
    print("Redirect Target: " + str(redirect_url))
    for line in lines:
        parsed_url = urlparse(redirect_url)
        params = parse_qs(parsed_url.query)
        payload = str(list(params.values()))
        payload2 = ''.join(map(str, list(params.values())[0]))
        link = redirect_url.replace(f"{payload2}", line)
        driver.get(link)
        try:
            WebDriverWait(driver, 1).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert.accept()
            print("[+] XSS Found!")
            print(f"Payload: {line}")
            print(f"{redirect_url}")
            count = count + 1
            tables.append(line.strip())
        except TimeoutException:
            print("[+] XSS not Found!")
        except UnexpectedAlertPresentException as e:
            print(f"Unexpected alert: {e}")
            pass
        try:
            alert2 = driver.switch_to.alert
            alert2.accept()
            print("[+] XSS Found!")
            print(f"Payload: {line}")
            print(f"{link}")
        except NoAlertPresentException:
            pass


if url:
    extract(url)
    response = requests.head(url)
    redirect_url = response.headers.get("Location")
    if redirect_url is not None:
        redirecting()
        print("\n[+] Table Summary [+]")
        print('\n'.join(tables))
        print(f"Total XSS Count: {count}")
        print(f"Success: {count}/{total_lines}={round((count / total_lines) * 100, 2)}%")
        print(prevent_xss())
    else:
        print("There is no redirect url.")
        exploit(url)
        print("\n[+] Table Summary [+]")
        print('\n'.join(tables))
        print(f"Total XSS Count: {count}")
        print(f"Success: {count}/{total_lines}={round((count / total_lines) * 100, 2)}%")
        print(prevent_xss())
else:
    pass
    #print("Failed. Please give a parameter as -l 'http://www.sudo.co.il/xss/level0.php' -p load.txt")


def post_xss(links):
    data = {}
    # print(post_data)

    parsed_query = urllib.parse.parse_qs(post_data)
    data = {key: value[0] for key, value in parsed_query.items()}
    print(f"Elements: {data}")

    edata = urllib.parse.urlencode(data)
    resp = requests.post(links, data=edata)
    # print(resp.text)
    global count
    global tables
    for line in lines:
        #link = url.replace('{xss}', line)
        driver.get(links)
        search_form = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, next(k for i, (k, v) in enumerate(data.items()) if i % 2 == 0)))
        )
        search_form.send_keys(f"{line.strip()}")
        submit_button = driver.find_element(By.XPATH, "//input[@type='submit']")
        submit_button.click()
        try:
            WebDriverWait(driver, 1).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert.accept()
            print("[+] XSS Found!")
            print(f"Payload: {line}")
            print(f"{links}")
            count = count + 1
            tables.append(line.strip())
        except TimeoutException:
            print("[+] XSS not Found!")
        except UnexpectedAlertPresentException as e:
            print(f"Unexpected alert: {e}")
            pass
        try:
            alert2 = driver.switch_to.alert
            alert2.accept()
            print("[+] XSS Found!")
            print(f"Payload: {line}")
        except NoAlertPresentException:
            pass
    print("\n[+] Table Summary [+]")
    print('\n'.join(tables))
    print(f"Total XSS Count: {count}")
    print(f"Success: {count}/{total_lines}={round((count / total_lines) * 100, 2)}%")
    print(prevent_xss())


if links:
    post_xss(links)
else:
    pass

driver.quit()
