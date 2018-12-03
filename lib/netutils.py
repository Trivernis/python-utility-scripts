import urllib.request as urlreq
import time

from bs4 import BeautifulSoup

from lib import logutils

logger = logutils.get_logger('netutils')


def get_soup4url(url: str, retrys: int =2, headers: dict=urlreq.noheaders(), timeout: int =30) -> BeautifulSoup:
    """ Returns a soup for the url """
    req = urlreq.Request(url, headers=headers)
    html = None
    for _ in range(0, retrys+1):
        try:
            html = urlreq.urlopen(req, timeout=timeout).read()
            break
        except Exception as e:
            logger.exception(e)
            time.sleep(1)  # to avoid request flooding
    if html:
        soup = BeautifulSoup(html, "lxml")
        return soup
    return False


def download_file(url: str, dest: str, headers: dict=urlreq.noheaders()):
    f = open(dest, "wb")
    req = urlreq.Request(url, headers=headers)
    try:
        image = urlreq.urlopen(req)
    except ConnectionError:
        print('\n [-] Connection Error')
        return
    f.write(image.read())
    f.close()
