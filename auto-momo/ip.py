# encoding:utf-8
import asyncio
from random import choice
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from re import findall, search
from os import environ
from asyncio import run, create_task, wait, Semaphore

listIP = []  # 保存IP地址
validIPs = []  # 保存验证成功的IP地址
global n
n = 0

link = 'link'
if environ.get('GITHUB_RUN_ID', None):
    link = environ['link']

# 随机返回请求头
async def getheaders():
    headers_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36"]
    headers = {'User-Agent': choice(headers_list)}
    return headers


# 生成任务列表
async def taskList(ss):
    task = [
        create_task(get_page('http://www.kxdaili.com/dailiip.html', session=ss)),
        create_task(get_page('https://www.kuaidaili.com/free', mod=2, session=ss)),
        create_task(get_page('https://cdn.jsdelivr.net/gh/parserpp/ip_ports@master/proxyinfo.txt', mod=-1, session=ss)),
        create_task(get_page('https://fastly.jsdelivr.net/gh/parserpp/ip_ports@main/proxyinfo.txt', mod=-1, session=ss)),
        create_task(get_page('https://www.kuaidaili.com/free', mod=2, session=ss)),
        create_task(get_page('https://www.proxy-list.download/api/v1/get?type=http', mod=3, session=ss)),
    ]

    for i in range(1, 4):
        task.append(create_task(get_page(f'http://http.taiyangruanjian.com/free', mod=1, session=ss)))
        task.append(create_task(get_page(f'http://www.kxdaili.com/dailiip.html', session=ss)))
        task.append(create_task(get_page(f'http://www.ip3366.net/free/?stype=1&page={i}', session=ss)))
    return task


# 实例化请求对象
async def create_aiohttp_ip():
    async with ClientSession(connector=TCPConnector(ssl=False)) as session:
        task = await taskList(session)
        await wait(task)


# 访问网页
async def get_page(url, session, mod=0):
    tout = ClientTimeout(total=5)
    hd = await getheaders()
    try:
        async with Semaphore(3):
            async with await session.get(url=url, headers=hd, timeout=tout) as response:
                page_source = await response.text()
                await soup_page(page_source, mod=mod)
    except Exception as e:
        print(f"['{url}']抓取失败:", e)


async def soup_page(source, mod):
    if mod == 0:
        # 通用
        ips = findall(r'<td>[\s]*?(\d+\.\d+\.\d+\.\d+)[\s]*?</td>', source)
        posts = findall(r'<td>[\s]*?(\d{1,5})[\s]*?</td>', source)
        for i in range(len(ips)):
            listIP.append(f"http://{ips[i]}:{posts[i]}")

    elif mod == -1:
        res = source.split('\n')
        for i in range(len(res) - 1):
            listIP.append(f'http://{res[i]}')

    elif mod == 1:
        # 太阳
        ips = findall(r'<div.*?">(\d+\.\d+\.\d+\.\d+)</div>', source)
        posts = findall(r'<div.*?">(\d{1,5})</div>', source)
        for i in range(len(ips)):
            listIP.append(f"http://{ips[i]}:{posts[i]}")

    elif mod == 2:
        # 快代理
        ips = findall(r'<td\s.*?="IP">(\d+\.\d+\.\d+\.\d+)</td>', source)
        posts = findall(r'<td\s.*?="PORT">(\d{1,5})</td>', source)
        for i in range(len(ips)):
            listIP.append(f"http://{ips[i]}:{posts[i]}")

    elif mod == 3:
        # www.proxy-list.download/api/v1/get?type=http
        ip_list = source.split('\r\n')[:-1]
        for i in ip_list:
            listIP.append(f"http://{i}")

    elif mod == 4:
        # 泥马代理
        ip_post = findall(r'<td>(.*?:\d+)</td>', source)
        for i in ip_post:
            listIP.append(f'http://{i}')
    
    elif mod == 7:
        ips = findall(r'<td>(\d+\.\d+\.\d+\.\d+)</td>', source)
        posts = findall(r'<td>(\d{1,5})</td>', source)
        for i in range(len(ips)):
            listIP.append(f'http://{ips[i]}:{posts[i]}')
    elif mod == 8:
        temp = search(r'<div\sstyle=\"padding-left:20px;\">[\s]?(.*?)[\s]?</div>', source)
        pList = temp.group(1).strip().split('<br>')[:-2]
        for p in pList:
            listIP.append(f"http://{p}")


def ip_main():
    run(create_aiohttp_ip())
    global listIP
    listIP = list(set(listIP))  # 代理去重
    print(f"代理ip抓取完成,共{len(listIP)}个可用代理ip地址。")


async def verify_ip(ip):
    try:
        async with ClientSession() as session:
            async with session.get(link, proxy=ip, timeout=ClientTimeout(total=5)) as response:
                if response.status == 200:
                    print(f"代理 {ip} 可用")
                    validIPs.append(ip)
                else:
                    print(f"代理 {ip} 不可用")
    except Exception as e:
        print(f"验证代理 {ip} 失败:", e)


def verify_all_ips():
    run(async_verify_all_ips())
    print(f"共{len(validIPs)}个代理IP验证成功。")
    for ip in validIPs:
        print(f"可用代理IP：{ip}")


async def async_verify_all_ips():
    tasks = [verify_ip(ip) for ip in listIP]
    await wait(tasks)


if __name__ == '__main__':
    ip_main()
    verify_all_ips()
