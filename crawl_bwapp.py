import scanning
import re

# http://localhost:8090
while True:
    url2 = input("Please give the url of bWAPP:\n")
    if re.match(r"^(http|https)://(?:localhost|(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))\S*$", url2):
        print("The URL is an IP address!")
        break
    else:
        print("The URL is not an IP address! Try again.")

ignored = [f"{url2}/logout.php"]
target = url2
data = {"login": "admin", "password": "letmein", "security_level": "0", "form": "submit"}

scan = scanning.Scanning(target, ignored)
scan.session.post(f"{url2}/login.php", data=data)

scan.crawling(target)
scan.exploit_link()
scan.running()
