# from ctypes import windll
import threading
from multiprocessing.dummy import Pool as ThreadPool
from queue import Queue
from threading import Thread
from time import sleep

from requests import ConnectionError, get, exceptions
from urllib3.connectionpool import SocketError, SSLError, MaxRetryError, ProxyError

#checks socks dependencies is exists
try:
    from urllib3.contrib.socks import SOCKSProxyManager
    #import requests.packages.urllib3.util.connection as requests_connection
except ImportError:
    raise exceptions.InvalidSchema ("Missing dependencies for SOCKS support.")

default_values = '''checker:
  # Check if current version of CheckX is latest  
  check_for_updates: true
  # Higher for better accuracy but slower (counted in milliseconds)
  timeout: 8000
  # Threads for account checking
  threads: 200
  # Proxy types: https | socks4 | socks5
  proxy_type: 'socks4'

  # Save not working proxies (will take a little longer than normal)
  save_dead: true
  # Normal users should keep this false unless problem start happening
  debugging: false
'''


class proxyChecker():
    def __init__(self,proxylist,checktype):
        # if self.checktype not in ['socks4', 'socks5', 'https', 'http']:
        #     raise BaseException("Proxy type is unknown, Please enter correct proxy type (SOCKS4, SOCKS5, HTTPS):")
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
        self.proxyjudge = 'http://ipinfo.io/ip'
        self.checktype = checktype
        self.threadPoints = []
        self._stopevent = threading.Event()
        self.pool = None
        self.accounts = [x for x in self.proxylist if ':' in x]
        self.scan()

    def scan(self):
        self.threadPoints.append(Thread(target=self.save_dead,name="a"))
        self.threadPoints.append(Thread(target=self.save_hits,name="b"))
        self.threadPoints.append(Thread(target=self.save_trans,name="c"))
        # self.threadPoints.append(Thread(target=self.cpmcounter,name="d"))
        self.threadPoints.append(Thread(target=self.tite,name="e"))
        for ths in self.threadPoints:
            ths.start()
            print(ths.getName()+" is: " + str(ths.isAlive()))
        self.pool = ThreadPool()

        print('\nPlease wait for proxies to finish checking...')
        self.pool.imap(func=self.check_proxies, iterable=self.accounts)
        self.pool.close()
        self.pool.join()
        while True:
            if int(self.savelive.qsize() + self.savedead.qsize() + self.savedead.qsize()) == 0:
                print(f'\nLive proxies: {self.live}\n'
                      f'Transparent proxies: {self.trasp}\n'
                      f'Dead proxies: {self.dead}\n')
                break
        print("done baby ------------")
        # for i in self.proxylist:
        #     print(i)
        self.join()
        print("[+] Worked Success")

    def join(self, timeout=None):
        """ Stop the thread. """
        self._stopevent.set()
        for ths in self.threadPoints:
            print("starting to join" + ths.getName())
            ths.join()
            print(ths.getName() + " is: " + str(ths.isAlive()))

    def save_dead(self):
        while not self._stopevent.isSet():
            while self.savedead.qsize() != 0:
                self.listDead.append(self.savedead.get())

    def save_hits(self):
        while not self._stopevent.isSet():
            while self.savelive.qsize() != 0:
                self.listLive.append(self.savelive.get())

    def save_trans(self):
        while not self._stopevent.isSet():
            while self.savetrans.qsize() != 0:
                self.listTrasp.append(self.savetrans.get())

    def check_proxies(self, proxy):

        proxy_dict = {}
        if proxy.count(':') == 3:
            spl = proxy.split(':')
            proxy = f'{spl[2]}:{spl[3]}@{spl[0]}:{spl[1]}'
        if self.checktype == 'http' or self.checktype == 'https':
            proxy_dict = {
                'http': f'http://{proxy}',
                'https': f'https://{proxy}'
            }
        elif self.checktype == 'socks4' or self.checktype == 'socks5':
            proxy_dict = {
                'http': f'{self.checktype}://{proxy}',
                'https': f'{self.checktype}://{proxy}'
            }
        try:
            r = get(url=self.proxyjudge, proxies=proxy_dict, timeout=10).text
            self.live += 1
            self.savelive.put(proxy)
            # disabled to get trans in another array,
            # if r.__contains__(self.myip):
            #     self.trasp += 1
            #     self.savetrans.put(proxy)
            # else:
            #     self.live += 1
            #     self.savelive.put(proxy)
        except (ConnectionError, SocketError, SSLError, MaxRetryError, ProxyError):
            self.dead += 1
            self.savedead.put(proxy)

    def tite(self):
        while not self._stopevent.isSet():
            # windll.kernel32.SetConsoleTitleW(
            #     f'Live: {self.live}'
            #     f' | Dead: {self.dead}'
            #     f' | Transparent {self.trasp}'
            #     f' | Left: {len(self.accounts) - (self.live + self.dead + self.trasp)}/{len(self.accounts)}'
            #     f' | CPM: {self.cpm}')
            sleep(0.1)

    def cpmcounter(self):
        while not self._stopevent.isSet():
            while (self.live + self.dead) >= 1:
                now = self.live + self.dead
                self.cpm = (self.live + self.dead - now) * 15

    def get_results(self):
        return self.listLive, self.listDead
