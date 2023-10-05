import re
import asyncio
import aiohttp
from urllib.parse import urlparse
import sys, os, shutil, time

async def parseURL(url):
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
                # print(img)

    img1 = list(map(lambda x: x if x.startswith('http') else http + x, img))
    return img1

async def picFile(dirName, url):
    pr = urlparse(url)
    fileName = os.path.join(dirName, os.path.basename(pr.path))
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                with open(fileName, 'wb') as fd:
                    async for chunk in response.content.iter_chunked(10):
                        fd.write(chunk)

async def arrayOfPicURLs(dirName, urls, start_time):
    tasks = []
    for url in urls:
        task = asyncio.ensure_future(picFile(dirName, url))
        tasks.append(task)
    await asyncio.gather(*tasks)
    print(f"Downloaded {dirName} in {time.time() - start_time:.2f} seconds")

async def startPArseUrlAndPics(dirName, url):
    start_time = time.time()
    task1 = asyncio.create_task(parseURL(url))
    urlPics = await task1
    task2 = asyncio.create_task(arrayOfPicURLs(dirName, urlPics, start_time))
    await task2

async def startAsync(urls):
    tasks = []
    for url in urls:
        pr = urlparse(url)
        dirName = os.path.join(os.getcwd(), pr.hostname)
        if os.path.exists(dirName):
            shutil.rmtree(dirName)
            os.mkdir(dirName)
        else:
            os.mkdir(dirName)
        task = asyncio.ensure_future(startPArseUrlAndPics(dirName, url))
        tasks.append(task)
    await asyncio.gather(*tasks)
    
if __name__ == '__main__':
    initialData = sys.argv
    defaultData = ['https://gb.ru/', 'https://habr.com/ru/all/', 'https://www.google.ru/']
    urls = initialData[1:] if len(initialData) > 1 else defaultData
    loop = asyncio.get_event_loop()
    loop.run_until_complete(startAsync(urls))
    # asyncio.run(startAsync(urls))