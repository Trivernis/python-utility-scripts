Python Utilities
=========

Here are some python-scripts that do all kinds of things.

- - -
### setup.py
Installs the dependencies. 
Use `setup.py --help` for more info. The setup.py help is
provided by setuptools.
### riddle.py
Downloads all images from one ore more given subreddits
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