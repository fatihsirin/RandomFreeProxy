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

Find and show 10 working HTTP(S) proxies:

.. code-block:: python

    import randomfreeproxy
    import time
    
    randomfreeproxy.checker_thread(expire_time=180) #initializing and setting expire time of data
    time.sleep(3)
    print(randomfreeproxy.get_random_proxy()) #getting proxy string
    randomfreeproxy.close_crawler()
    while True:
        print(randomfreeproxy.get_random_proxy())#getting proxy string
        time.sleep(15)


`More examples <https://proxybroker.readthedocs.io/en/latest/examples.html>`_.



#To Do
* logging
* hidemy.me will be parsed and add as resource <https://hidemy.name/en/proxy-list/?maxtime=1000&anon=64&start=0#list>
