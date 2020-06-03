import os
import re
import time
from datetime import datetime
import requests
import random
import threading
from multiprocessing.dummy import Pool as ThreadPool
from queue import Queue
from threading import Thread

from requests import ConnectionError, get, exceptions
from urllib3.connectionpool import SocketError, SSLError, MaxRetryError, ProxyError


try:  # checks socks dependencies is exists
    from urllib3.contrib.socks import SOCKSProxyManager
except ImportError:
    raise exceptions.InvalidSchema("Missing dependencies for SOCKS support.")

directorypath = "./ProxyData/"
file_ips = 'IpList.txt'
success_ips = 'Success.txt'
failed_ips = 'Failed.txt'
temp_success_ips = 'temp_Success.txt'

ip_list_bytype = {"https": [], "socks4": [], "socks5": []}
check_status = None  # started == 1 , done == 0

_stopevent = threading.Event()
expire_time = 1800  # 60 minutes for expire data
#######################################################################################################
success_file_data = {"https": [], "socks4": [], "socks5": []}

class proxyChecker():
    def __init__(self,proxylist, checktype):
        self.dead = 0
        self.live = 0
        self.cpm = 0
        self.trasp = 0
        self.listLive = []
        self.listDead = []
        self.listTrasp = []
        self.savelive = Queue()
        self.savedead = Queue()
        self.savetrans = Queue()
        self.proxylist = proxylist
        self.folder = "./"
        self.myip = str(get('http://api.ipify.org').text)
        self.proxyjudge = ['http://ipinfo.io/ip', 'https://ifconfig.me/ip','https://ipconfig.io/ip']
        self.checktype = checktype
        self.threadPoints = []
        self._stopevent = threading.Event()
        self.pool = None
        self.accounts = [x for x in self.proxylist if ':' in x]
        self.scan()

    def scan(self):
        # print("starting threads")
        self.threadPoints.append(Thread(target=self.save_dead,name="save_dead"))
        self.threadPoints.append(Thread(target=self.save_hits,name="save_hits"))
        self.threadPoints.append(Thread(target=self.realtime_write, name="realtime_write"))
        for ths in self.threadPoints:
            ths.start()
            # print(ths.getName()+" is: " + str(ths.isAlive()))
        self.pool = ThreadPool()

        # print('\nPlease wait for proxies to finish checking...')
        self.pool.imap(func=self.check_proxies, iterable=self.accounts)
        self.pool.close()
        self.pool.join()
        while True:
            if int(self.savelive.qsize() + self.savedead.qsize() + self.savedead.qsize()) == 0:
                break
        # print("[+] Worked Success")

    def join(self):
        """ Stop the thread. """
        self._stopevent.set()
        for ths in self.threadPoints:
            # print("starting to join" + ths.getName())
            ths.join()
            # print(ths.getName() + " is: " + str(ths.isAlive()))

    def save_dead(self):
        while not self._stopevent.isSet():
            while self.savedead.qsize() != 0:
                self.listDead.append(self.savedead.get())

    def save_hits(self):
        while not self._stopevent.isSet():
            while self.savelive.qsize() >= 2:
                self.listLive.append(self.savelive.get())
                _temp_live = self.savelive.get()
                ip_list_bytype[_temp_live[0]].append(_temp_live[1])

    def check_proxies(self, proxy):
        proxy_types = ["https", "socks4", "socks5"]
        # print(proxy)
        for checktype in proxy_types:
            time.sleep(0.5)
            proxy_dict = {}
            if proxy.count(':') == 3:
                spl = proxy.split(':')
                proxy = f'{spl[2]}:{spl[3]}@{spl[0]}:{spl[1]}'
            if checktype == 'http' or checktype == 'https':
                proxy_dict = {
                    'http': f'http://{proxy}',
                    'https': f'https://{proxy}'
                }
            elif checktype == 'socks4' or checktype == 'socks5':
                proxy_dict = {
                    'http': f'{checktype}://{proxy}',
                    'https': f'{checktype}://{proxy}'
                }
            try:
                r = get(url=random.choice(self.proxyjudge), proxies=proxy_dict, timeout=30).text
                self.live += 1
                self.savelive.put(proxy)
                self.savelive.put([checktype,proxy])
            except (ConnectionError, SocketError, SSLError, MaxRetryError, ProxyError):
                self.dead += 1
                self.savedead.put(proxy)
            except Exception as e:
                time.sleep(5)



    def get_results(self):
        return self.listLive, self.listDead

    def realtime_write(self):
        time.sleep(30)
        while not self._stopevent.isSet():
            writable_format = []
            time.sleep(15)
            for key in ip_list_bytype.keys():
                for item in ip_list_bytype[key]:
                    writable_format.append("{ip}-{type}".format(ip=item, type=key))
            WriteFile(filename=success_ips, data=writable_format)
            time.sleep(10)

############################################################################################################
def WriteFile(filename, data):
    if not os.path.exists(directorypath):
        os.makedirs(directorypath)
    with open(directorypath + filename, 'w') as f:
        f.writelines("%s\n" % l for l in data)

def ReadFile(filename):
    if not os.path.exists(directorypath+filename):
        return False
    else:
        with open(directorypath + filename, 'r') as f:
            readed_data = f.read().splitlines()
            return readed_data

def LastModifTimeDifFile(file):
    if not os.path.exists(file):
        return False
    else:
        lastmodif = datetime.strptime(time.ctime(os.path.getmtime(file)), "%a %b %d %H:%M:%S %Y")
        now = datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
        dif = int((now - lastmodif).total_seconds() / 60.0)
        # print('time dif', str(dif))
        return dif

