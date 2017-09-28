from bs4 import BeautifulSoup
from urllib.parse import urlparse

import requests
import time
import os
import queue

start_page = "https://www.cpe.ku.ac.th"
queue_visit = queue.Queue()
set_page = set()
visited_page = set()
robots = []

PATH = os.path.dirname(os.path.realpath(__file__))


class Crawler:

    def __init__(self, url):
        global visited_page
        try:
            self.url = url
            self.hostname = urlparse(url).netloc
            self.page = requests.get(url, timeout=5).text
            time.sleep(1)
            self.soup = BeautifulSoup(
                self.page, 'html.parser', from_encoding="iso-8859-1")
            self.visited_page = visited_page
        except KeyboardInterrupt:
            exit()
        except:
            pass

    def linkparser(self):
        global queue_visit
        global visited_page
        global set_page
        try:
            for a in self.soup.find_all('a', href=True):
                link = a.get('href')
                if not urlparse(link).netloc and urlparse(link).scheme == '':
                    link = self.url + '/' + link
                if self.check_hostname(link) and link not in visited_page and link not in set_page and link != '#' and (not self.    check_pdf(link)):
                    set_page.add(link)
                    queue_visit.put(link)
            self.visited_page.add(self.url)
            visited_page = visited_page | self.visited_page
        except KeyboardInterrupt:
            exit()
        except:
            pass

    def check_hostname(self, link):
        link_hostname = urlparse(link).netloc
        link_path = urlparse(link).path
        link_query = urlparse(link).query
        if "ku.ac.th" in link_hostname:
            if link_hostname != self.hostname:
                return True
            elif (link_query or len(link_path) > 1):
                return True
            else:
                return False
        else:
            return False

    def get_robot(self, url):
        global robots
        url_parse = urlparse(url)
        host = url_parse.scheme + '://' + url_parse.netloc + '/'
        if not host in robots:
            try:
                res = requests.get(host + 'robots.txt', timeout=5)
                if res.status_code != 404 and res.status_code != 403:
                    robots = res.text
                    robots.append(host)
                    print('Found Robot at ' + host)
            except KeyboardInterrupt:
                exit()
            except:
                pass

    def check_pdf(self, url):
        not_allow = ['.pdf']
        last_path = url[url.rfind('/'):]
        if last_path[last_path.rfind('.'):] in not_allow:
            return True
        else:
            return False


def check_tail(url):
    allow_ext = ['.php', '.html', '.htm']
    last_path = url[url.rfind('/'):]
    if last_path[last_path.rfind('.'):] in allow_ext:
        return True
    else:
        return False


def save_to_file(file_name, data):
    text_file = open(file_name, "w")
    for i in data:
        text_file.write(i + "\n")
        text_file.close()


def make_folder(url_hostname, url_path):
    url_path_folder = url_path.split('/')[1:-1]
    save_path = os.path.join(PATH, 'html', url_hostname, *url_path_folder)
    print(save_path)
    if not os.path.exists(save_path):
        os.makedirs(save_path)


def init_Crawler(url):
    try:
        mycrawler = Crawler(url)
        mycrawler.get_robot(url)
        mycrawler.linkparser()
        if check_tail(url):
            url_path = urlparse(url).path
            url_hostname = urlparse(url).netloc
            paths = url_path.split('/')
            make_folder(url_hostname, url_path)

            # for item in paths:
            #     if item != '':
            #         full_path = full_path + '/' + item
            #     make_folder(path + '/' + full_path)
            html_file = open(url_hostname + '/' + paths[len(paths) - 1], "wb")
            html_file.write(mycrawler.page)
            html_file.close()
            print('Save .html file to folder: ' + url_hostname)
    except KeyboardInterrupt:
        exit()
    except:
        pass


if __name__ == '__main__':
    url_parse = urlparse("http://cpe.ku.ac.th/1/2/3/4.html")
    make_folder(url_parse.netloc, url_parse.path)
    # init_Crawler(start_page)
    # while not queue_visit.empty() and len(visited_page) <= 10000:
    #     print("Queue size:", queue_visit.qsize())
    #     print("Visited Page:", len(visited_page))

    #     url = queue_visit.get()
    #     print('start with url : ' + url)
    #     init_Crawler(url)
    #     print()
    # save_to_file('robots.txt', robots)
    # print('End')
