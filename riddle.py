import urllib.request as urlreq
from typing import List, Dict

from bs4 import BeautifulSoup
import os
import zipfile
import optparse
import asyncio

redditurl: str = 'https://old.reddit.com/r/%s'
dl_dir: str = './.cache/'  # Format must be ./
img_ext: List[str] = ['jpg', 'png', 'bmp']
blacklist: List[str] = ['b.thumbs.redditmedia.com']
hdr: Dict[str, str] = {
    'User-Agent': """Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) 
                     Chrome/23.0.1271.64 Safari/537.11""",
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3', 'Accept-Encoding': 'none', 'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}


async def get_img_as(url):
    req = urlreq.Request(url, headers=hdr)
    html = None
    for x in range(0, 10):
        try:
            html = urlreq.urlopen(req).read()
            break
        except Exception as e:
            print('[-]', e)
            await asyncio.sleep(1)
    soup = BeautifulSoup(html, "lxml")
    ret = []
    for t in soup.find_all(has_source):
        if 'redditmedia' not in t['src']:
            try:
                ret.append(t['src'])
            except KeyError:
                pass
    return ret


async def get_next(url):
    req = urlreq.Request(url, headers=hdr)
    html = None
    for x in range(0, 10):
        try:
            html = urlreq.urlopen(req).read()
            break
        except Exception as e:
            print('[-]', e)
            await asyncio.sleep(1)
    soup = BeautifulSoup(html, "lxml")
    ids = []
    for t in soup.find_all(has_source):
        if 'redditmedia' not in t['src']:
            try:
                fname = t['data-fullname']
                ids.append(fname)
            except KeyError:
                pass
    return [id for id in ids if id][-1]


def has_source(tag):
    if tag.has_attr('src'):
        try:
            return tag['src'].split('.')[-1].lower() in img_ext
        except IndexError or KeyError:
            return False
    elif tag.has_attr('data-url'):
        try:
            tag['src'] = tag['data-url']
            return tag['src'].split('.')[-1].lower() in img_ext
        except KeyError or KeyError:
            return False
    else:
        return False


async def download_async(url, zfile=None):
    images = await get_img_as(url)
    print('[+] Found %s images' % len(images))
    for img in images:
        try:
            if 'http' not in img.split('/')[0] and '//' not in img.split('.')[0]:
                img = url + img
            if 'http' not in img.split('/')[0]:
                img = 'http:' + img
            if img.strip('http://').strip('https://').split('/')[0] in blacklist:
                img = None
                continue
            name = dl_dir + img.split('/')[-1]
            if os.path.isfile(name):
                continue
            f = open(name, "wb")
            req = urlreq.Request(img, headers=hdr)
            image = urlreq.urlopen(req)
            f.write(image.read())
            f.close()
            zfile.write(name, compress_type=zipfile.ZIP_DEFLATED)
            try:
                os.remove(name)
            except FileNotFoundError or PermissionError:
                pass
            print('[+] Saved Image %s from %s' % (img, url))
            await asyncio.sleep(0.25)
        except Exception as error:
            print('[-] Failed with %s' % img)
    print('[+] Finished %s' % url)


async def dl_loop(section, zfile, loop, chaos=False):
    baseurl = redditurl % section
    url = baseurl
    if chaos:
        loop.create_task(download_async(url, zfile))
    else:
        await loop.create_task(download_async(url, zfile))
    while True:
        print('[*] Getting Images from %s' % url)
        try:
            after = await get_next(url)
            url = '{}/?after={}'.format(baseurl, after)
            if chaos:
                loop.create_task(download_async(url, zfile))
            else:
                await loop.create_task(download_async(url, zfile))
        except Exception as ex:
            print('[-]', ex)
            zfile.close()
            break
        finally:
            await asyncio.sleep(0.1)


def main(sections, chaos=False):
    if not os.path.exists(dl_dir):
        os.makedirs(dl_dir)
    zfiles = {}
    for sect in sections:
        mode = 'w'
        if os.path.isfile(sect + '.zip'):
            mode = 'a'
        zfiles[sect] = zipfile.ZipFile('%s.zip' % sect, mode)
    loop = asyncio.get_event_loop()
    try:
        for sect in sections:
            if chaos:
                loop.call_soon(loop.create_task(
                    dl_loop(sect, zfiles[sect], loop, chaos=True)))
            else:
                loop.call_soon(loop.create_task(
                    dl_loop(sect, zfiles[sect], loop)))
        loop.run_forever()
    except KeyboardInterrupt:
        loop.stop()
        for sect in sections:
            try:
                zfiles[sect].close()
            except Exception as error:
                print(error)


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-c', '--chaos', dest='chaos',
                      action='store_true', default=False)
    options, sects = parser.parse_args()
    main(sects, chaos=options.chaos)
