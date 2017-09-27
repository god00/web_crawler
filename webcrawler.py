from bs4 import BeautifulSoup
from urllib.parse import urlparse

import requests
import time
import urllib.request
import os.path
import queue

start_page = "https://www.cpe.ku.ac.th"
queue_visit = queue.Queue()
set_page = set()
visited_page = set()
robots = []

path = os.path.dirname(os.path.realpath(__file__))
path = os.path.split(path)[0]

class Crawler:

    def __init__(self,url):
        global visited_page
        self.url = url
        self.hostname = urlparse(url).netloc
        self.page = requests.get(url).content
        time.sleep(1)
        self.soup = BeautifulSoup(self.page, 'html.parser', from_encoding="iso-8859-1")
        self.visited_page = visited_page

    def linkparser(self):
        global queue_visit
        global visited_page
        global set_page
        for a in self.soup.find_all('a', href=True):
            link = a.get('href')
            if self.check_hostname(link) and link not in visited_page and link not in set_page and link != '#':
                set_page.add(link)
                queue_visit.put(link)
        self.visited_page.add(self.url)
        visited_page = visited_page | self.visited_page

    def check_hostname(self,link):
        link_hostname = urlparse(link).netloc
        link_path = urlparse(link).path
        link_query = urlparse(link).query
        return (self.hostname == link_hostname) and (link_query or len(link_path)>1) and ("ku.ac.th" in link_hostname)

    def get_robot(self,url):
        global robots
        url_parse = urlparse(url)
        host = url_parse.scheme + '://' + url_parse.netloc + '/'
        if not host in robots:
            try:
                res = requests.get(host + 'robots.txt', timeout = 1)
                if res.status_code != 404 and res.status_code != 403:
                    robots = res.text
                    robots.append(host)
                    print['Found Robot at ' + host ]
            except KeyboardInterrupt:
                exit()
            except:
                pass


def check_tail(url):
    allow_ext = ['.php','.html', '.htm']
    last_path = url[url.rfind('/'):]
    if last_path == '/' or last_path[last_path.rfind('.'):] in allow_ext:
        print(url)
        return True
    else:
        return False

def save_to_file(self,file_name, data):
    text_file = open(file_name, "w")
    for i in data:
        text_file.write(i+"\n")
        text_file.close()


def make_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)


def do_in_queqe():
    global queue_visit
    global visited_page
    print(queue_visit.qsize())
    print(len(visited_page))
    if not queue_visit.empty() and len(visited_page) <= 10000:
        url = queue_visit.get()
        print('start with url : ' + url)
        init_Crawler(url)
        do_in_queqe()

def init_Crawler(url):
    global path
    mycrawler = Crawler(url)
    mycrawler.get_robot(url)
    mycrawler.linkparser()
    if check_tail(url):
        url_path = urlparse(url).path
        paths = url_path.split('/')
        for item in paths:
            make_folder(path + '/' + item)
        html_file = open(path + '/' + url_path, "w")
        html_file.write(mycrawler.page)
        html_file.close()


if __name__ == '__main__':
    init_Crawler(start_page)
    do_in_queqe()
    save_to_file(path,robots)
    print('End')