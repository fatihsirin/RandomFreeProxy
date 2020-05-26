import re
import time

import requests


def regProxy():
    # pattern_proxy = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]):[0-9]+$"
    pattern_proxy = r"([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{2,4})"
    compiledReg = re.compile(pattern_proxy, re.MULTILINE)
    return compiledReg


def extract(data, patt):
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


def dataUrl():
    sources = None
    with open(r'./sources.txt', 'r') as f:
        sources = f.read().splitlines()
    return sources


def getData():
    IpList = []
    proxyFinder = regProxy()
    urls = dataUrl()
    for url in urls:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
            'Accept': "application/json, text/javascript, */*; q=0.01",
            'Accept-Language': "de,en-US;q=0.7,en;q=0.3",
            'X-Requested-With': "XMLHttpRequest",
            'Referer': url,
            # 'Connection':"keep-alive"
        }
        response = requests.get(url, headers=headers)
        time.sleep(1)
        statuscode = response.status_code
        if statuscode == 200:
            data = extract(response.text, proxyFinder)
            IpList = IpList + data

    IpList = list(dict.fromkeys(IpList))
    return IpList


getData()
