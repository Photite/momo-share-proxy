# encoding:utf-8
from os import environ
from ip import listIP, getheaders, ip_main  # 确保这些函数在ip模块中已正确实现
from asyncio import create_task, wait, Semaphore, run
from aiohttp import ClientSession, ClientTimeout

# 全局变量记录成功访问次数
global n  
n = 0

# 要访问的URL
link = 'link'  

# 如果在GitHub Actions中运行，从环境变量读取URL
if environ.get('GITHUB_RUN_ID', None):
    link = environ['link']

async def create_aiohttp(url, proxy_list):
    """
    使用代理列表创建并运行异步HTTP请求。
    """
    global n
    n = 0
    print(url)
    async with ClientSession() as session:
        # 为每个代理创建任务列表
        tasks = [create_task(web_request(url, proxy, session)) for proxy in proxy_list]
        await wait(tasks)

async def web_request(url, proxy, session):
    """
    使用代理执行网页请求。
    """
    # 信号量限制并发请求数量
    async with Semaphore(5):
        try:
            async with session.get(url=url, headers=await getheaders(), proxy=proxy, 
                                   timeout=ClientTimeout(total=10)) as response:
                # 获取响应文本
                page_source = await response.text()
                await page(page_source)
        except Exception:
            pass

async def page(page_source):
    """
    检查页面是否包含成功访问的标志。
    """
    global n
    if "学习天数" in page_source:
        n += 1

def main():
    """
    运行脚本的主函数。
    """
    ip_main()  # 获取代理
    run(create_aiohttp(link, listIP))
    print(f"墨墨分享链接访问成功{n}次。")

if __name__ == '__main__':
    main()
