Update the system

```sudo apt update```

Install all necessary modules

```pip3 install -r requirements.txt``` 

Install Google Chrome for Linux (if you already do not have)

```
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb
```

You can run Google Chrome and find it's version

```
google-chrome --no-sandbox
google-chrome --version
```

Download chromedriver

Visit the following link and download the 64-bit linux zipped version of your Google Chrome version
https://googlechromelabs.github.io/chrome-for-testing/

For example for version Version: 127.0.6533.119 (r1313161) that would be the following.
chromedriver	linux64	https://storage.googleapis.com/chrome-for-testing-public/127.0.6533.119/linux64/chromedriver-linux64.zip

Unzip the file, save it in the same locations as the program and copy the chromedriver to the following location.

```
sudo chmod +x chromedriver
sudo mv -f chromedriver /usr/local/bin/chromedriver
```

You can make sure that the process is complete by running

```which chromedriver```

If the output is the following you are good to go..

```/usr/local/bin/chromedriver```

Install bWAPP with Docker

```sudo docker run -d -p 8090:80 hackersploit/bwapp-docker```

This will run on the following link.
http://localhost:8090/

Install and register as a new user using the following credentials

Username: admin
Password: letmein

```python3 bwapp.py```

Some sample commands to run for.

```
python3 xssel.py -l "http://www.sudo.co.il/xss/level0.php" -p load.txt
python3 xssel.py -l "http://www.sudo.co.il/xss/level1.php" -p load.txt
python3 xssel.py -u "https://sudo.co.il/xss/level0.php?email={xss}#" -p load.txt
```

Crawling for bWAPP and WordPress

```
python3 crawl_bwapp.py
python3 crawl_wp.py
```