import asyncio
import re
import time

import aiohttp
import requests


#
# def regProxy():
#     # pattern_proxy = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]):[0-9]+$"
#     pattern_proxy = r"([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{2,4})"
#     compiledReg = re.compile(pattern_proxy, re.MULTILINE)
#     return compiledReg
#
#
# def extract(data, patt):
#     result = []
#     while True:
#         m = patt.search(data)
#         if not m:
#             break
#         i = m.group()
#         if not i in result:
#             result.append(m.group())
#         data = data[m.end():]
#     return result
#
#
# def dataUrl():
#     sources = None
#     with open(r'./sources.txt', 'r') as f:
#         sources = f.read().splitlines()
#     return sources
#
#
# def getData():
#     IpList = []
#     proxyFinder = regProxy()
#     urls = dataUrl()
#     for url in urls:
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
#             'Accept': "application/json, text/javascript, */*; q=0.01",
#             'Accept-Language': "de,en-US;q=0.7,en;q=0.3",
#             'X-Requested-With': "XMLHttpRequest",
#             'Referer': url,
#             # 'Connection':"keep-alive"
#         }
#         response = requests.get(url, headers=headers)
#         time.sleep(1)
#         statuscode = response.status_code
#         if statuscode == 200:
#             data = extract(response.text, proxyFinder)
#             IpList = IpList + data
#
#     IpList = list(dict.fromkeys(IpList))
#     return IpList
#

# getData()


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
        self.sources = self.dataUrl()

    def dataUrl(self):
        sources = None
        with open(r'./sources.txt', 'r') as f:
            sources = f.read().splitlines()
        return sources

    def regProxy(self):
        # pattern_proxy = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]):[0-9]+$"
        pattern_proxy = r"([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{2,4})"
        compiledReg = re.compile(pattern_proxy, re.MULTILINE)
        return compiledReg

    def extract(self, data, patt):
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

    def getData(self):
        IpList = []
        proxyFinder = self.regProxy()
        urls = self.sources
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
                data = self.extract(response.text, proxyFinder)
                IpList = IpList + data
            else:
                print("[-] Got Problem with " + url)

        IpList = list(dict.fromkeys(IpList))
        return IpList


TIMEOUT = 30
# CHECK_URLS = ['https://ifconfig.co/ip']

CHECK_URLS = (
    ('ifconfig', 'https://ifconfig.co/ip'),
)


async def check_proxy(proxy):
    """Try to load content of several commonly known websites through proxy"""

    timeout = aiohttp.ClientTimeout(total=TIMEOUT)
    result = dict()
    ip, port = proxy.split(':')
    result['ip'] = ip
    result['port'] = port

    for website_name, url in CHECK_URLS:
        try:
            async with aiohttp.ClientSession(timeout=timeout, connector=aiohttp.TCPConnector(ssl=False)) as session:
                start = time.time()
                status_code = 404
                total_time = None
                error_msg = 'no'
                async with session.get(url, proxy='http://{}:{}'.format(ip, port)) as resp:
                    status_code = resp.status
                    await resp.text()
                    end = time.time()
                    total_time = int(round(end - start, 2) * 1000)
        except asyncio.TimeoutError:
            status_code = 408
            error_msg = 'timeout error'
        except aiohttp.client_exceptions.ClientProxyConnectionError:
            error_msg = 'connection error'
            status_code = 503
        except Exception as e:
            status_code = 503
            error_msg = 'unknown error: {}.'.format(e)
        finally:
            result[website_name + '_status'] = status_code
            result[website_name + '_error'] = error_msg
            result[website_name + '_total_time'] = total_time
    print(result)
    return result


async def runner(complete_list):
    tasks = [check_proxy(item) for item in complete_list]
    return await asyncio.gather(*tasks)


data = Scrapper().getData()
try:
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(runner(data))
finally:
    loop.close()
# return result
