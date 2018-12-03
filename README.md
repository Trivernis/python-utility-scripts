Python Utilities
=========

Here are some python-scripts that do all kinds of things.

## Setup
Install all dependencies with
```commandline
pip install -r requirements.txt
```

## Scripts

### riddle.py
Downloads all images from one or more given subreddits
```commandline
Usage: riddle.py [options] [subreddits]

Options:
  -h, --help   show this help message and exit
  -c, --chaos                         Doesn't wait for previous downloads to
               finish and doesn't exit when no more
               images can be found. Do only activate this if you want to
               download a lot of images                       from multiple
               subreddits at the same time.
```

## riddle2.py
Downloads all images from one  or more given subreddits in a more predictable
 way than riddle.py.
```commandline
Usage: riddle2.py [options] [subreddits]

Options:
  -h, --help            show this help message and exit
  -c COUNT, --count=COUNT
                        The number of images to download.
  -o OUTPUT, --output=OUTPUT
                        The name of the output zipfile. If none is specified,
                        it's the subreddits name.
  -t, --test            Tests the functions of the script
  -l, --loop            Continuing download loop. When this option is set
                        every 5 Minutes the program searches for
                        new images
```