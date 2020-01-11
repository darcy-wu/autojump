#!/usr/bin/env python3
# write by darcy.wu

__version__ = 0.1
__all__ = ["jump"]

import sys
import os
import re
import locale

import logging
#from colorlog import ColoredFormatter

from optparse import OptionParser
import percol
from percol import Percol
from percol import tty
from percol import ansi
from percol.action import action

#selected_str = [os.environ["HOME"]]
selected_str = []

@action()
def get_selected_string(lines, percol):
    global selected_str
    for line in lines:
        selected_str.append(line)

log_level = logging.DEBUG
logging.root.setLevel(log_level)
#formatter = ColoredFormatter('[%(log_color)s%(levelname)s%(reset)s] %(log_color)s%(message)s%(reset)s')
stream = logging.StreamHandler()
stream.setLevel(log_level)
#stream.setFormatter(formatter)

logger = logging.getLogger('autojump')
logger.setLevel(log_level)
logger.addHandler(stream)


def cli_query(query, candidates):
    # get ttyname
    ttyname = tty.get_ttyname()
    if not ttyname:
        logger.critical("""No tty name is given and failed to guess it from descriptors.  Maybe all descriptors are redirected.""")
        sys.exit(1)

    # decide which encoding to use
    locale.setlocale(locale.LC_ALL, '')
    output_encoding = locale.getpreferredencoding()

    with open(ttyname, "wb+", buffering=0) as tty_f:
        if not tty_f.isatty():
            logger.critical("{0} is not a tty file".format(ttyname))
            sys.exit(2)

        # setup actions
        acts = (get_selected_string, get_selected_string)

        # arrange finder class
        from percol.finder import FinderMultiQueryString
        candidate_finder_class = action_finder_class = FinderMultiQueryString

        with Percol(descriptors = tty.reconnect_descriptors(tty_f),
                    candidates = candidates,
                    actions = acts,
                    finder = candidate_finder_class,
                    action_finder = action_finder_class,
                    query = query,
                    encoding = output_encoding) as percol:
            # finder settings from option values
            percol.model_candidate.finder.lazy_finding = True
            percol.model_candidate.finder.case_insensitive = True
            percol.model_candidate.finder.invert_match = False
            # enter main loop
            exit_code = percol.loop()
    if exit_code:
        logger.error('Query Canceled!')
        sys.exit(exit_code)

    if selected_str:
        return selected_str
    else:
        return ['']

def setup_options(parser):
    parser.add_option("--add", dest = "add", action = "store_true", default = False,
                      help = "add new dir")
    parser.add_option("--clean", dest = "clean", action = "store_true", default = False,
                      help = "clean invalid dir")
    parser.add_option("--jump-file", dest = "jumpfile",
                      help = "jump file")
    #parser.add_option("--query", dest = "query",
    #                  help = "pre-input query")
    #parser.add_option("--auto-fail", dest = "auto_fail", default = False, action="store_true",
    #                  help = "auto fail if no candidates")
    #parser.add_option("--auto-match", dest = "auto_match", default = False, action="store_true",
    #                  help = "auto matching if only one candidate")

def read_record(filename):
    path_record = {}
    with open(filename) as fd:
        for line in fd:
            (count, line) = get_path(line)
            path_record[line] = count
        fd.close()
    return path_record

def read_input(filename):
    stream = open(filename, "r")
    i = 0
    for line in stream:
        i += 1
        (count, line) = get_path(line)
        yield ansi.remove_escapes("%03d -> %s" % (i, line.rstrip("\r\n")))
    stream.close()

def get_path(line):
    lt = line.split()
    if len(lt) == 1:
        return (1, lt[0])
    else:
        return (int(lt[0]), lt[1])

def write_back(file, record):
    lines = ['%d %s\n' % (v, k) for (k,v) in record.items()]
    lines.sort(reverse=True)
    with open(file, 'w') as fd:
        fd.writelines(lines)
        fd.close()

def main():
    parser = OptionParser(usage = "Usage: %prog [options] [FILE]", version = "%prog {0}".format(__version__))
    setup_options(parser)
    options, args = parser.parse_args()

    if not os.path.exists(os.environ['HOME'] + '/.autojump/jump.list'):
        os.system('mkdir ~/.autojump -p; touch ~/.autojump/jump.list')

    jumplist = os.environ['HOME'] + '/.autojump/jump.list'

    if options.add:
        with open(jumplist, 'r') as fd:
            lines = fd.readlines()
            fd.close()
        l = args[0] + '\n'
        get = 0
        for line in lines:
            if re.search(r' %s$' % l, line):
                get = 1
                break
        if get == 0:
            with open(jumplist, 'a') as fd:
                fd.write('1 ' + l)
                fd.close()
    elif options.clean:
        with open(jumplist, 'r') as fd:
            lines = fd.readlines()
            fd.close()
        newlines = []
        for l in lines:
            (count, path) = get_path(l)
            if os.path.exists(path) and count >= 1:
                #newlines.append(str(count) + ' ' + path)
                newlines.append(l)
        with open(jumplist, 'w') as fd:
            fd.writelines(newlines)
            fd.close()
        logger.info('total path: %d. clean path: %d' % (len(lines), len(lines) - len(newlines)))
    else:
        filename = jumplist

        if filename and not os.access(filename, os.R_OK):
            logger.critical("Cannot read a file '" + filename + "'")
            sys.exit(1)

        try:
            candidates = read_input(filename)
        except KeyboardInterrupt:
            logger.critical("Canceled")
            sys.exit(1)

        #select = cli_query(options.query, candidates)[0]
        t = cli_query(' '.join(args), candidates)[0]
        if t:
            select = t.split(' -> ')[1]
            path_record = read_record(filename)
            path_record[select] += 1
            write_back(filename, path_record)
            sys.stdout.write(select)
        else:
            sys.stdout.write(os.getcwd())


if __name__ == '__main__':
    main()

