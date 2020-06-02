    import randomfreeproxy
    import time

    randomfreeproxy.checker_thread(expire_time=180) #initializing and setting expire time of data
    time.sleep(3)
    print(randomfreeproxy.get_random_proxy()) #getting proxy string
    randomfreeproxy.close_crawler()
    while True:
        print(randomfreeproxy.get_random_proxy())#getting proxy string
        time.sleep(15)
