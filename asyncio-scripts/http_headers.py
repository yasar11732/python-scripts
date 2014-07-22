import asyncio
import urllib.request
import urllib.parse

urls = []
results = []


@asyncio.coroutine
def print_status_code():
    print('couroutine started')
    while True:
        if not urls:
            yield from asyncio.sleep(1)
            continue

        url = urls.pop(0)
        if url is None:
            return

        url = urllib.parse.urlsplit(url)
        
        reader, writer = yield from asyncio.open_connection(url.hostname, 80)

        query = ('GET {url.path} HTTP/1.0\r\n'
                 'Host: {url.hostname}\r\n'
                 '\r\n').format(url=url)

        writer.write(query.encode('latin-1'))
        line = yield from reader.readline()
        code = line.decode('latin1').split()[1]
        results.append((code, url.geturl()))

if __name__ == "__main__":
    from bs4 import BeautifulSoup as bs
    sitemap = urllib.request.urlopen('http://ysar.net/sitemap.xml').read()
    soup = bs(sitemap)
    tasks = []

    num_coroutines = 10

    loop = asyncio.get_event_loop()

    url_q = asyncio.Queue()
    
    for i in range(num_coroutines):  # start 10 tasks
        tasks.append(asyncio.Task(print_status_code()))

    for loc in soup.find_all('loc'):
        urls.append(loc.string)

    for i in range(num_coroutines):  # Put poison pil.
        urls.append(None)
    
    loop.run_until_complete(asyncio.wait(tasks))

    print(results)
