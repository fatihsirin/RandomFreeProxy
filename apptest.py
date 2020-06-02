import randomfreeproxy
import time
import requests

randomfreeproxy.checker_thread(expire_time=1800)
time.sleep(5)
randomfreeproxy.close_crawler()
proxies = {}
while True:
    proxies = randomfreeproxy.get_random_proxy()
    r = requests.get("http://ipinfo.io/ip", proxies=proxies)
    print(proxies)
    if r.status_code == 200:
        print("Request's IP Address: " + r.text)
        print("----------")

    time.sleep(5)