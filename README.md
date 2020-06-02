RandomFreeProxy
--------

RandomFreeProxy is an open source tool that asynchronously crawler public proxies from multiple sources and concurrently checks them.

Features
--------

* Finds more than 9000 proxies
* Support protocols: HTTP(S), SOCKS4/5
* Proxies may be filtered by type.
* Automatically removes duplicate proxies.
* Is synchronous.
* Save found proxies to a file in custom format.

Requirements
------------
    $ pip install -r  requirements.txt

* Python **3.5** or higher
* `requests <https://pypi.python.org/pypi/requests>`
* `requests[socks]`

Basic code example
------------

Initialize and get proxy dictionary string

```python
import randomfreeproxy
import time

randomfreeproxy.checker_thread(expire_time=180) #initializing and setting expire time of data
time.sleep(3)
print(randomfreeproxy.get_random_proxy()) #getting proxy string
randomfreeproxy.close_crawler()
while True:
    print(randomfreeproxy.get_random_proxy())#getting proxy string
    time.sleep(15)

```

**Output**
```
{'http': 'http://203.190.33.51:8080', 'https': 'https://203.190.33.51:8080'}
{'http': 'socks5://81.19.223.180:1080', 'https': 'socks5://81.19.223.180:1080'}
{'http': 'socks4://104.248.63.18:30588', 'https': 'socks4://104.248.63.18:30588'}
{'http': 'http://104.248.63.15:30588', 'https': 'https://104.248.63.15:30588'}
{'http': 'socks4://104.248.63.17:30588', 'https': 'socks4://104.248.63.17:30588'}
{'http': 'socks5://104.248.63.18:30588', 'https': 'socks5://104.248.63.18:30588'}
{'http': 'socks4://110.49.101.58:1080', 'https': 'socks4://110.49.101.58:1080'}
```


To Do
-----
* logging
* hidemy.me will be parsed and add as resource <https://hidemy.name/en/proxy-list/?maxtime=1000&anon=64&start=0#list>


