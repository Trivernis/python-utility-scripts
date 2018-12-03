import os
import optparse

from lib import miscutils, fsutils

sources = {}


def optparse_init() -> tuple:
    parser = optparse.OptionParser()
    parser.add_option('-f', '--file', type='string', dest='s_file', help='Searching lines in the given file.')
    parser.add_option('-d', '--directory', type='string', dest='s_dir', help='Searching files in a directory.')
    parser.add_option('-q', '--query', type='string', dest='query', help='The search term. Supporting "".')
    parser.add_option('-l', '--loop', action='store_true', default=False, dest='loop', help="""Runs the program in
    an endless loop.""")
    return parser.parse_args()


def read_file_source(fname):
    finfo = fsutils.FileInfo(fname)
    if finfo.exist:
        with finfo.open('r') as f:
            return list(f.readlines())


def read_directory_source(dirname):
    """ Reading the contents of the directory """
    dinfo = fsutils.DirInfo(dirname)
    if dinfo.exist:
        return dinfo.get_full_content()


def main():
    options, args = optparse_init()
    engines = []

    if options.s_file:
        e_file = miscutils.SearchEngine(read_file_source(options.s_file))
        engines.append(e_file)

    if options.s_dir:
        e_dir = miscutils.SearchEngine(read_directory_source(options.s_dir))
        engines.append(e_dir)

    while True:
        if options.query and not options.loop:
            query = options.query
        else:
            query = input('Search: ')

        for engine in engines:
            for res in engine.search(query):
                print(res)
            print('- - - - -')
        if not options.loop:
            break


if __name__ == '__main__':
    main()
