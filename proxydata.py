import re
import time
import os
import requests
from datetime import datetime
import os
import re
import time
from datetime import datetime

import requests


class Scrapper:
    """
        Scrapper class is use to scrape the proxies from various websites.
        """

    def __init__(self):
        """
        Initialization of scrapper class
        :param category: Category of proxy to scrape.
        :param print_err_trace: (True or False) are you required the stack trace for error's if they occured in the program
        """
        # init with Empty Proxy List
        self.proxies = []
        self.sources = None
        self.directorypath = "./ProxyData/"
        self.file_ips = 'IpList.txt'
        self.success_ips = 'Success.txt'
        self.failed_ips = 'Failed.txt'

    def init(self):
        print('[+]started')
        if not os.path.exists(self.directorypath + self.file_ips):
            self.sources = self.DataUrls()
            data = self.GetData(urls=self.sources)
            self.WriteFile(filename=self.file_ips, data=data)
            return data
        else:
            if self.LastModifTimeDifFile(self.directorypath + self.file_ips) > 120:
                self.sources = self.DataUrls()
                data = self.GetData(urls=self.sources)
                self.WriteFile(data)
            else:
                data = self.ReadFile(filename=self.file_ips)
                return data
        print('[+]done')

    def DataUrls(self):
        sources = None
        with open(r'./sources.txt', 'r') as f:
            sources = f.read().splitlines()
        return sources

    def RegProxy(self):
        # pattern_proxy = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]):[0-9]+$"
        pattern_proxy = r"([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{2,5})"
        compiledReg = re.compile(pattern_proxy, re.MULTILINE)
        return compiledReg

    def Extract(self, data, patt):
        result = []
        while True:
            m = patt.search(data)
            if not m:
                break
            i = m.group()
            if not i in result:
                result.append(m.group())
            data = data[m.end():]
        return result

    def pprint(self):
        print(self.sources)

    def WriteFile(self, filename, data):
        if not os.path.exists(self.directorypath):
            os.makedirs(self.directorypath)
        with open(self.directorypath + filename, 'w') as f:
            f.writelines("%s\n" % l for l in data)

    def ReadFile(self, filename):
        if not os.path.exists(self.directorypath):
            return False
        else:
            with open(self.directorypath + filename, 'r') as f:
                readed_data = f.readlines()
                return readed_data

    def LastModifTimeDifFile(self, file):
        lastmodif = datetime.strptime(time.ctime(os.path.getmtime(file)), "%a %b %d %H:%M:%S %Y")
        now = datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
        dif = int((now - lastmodif).total_seconds() / 60.0)
        print('time dif', str(dif))
        return dif

    def GetData(self, urls):
        IpList = []
        proxyFinder = self.RegProxy()
        for url in urls:
            print("[+] Started to Download: " + url)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
                'Accept': "application/json, text/javascript, */*; q=0.01",
                'Accept-Language': "de,en-US;q=0.7,en;q=0.3",
                'X-Requested-With': "XMLHttpRequest",
                'Referer': url,
                # 'Connection':"keep-alive"
            }
            response = requests.get(url, headers=headers)
            time.sleep(5)
            statuscode = response.status_code
            if statuscode == 200:
                print("[+] Successfully Downloaded")
                data = self.Extract(response.text, proxyFinder)
                IpList = IpList + data
            else:
                print("[-] Got Problem with " + url)

        IpList = list(dict.fromkeys(IpList))
        return IpList


# import checker
# data = Scrapper().getData()
# x = checker.Main(proxylist=data, checktype="socks5")
# print("ddddddd")


# seq = ["This is 6th line", "This is 7th line"]

Scrapper().init()
