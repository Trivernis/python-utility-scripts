# encoding=utf-8
import urllib.request as urlreq
from bs4 import BeautifulSoup

import zipfile
import time
import os
import sys
import optparse
import shutil

blacklist = ['b.thumbs.redditmedia.com', 'reddit.com']
dl_dir = './.cache/'
img_ext = ['jpg', 'jpeg', 'png']    # define the urls we are searching for
hdr = {                             # request header
    'User-Agent': """Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) 
                     Chrome/23.0.1271.64 Safari/537.11""",
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3', 'Accept-Encoding': 'none', 'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}
errors = {}


def print_progress(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    # Print New Line on Complete
    if iteration == total:
        print()


def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor


def get_extension(fstring):
    return fstring.split('.')[-1].lower()


def get_soup4url(url):
    """ Returns a soup for the url with 10 retrys """
    req = urlreq.Request(url, headers=hdr)
    html = None
    for x in range(0, 10):
        try:
            html = urlreq.urlopen(req).read()
            break
        except Exception as e:
            if errors[e]:
                errors[e] += 1
            else:
                errors[e] = 1
    if html:
        soup = BeautifulSoup(html, "lxml")
        return soup
    return False


def has_source(tag):
    if tag.has_attr('src'):
        try:
            return get_extension(tag['src']) in img_ext
        except IndexError or KeyError:
            return False
    elif tag.has_attr('data-url'):
        try:
            tag['src'] = tag['data-url']
            return get_extension(tag['src']) in img_ext
        except IndexError or KeyError:
            return False
    else:
        return False


def get_next_url(baseurl, url):
    ids = []
    soup = get_soup4url(url)
    if not soup:
        return False
    for t in soup.find_all(has_source):
        if 'redditmedia' not in t['src']:
            try:
                fname = t['data-fullname']
                ids.append(fname)
            except KeyError:
                pass
    ids = [_id for _id in ids if _id]
    if len(ids) == 0:
        return False
    _id = ids[-1]
    next_url = '{}/?after={}'.format(baseurl, _id)
    return next_url


def get_img4site(url):
    soup = get_soup4url(url)
    if not soup:
        return False
    ret = []
    sys.stdout.write('.')
    sys.stdout.flush()
    for t in soup.find_all(has_source):
        try:
            if 'redditmedia' not in t['src'] and 'icon' not in t['src']:
                img = t['src']
                if 'http' not in img.split('/')[0] and '//' not in img.split('.')[0]:
                    img = url + img
                if 'http' not in img.split('/')[0]:
                    img = 'http:' + img
                if img.strip('http://').strip('https://').split('/')[0] in blacklist:
                    img = None
                if img:
                    ret.append(img)
        except KeyError:
            pass
    return ret


def get_img4sub(url, length=-1):
    baseurl = url
    imgs = []
    print('[ ] 1/2 Getting images...')
    if length >= 0:
        x = 0
        while x < length:
            time.sleep(0.1)  # we don't want to flood with requests
            imgurls = get_img4site(url)
            if not imgurls:
                break
            imgs.extend(imgurls)
            x = len(imgs)
            url = get_next_url(baseurl, url)
            if not url:
                break
            sys.stdout.write('\b')
        imgs = imgs[:length]
    else:
        while url:
            time.sleep(0.1)  # we don't want to flood with requests
            imgurls = get_img4site(url)
            if not imgurls:
                break
            imgs.extend(imgurls)
            url = get_next_url(baseurl, url)
    print('[+] Found %s images' % len(imgs))
    return imgs


def download_images(imgs, zfile):
    count = 1
    imgcount = len(imgs)
    fnames = [zinfo.filename for zinfo in zfile.infolist()]
    print('[ ] Downloading %s images' % imgcount)
    if not os.path.isdir(dl_dir):
        os.mkdir(dl_dir)
    for img in imgs:
        print_progress(count, imgcount, prefix="2/2 Downloading: ", suffix="Complete")
        imgname = img.split('/')[-1]
        name = dl_dir + imgname
        if os.path.isfile(name) or imgname in fnames:
            count += 1
            continue
        f = open(name, "wb")
        req = urlreq.Request(img, headers=hdr)
        try:
            image = urlreq.urlopen(req)
        except ConnectionError:
            print('\n [-] Connection Error')
            return
        f.write(image.read())
        f.close()
        zfile.write(name, imgname, zipfile.ZIP_DEFLATED)
        try:
            os.remove(name)
        except FileNotFoundError or PermissionError:
            pass
        time.sleep(0.1)  # no don't penetrate
        count += 1
    added = len(zfile.infolist()) - len(fnames)
    print('[+] Added %s files to the zipfile' % added)


def download_subreddit(sub, count=-1):
    mode = 'w'
    if os.path.isfile(sub + '.zip'):
        mode = 'a'
    url = 'https://old.reddit.com/r/%s/' % sub
    imgs = get_img4sub(url, length=count)
    zfile = zipfile.ZipFile('%s.zip' % sub, mode)
    download_images(imgs, zfile)
    zfile.close()


def cleanup():
    print('[ ] Cleanup...')
    if os.path.isdir(dl_dir):
        shutil.rmtree(dl_dir)


def parser_init():
    parser = optparse.OptionParser(usage="usage: %prog [options] [subreddits]")
    parser.add_option('-c', '--count', dest='count',
                      type='int', default=-1,
                      help='The number of images to download.')
    parser.add_option('-t', '--test', dest='test',
                      action='store_true', default=False,
                      help='Tests the functions of the script')
    return parser.parse_args()


def main():
    options, subreddits = parser_init()
    if options.count:
        count = options.count
    else:
        count = -1
    if options.test:
        count = 1
        subreddits = ['python']
    for sub in subreddits:
        print('[ ] Downloading %s' % sub)
        download_subreddit(sub, count=count)
    cleanup()
    print(errors)


if __name__ == '__main__':
    main()
