import os
import re
import time
from datetime import datetime
import requests
from checker import proxyChecker


ExpireTime = 100 #in minutes
directorypath = "./ProxyData/"
file_ips = 'IpList.txt'
success_ips = 'Success.txt'
failed_ips = 'Failed.txt'


def WriteFile(filename, data):
    if not os.path.exists(directorypath):
        os.makedirs(directorypath)
    with open(directorypath + filename, 'w') as f:
        f.writelines("%s\n" % l for l in data)


def ReadFile(filename):
    if not os.path.exists(directorypath):
        return False
    else:
        with open(directorypath + filename, 'r') as f:
            readed_data = f.read().splitlines()
            return readed_data

def LastModifTimeDifFile(file):
    lastmodif = datetime.strptime(time.ctime(os.path.getmtime(file)), "%a %b %d %H:%M:%S %Y")
    now = datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
    dif = int((now - lastmodif).total_seconds() / 60.0)
    print('time dif', str(dif))
    return dif

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

        self.proxy_checker = None

    def init(self):
        print('[+]started')
        if not os.path.exists(directorypath + file_ips):
            self.sources = self.DataUrls()
            data = self.GetData(urls=self.sources)
            WriteFile(filename=file_ips, data=data)
            return data
        else:
            if LastModifTimeDifFile(directorypath + file_ips) > ExpireTime:
                self.sources = self.DataUrls()
                data = self.GetData(urls=self.sources)
                WriteFile(filename=file_ips, data=data)
                return data
            else:
                data = ReadFile(filename=file_ips)
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

    def Extract(self,data, patt):
        result = []
        while True:
            m = patt.search(data)
            if not m:
                break
            i = m.group()
            result.append(m.group())
            data = data[m.end():]
        return result

    def pprint(self):
        print(self.sources)

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

        IpList = IpList + self.proxynova()
        IpList = list(dict.fromkeys(IpList))
        return IpList

    def proxynova(self):
        urls = ['https://www.proxynova.com/proxy-server-list/country-bd',
                'https://www.proxynova.com/proxy-server-list/country-br',
                'https://www.proxynova.com/proxy-server-list/country-cl',
                'https://www.proxynova.com/proxy-server-list/country-cn',
                'https://www.proxynova.com/proxy-server-list/country-co',
                'https://www.proxynova.com/proxy-server-list/country-fr',
                'https://www.proxynova.com/proxy-server-list/country-de',
                'https://www.proxynova.com/proxy-server-list/country-hk',
                'https://www.proxynova.com/proxy-server-list/country-in',
                'https://www.proxynova.com/proxy-server-list/country-id',
                'https://www.proxynova.com/proxy-server-list/country-jp',
                'https://www.proxynova.com/proxy-server-list/country-ke',
                'https://www.proxynova.com/proxy-server-list/country-nl',
                'https://www.proxynova.com/proxy-server-list/country-pl',
                'https://www.proxynova.com/proxy-server-list/country-ru',
                'https://www.proxynova.com/proxy-server-list/country-rs',
                'https://www.proxynova.com/proxy-server-list/country-kr',
                'https://www.proxynova.com/proxy-server-list/country-tw',
                'https://www.proxynova.com/proxy-server-list/country-th',
                'https://www.proxynova.com/proxy-server-list/country-ua',
                'https://www.proxynova.com/proxy-server-list/country-gb',
                'https://www.proxynova.com/proxy-server-list/country-us',
                'https://www.proxynova.com/proxy-server-list/country-ve',
                'https://www.proxynova.com/proxy-server-list/country-ir',
                'https://www.proxynova.com/proxy-server-list/country-tr',
                'https://www.proxynova.com/proxy-server-list/country-na',
                'https://www.proxynova.com/proxy-server-list/country-mz',
                'https://www.proxynova.com/proxy-server-list/country-it',
                'https://www.proxynova.com/proxy-server-list/country-eg',
                'https://www.proxynova.com/proxy-server-list/country-bg'];

        reg_html = r"<td align(.*)\s(?!.*(<time|<div|<span)\s)(.*)\s(.*)\s(.*)\s(.*)\/td>"
        reg_port = r'(?!\.)\s([0-9]{2,5})\s(?!\.)'
        reg_ip = r"((?<=\(\'([\s]{0,}){0})(([0-9]{1,3}\.){3}[0-9]{1,3})(?=([\'\)]{0})))"
        reg_html = re.compile(reg_html)
        reg_port = re.compile(reg_port)
        reg_ip = re.compile(reg_ip)
        data_list = []

        for url in urls:
            print("[+] Started to Download: " + url)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
            }
            response = requests.get(url, headers=headers)
            time.sleep(2)
            statuscode = response.status_code
            if statuscode == 200:
                print("[+] Successfully Downloaded")
                data_htmlip = self.Extract(response.text, reg_html)
                temp_array = []
                for i in range(0, len(data_htmlip), 2):
                    temp_array.append(str(data_htmlip[i]) + str(data_htmlip[i + 1]))

                for iter in temp_array:
                    data_list.append(str(self.Extract(iter, reg_ip)[0]).rstrip().lstrip()
                                     + ":" +
                                     str(self.Extract(iter, reg_port)[0]).rstrip().lstrip()
                                     )
                print(data_list)
            else:
                print("[-] Got Problem with " + url)
        return data_list

    @staticmethod
    def data_checker(proxy_types, proxy_list):
        ##########################################
        writable_format = []
        lives = {}
        for type in proxy_types:
            result = proxyChecker(proxylist=proxy_list, checktype=type)
            # listLive, listDead = _tempcheck.get
            lives[type] = result.listLive
            for item in lives[type]:
                writable_format.append("{ip}-{type}".format(ip=item,type=type))
        WriteFile(filename=success_ips,data=writable_format)
        return lives

    @staticmethod
    def get_successed():
        lives={"https": [], "socks4": [], "socks5": []}
        file = ReadFile(filename=success_ips)
        for item in file:
            ip,type = item.split("-")
            lives[type].append(ip)
        return lives






proxy_types = ["https", "socks4", "socks5"]
x = Scrapper().init()
# data = Scrapper.data_checker(proxy_types=proxy_types, proxy_list=x)
success = Scrapper.get_successed()
#