class Scrapper:
    """
    Scrapper class is use to scrape the proxies from various websites.
    """

    def __init__(self,expire_time=100):
        """
        Initialization of scrapper class
        :param category: Category of proxy to scrape.
        """
        # init with Empty Proxy List
        self.proxies = []
        self.sources = None
        self.ExpireTime = expire_time
        self.proxy_checker = None # in minutes


    def init(self):
        global success_file_data
        success_file_data = Scrapper.get_successed(expire_time)
        data = None
        # print('[+]started')
        if not os.path.exists(directorypath + file_ips):
            self.sources = self.DataUrls()
            data = self.GetData(urls=self.sources)
            WriteFile(filename=file_ips, data=data)
        else:
            if LastModifTimeDifFile(directorypath + file_ips) > self.ExpireTime:
                self.sources = self.DataUrls()
                data = self.GetData(urls=self.sources)
                WriteFile(filename=file_ips, data=data)
            else:
                data = ReadFile(filename=file_ips)
        # print('[+]done')
        return data

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

    def GetData(self, urls):
        IpList = []
        proxyFinder = self.RegProxy()
        for url in urls:
            # print("[+] Started to Download: " + url)
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
                # print("[+] Successfully Downloaded")
                data = self.Extract(response.text, proxyFinder)
                IpList = IpList + data
            else:
                pass
                # print("[-] Got Problem with " + url)

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
            # print("[+] Started to Download: " + url)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
            }
            response = requests.get(url, headers=headers)
            time.sleep(2)
            statuscode = response.status_code
            if statuscode == 200:
                # print("[+] Successfully Downloaded")
                data_htmlip = self.Extract(response.text, reg_html)
                temp_array = []
                for i in range(0, len(data_htmlip), 2):
                    temp_array.append(str(data_htmlip[i]) + str(data_htmlip[i + 1]))

                for iter in temp_array:
                    data_list.append(str(self.Extract(iter, reg_ip)[0]).rstrip().lstrip()
                                     + ":" +
                                     str(self.Extract(iter, reg_port)[0]).rstrip().lstrip()
                                     )
                # print(data_list)
            else:
                pass
                # print("[-] Got Problem with " + url)
        return data_list

    @staticmethod
    def data_checker(proxy_list):
        proxy_types = ["https", "socks4", "socks5"]
        writable_format = []
        proxyChecker(proxylist=proxy_list, checktype=type)
        lives = ip_list_bytype
        for key in lives.keys():
            for item in lives[key]:
                writable_format.append("{ip}-{type}".format(ip=item, type=key))
        WriteFile(filename=success_ips,data=writable_format)
        return lives

    @staticmethod
    def get_successed(expiretime):
        lives={"https": [], "socks4": [], "socks5": []}
        mod_time = LastModifTimeDifFile(directorypath+success_ips)
        if mod_time < expiretime:
            file = ReadFile(filename=success_ips)
            if file:
                for item in file:
                    ip, type = item.split("-")
                    lives[type].append(ip)
                return lives
            else:
                return {"https": [], "socks4": [], "socks5": []}
        else:
            return {"https": [], "socks4": [], "socks5": []}

########################################################################################################################

def get_list(expire_time=1800):
    threads = []
    while not _stopevent.isSet():
        # print(time.ctime())
        scrapper = Scrapper(expire_time=expire_time)
        data = scrapper.init()
        Scrapper.data_checker(proxy_list=data)
        time.sleep(expire_time)

def checker_thread(expire_time=1800):
    threading.Thread(target=get_list, args=[expire_time]).start()

def close_crawler():
    _stopevent.set()

def get_random_proxy():
    global ip_list_bytype
    global success_file_data
    proxy_dict = None
    success = None
    if not (len(ip_list_bytype["https"]) and len(ip_list_bytype["socks4"]) and len(ip_list_bytype["socks5"])):
        success = Scrapper.get_successed(expire_time)
        success = {"https": [], "socks4": [], "socks5": []}
        success["https"] = success_file_data["https"] + ip_list_bytype["https"]
        success["socks4"] = success_file_data["socks4"] + ip_list_bytype["socks4"]
        success["socks5"] = success_file_data["socks5"] + ip_list_bytype["socks5"]

    elif success and (len(ip_list_bytype["https"]) and len(ip_list_bytype["socks4"]) and len(ip_list_bytype["socks5"])):
        # print("waiting for success proxy output")
        return None
    elif len(ip_list_bytype["https"]) and len(ip_list_bytype["socks4"]) and len(ip_list_bytype["socks5"]):
        success = ip_list_bytype

    if not success:
        proxy_dict = {
            "http": None,
            "https": None,
        }
        # print("[-] Proxy is disabled. Waiting for data.")
        return proxy_dict
    else:
        checktype = random.choice(list(success.keys()))
        # print("checktype ->>>>>" + checktype)
        if success[checktype]:
            proxy = random.choice(success[checktype])
            if checktype == 'http' or checktype == 'https':
                proxy_dict = {
                    'http': f'http://{proxy}',
                    'https': f'https://{proxy}'
                }
            elif checktype == 'socks4' or checktype == 'socks5':
                proxy_dict = {
                    'http': f'{checktype}://{proxy}',
                    'https': f'{checktype}://{proxy}'
                }
        else:
            proxy_dict = {
                "http": None,
                "https": None,
            }
        return proxy_dict


def main():
    print("starting thread")
    checker_thread()
    print("starting proxy data")
    time.sleep(3)
    print(get_random_proxy())
    close_crawler()
    while True:
        print(get_random_proxy())
        time.sleep(15)
    pass

if __name__ == '__main__':
    main()
