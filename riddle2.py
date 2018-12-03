import zipfile
import time
import os
import sys
import optparse
import shutil

from lib import cutils, netutils, fsutils

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


def has_source(tag: netutils.BeautifulSoup) -> bool:
    if tag.has_attr('src'):
        try:
            return fsutils.get_extension(tag['src']) in img_ext
        except IndexError or KeyError:
            return False
    elif tag.has_attr('data-url'):
        try:
            tag['src'] = tag['data-url']
            return fsutils.get_extension(tag['src']) in img_ext
        except IndexError or KeyError:
            return False
    else:
        return False


def get_next_url(baseurl: str, url: str):
    ids = []
    soup = netutils.get_soup4url(url, headers=hdr)
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
    if len(ids) == 0:  # if no id was found, we can't get any further into the past
        return None
    _id = ids[-1]
    next_url = '{}/?after={}'.format(baseurl, _id)
    return next_url


def get_img4site(url: str) -> list:
    soup = netutils.get_soup4url(url, headers=hdr)
    if not soup:
        return []
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


def get_img4sub(url: str, length: int =-1) -> list:
    baseurl = url
    imgs = []
    print('[~] 1/2 Getting images...')
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
    print()
    print('[+] Found %s images' % len(imgs))
    return imgs


def download_images(imgs: list, zfile: zipfile.ZipFile):
    imgcount = len(imgs)
    fnames = [zinfo.filename for zinfo in zfile.infolist()]
    print('[~] 2/2 Downloading %s images' % imgcount)
    pb = cutils.ProgressBar(total=imgcount, prefix="[~] 2/2 Downloadinng", suffix="Complete")
    fsutils.dir_exist_guarantee(dl_dir)
    for img in imgs:
        pb.tick()
        imgname = img.split('/')[-1]
        name = os.path.join(dl_dir, imgname)
        if os.path.isfile(name) or imgname in fnames:
            continue
        netutils.download_file(img, name, headers=hdr)
        zfile.write(name, imgname, zipfile.ZIP_DEFLATED)
        try:
            os.remove(name)
        except FileNotFoundError or PermissionError:
            pass
        time.sleep(0.1)  # no don't penetrate
    added = len(zfile.infolist()) - len(fnames)
    print('[+] Added %s files to the zipfile' % added)


def download_subreddit(sub: str, count: int =-1, out: str =None):
    mode = 'w'
    zname = sub + '.zip'
    if out:
        zname = out
    if os.path.isfile(zname):
        mode = 'a'
    url = 'https://old.reddit.com/r/%s/' % sub
    imgs = get_img4sub(url, length=count)
    zfile = zipfile.ZipFile(zname, mode)
    download_images(imgs, zfile)
    zfile.close()


def cleanup():
    print('[~] Cleanup...')
    if os.path.isdir(dl_dir):
        shutil.rmtree(dl_dir)


def parser_init():
    parser = optparse.OptionParser(usage="usage: %prog [options] [subreddits]")
    parser.add_option('-c', '--count', dest='count',
                      type='int', default=-1,
                      help='The number of images to download.')
    parser.add_option('-o', '--output', dest='output',
                      type='str', default=None,
                      help='The name of the output zipfile. If none is specified, it\'s the subreddits name.')
    parser.add_option('-t', '--test', dest='test',
                      action='store_true', default=False,
                      help='Tests the functions of the script')
    parser.add_option('-l', '--loop', dest='loop',
                      action='store_true', default=False,
                      help="""Continuing download loop. When this option is set every 5 Minutes the program searches for
                      new images""")
    return parser.parse_args()


def download_subreddits(subreddits, count, output):
    for sub in subreddits:
        print('[~] Downloading %s' % sub)
        download_subreddit(sub, count=count, out=output)
        print()


def main():
    options, subreddits = parser_init()
    count = options.count
    output = options.output
    if options.test:
        count = 1
        subreddits = ['python']
        output = 'test.zip'
    if options.loop:
        while True:
            download_subreddits(subreddits, count, output)
            print('[~] Next Download in 5 minues...')
            time.sleep(300)
    else:
        download_subreddits(subreddits, count, output)
    cleanup()
    if options.test:
        os.remove(output)
    if len(errors.keys()) > 0:
        print('[-] Following errors occured:')
        for key in errors.keys():
            print('    %s times: %s' % (errors[key], key))


if __name__ == '__main__':
    main()
