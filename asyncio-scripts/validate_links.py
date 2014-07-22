import asyncio
from html.parser import HTMLParser
import urllib.parse
from queue import Queue

class LinkGather(HTMLParser):
    """
    Simple http parser to get resources out of an html page
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.encoding='latin1'
        self.links=[]
    
    def handle_starttag(self, tag, attrs):
        if tag=='meta':  ## try to get meta charset for correct decoding
            for k,v in attrs:
                if k == 'charset':
                    self.encoding=v
            
        for k,v in attrs:
            if k in ('src', 'href'):
                self.links.append(v)
                break

    def feed_raw(self, bytess):
        "Feed raw bytes, so it can be handled with correct encoding."
        self.feed(bytess.decode(self.encoding))       
        
class RecursiveStatusChecker(object):
    "This class recursively visits links from a internet location and gathers http status codes."
    
    def __init__(self, url):
        self.results = []
        self._visited = set((url,))
        
        self._tasks =  [asyncio.Task(self.recursive_fetch(url))]
        self.errors = []

    def run(self):
        "Run tasks until all of them are completed"
        loop = asyncio.get_event_loop()

        while True:
            try:
                loop.run_until_complete(self._tasks.pop())
            except IndexError:
                break
        

    @asyncio.coroutine
    def recursive_fetch(self,
                        start_url,  # where to begin fetching
                        parent=None,# who links to this page
                        ):
        "Fetch a page. If this page is html page, create new tasks for new links"

        print("fetching", start_url)
        
        parser = LinkGather()
        url = urllib.parse.urlsplit(start_url)

        try:
            r, w = yield from asyncio.open_connection(url.hostname, 80)
        except Exception as err:
            self.errors.append((start_url, err))
            return

        query = ('GET {p} HTTP/1.0\r\n'
                 'Host: {hn}\r\n'
                 'Accept:*/*\r\n'
                 '\r\n'.format(p=urllib.parse.quote(url.path), hn=url.hostname))

        w.write(query.encode('latin-1'))
        try:
            line = yield from r.readline()
        except Exception as err:
            self.erros.append((start_url, err))
            return

        line = line.decode('latin1')  ## normally, it is something like -- HTTP/1.0 200 OK

        if not line.startswith('HTTP'):
            self.errors.append((start_url, Exception("Unexpected http response: %s" % line)))
            return

        code = line.split()[1]
            
        headers = {}
        while True: # parse headers
            try:
                line = yield from r.readline()
            except Exception as err:
                self.erros.append((start_url, err))
                return

            line = line.decode('latin1')
            
            if line == "\r\n":
                break

            k,*v = line.split(":")
            headers[k.strip().lower()] = ":".join(v).strip().lower()

        ct = ""
        if 'content-type' in headers:
            ct = headers['content-type']
            if ";" in ct:
                ct, cs = headers['content-type'].split(";")
                cs = cs.split("=")[1].strip()
                parser.encoding = cs  # if we get a charset from http headers, set parser's encoding accordingly

        self.results.append((code, parent, start_url))

        if ct == 'text/html':
            while True:
                line = yield from r.readline()
                if not line:
                    break
                parser.feed_raw(line)
            
            for link in parser.links:
                full_link = urllib.parse.urljoin(url.geturl(), link)
                if full_link.startswith('mailto:'):
                    continue

                full_link_parts = urllib.parse.urlsplit(full_link)
                normalized_link = urllib.parse.urlunparse((full_link_parts.scheme, full_link_parts.netloc, full_link_parts.path, '', '', '')) 
                
                if full_link_parts.netloc == url.netloc and not normalized_link in self._visited:
                    self._visited.add(normalized_link)
                    self._tasks.append(asyncio.Task(self.recursive_fetch(normalized_link, start_url)))

if __name__ == "__main__":
    
    rsc = RecursiveStatusChecker('http://ysar.net/')
    rsc.run()

    import csv

    with open('fetch-results.csv', 'w', newline='') as f:
        result_writer = csv.writer(f)

        for result in rsc.results:
            result_writer.writerow(result)
