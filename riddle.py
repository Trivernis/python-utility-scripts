import urllib.request as urlreq
from typing import List, Dict

from bs4 import BeautifulSoup
import os
import zipfile
import optparse
import asyncio
import shutil

redditurl: str = 'https://old.reddit.com/r/%s'
dl_dir: str = './.cache/'  # Format must be ./
img_ext: List[str] = ['jpg', 'png', 'bmp']
blacklist: List[str] = ['b.thumbs.redditmedia.com', 'reddit.com']
hdr: Dict[str, str] = {
    'User-Agent': """Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) 
                     Chrome/23.0.1271.64 Safari/537.11""",
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3', 'Accept-Encoding': 'none', 'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}


def print_progress(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    # Print New Line on Complete
    if iteration == total:
        print()


async def request_soup(url):
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
    return soup


async def get_img_as(url):
    soup = await  request_soup(url)
    ret = []
    for t in soup.find_all(has_source):
        if 'redditmedia' not in t['src']:
            try:
                ret.append(t['src'])
            except KeyError:
                pass
    return ret


async def get_next(url):
    ids = []
    soup = await request_soup(url)
    for t in soup.find_all(has_source):
        if 'redditmedia' not in t['src']:
            try:
                fname = t['data-fullname']
                ids.append(fname)
            except KeyError:
                pass
    return [_id for _id in ids if _id][-1]


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


async def download_async(url, zfile=None, test=False):
    images = await get_img_as(url)
    print('[+] Found %s images' % len(images))
    logmsg = ""
    imgcount = len(images)
    savedcount = 0
    count = 0
    print_progress(count, imgcount, prefix="Downloading: ", suffix="Complete")
    for img in images:
        print_progress(count+1, imgcount, prefix="Downloading: ", suffix="Complete")
        count+=1
        if test:
            continue
        try:
            if 'http' not in img.split('/')[0] and '//' not in img.split('.')[0]:
                img = url + img
            if 'http' not in img.split('/')[0]:
                img = 'http:' + img
            if img.strip('http://').strip('https://').split('/')[0] in blacklist:
                img = None
                continue
            imgname = img.split('/')[-1]
            name = dl_dir + imgname
            if os.path.isfile(name):
                continue
            f = open(name, "wb")
            req = urlreq.Request(img, headers=hdr)
            image = urlreq.urlopen(req)
            f.write(image.read())
            f.close()
            zfile.write(name, imgname, zipfile.ZIP_DEFLATED)
            try:
                os.remove(name)
            except FileNotFoundError or PermissionError:
                pass
            savedcount += 1
            await asyncio.sleep(0.25)
        except Exception as error:
            logmsg += '[-] Failed with %s %s\n' % (img, error)
    print('[+] %s images downloaded | %s finished %s' % (savedcount, logmsg, url))


async def dl_loop(section, zfile, loop, chaos=False, test=False):
    baseurl = redditurl % section
    url = baseurl
    if chaos:
        loop.create_task(download_async(url, zfile, test))
    else:
        await loop.create_task(download_async(url, zfile, test))
    while True:
        print('[*] Getting Images from %s' % url)
        try:
            after = await get_next(url)
            url = '{}/?after={}'.format(baseurl, after)
            if chaos:
                loop.create_task(download_async(url, zfile, test))
            else:
                await loop.create_task(download_async(url, zfile, test))
        except Exception as ex:
            print('[-]', ex)
            zfile.close()
            break
        finally:
            await asyncio.sleep(0.1)


def main(sections, opts):
    chaos = opts.chaos
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
                loop.create_task(loop.create_task(
                    dl_loop(sect, zfiles[sect], loop, chaos=True, test=opts.test)))
            else:
                loop.run_until_complete(loop.create_task(
                    dl_loop(sect, zfiles[sect], loop, test=opts.test)))
        if chaos:
            loop.run_forever()
    except KeyboardInterrupt:
        for sect in sections:
            try:
                zfiles[sect].close()
            except Exception as error:
                print(error)
    finally:
        shutil.rmtree(dl_dir)


if __name__ == '__main__':
    parser = optparse.OptionParser(usage="usage: %prog [options] [subreddits]")
    parser.add_option('-c', '--chaos', dest='chaos',
                      action='store_true', default=False,
                      help=""" Doesn't wait for previous downloads to finish and doesn't exit when no more
                      images can be found. Do only activate this if you want to download a lot of images
                      from multiple subreddits at the same time. Only option to exit is CTRL + C.""")
    parser.add_option('-t', '--test', dest='test',
                      action='store_true', default=False,
                      help='Tests the functions of the script')
    options, sects = parser.parse_args()
    print('[~] Recieved subreddits %s' % ', '.join(sects))
    main(sects, opts=options)
