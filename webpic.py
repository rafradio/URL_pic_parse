import requests
import re
import asyncio
import aiohttp
from urllib.parse import urlparse
import os

async def fetchAsync(url):
    img = []
    # http = urlparse(url)
    http = '{uri.scheme}://{uri.hostname}'.format(uri=urlparse(url))
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                pat = re.compile(r'<\s*img [^>]*src="([^"]+)')
                text = b""
                async for data in response.content.iter_chunked(1024):
                    text += data
                decoded_string = text.decode("utf-8", errors='replace')
                img = pat.findall(decoded_string)
                print(img)
                # img = list(filter(lambda x: x.startswith('http'), pat.findall(decoded_string)))
    img1 = list(map(lambda x: x if x.startswith('http') else http + x, img))
    return img1

async def picFile(dirName, url):
    pr = urlparse(url)
    # print(pr.path)
    fileName = os.path.join(dirName, os.path.basename(pr.path))
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                with open(fileName, 'wb') as fd:
                    async for chunk in response.content.iter_chunked(10):
                        fd.write(chunk)

async def arrayOfFiles(dirName, urls):
    tasks = []
    for url in urls:
        task = asyncio.ensure_future(picFile(dirName, url))
        tasks.append(task)
    await asyncio.gather(*tasks)

async def startAsync(dirName, url):
    task1 = asyncio.create_task(fetchAsync(url))
    urlPics = await task1
    # http = urlparse(url)
    task2 = asyncio.create_task(arrayOfFiles(dirName, urlPics))
    await task2

async def startAsyncS(urls):
    tasks = []
    for url in urls:
        pr = urlparse(url)
        dirName = os.path.join(os.getcwd(), pr.hostname)
        os.mkdir(dirName)
        task = asyncio.ensure_future(startAsync(dirName, url))
        tasks.append(task)
    await asyncio.gather(*tasks)
    
if __name__ == '__main__':
    urls = ['https://gb.ru/', 'https://habr.com/ru/all/', 'https://www.google.ru/']
    # urls = ['https://gb.ru/']
    loop = asyncio.get_event_loop()
    loop.run_until_complete(startAsyncS(urls))
    # asyncio.run(startAsyncS(urls))