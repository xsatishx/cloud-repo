from .log import get_logger

from contextlib import contextmanager
from progressbar import ProgressBar, Percentage, Bar, ETA, FileTransferSpeed
import hashlib
import mmap
import os
import requests
import stat

# Logging
log = get_logger('utils')

# Silence warnings from requests
try:
    requests.packages.urllib3.disable_warnings()
except Exception as e:
    log.info('Unable to silence requests warnings: {}'.format(str(e)))


def check_transfer_size(actual, expected):
    """Simple validation on any expected versus actual sizes.

    :param int actual: The size that was actually transferred
    :param int actual: The size that was expected to be transferred

    """

    return actual == expected


def get_pbar(file_id, maxval, start_val=0):
    """Create and initialize a custom progressbar

    :param str title: The text of the progress bar
    "param int maxva': The maximumum value of the progress bar

    """
    title = 'Downloading {}: '.format(file_id)
    pbar = ProgressBar(widgets=[
        title, Percentage(), ' ',
        Bar(marker='#', left='[', right=']'), ' ',
        ETA(), ' ', FileTransferSpeed(), ' '], maxval=maxval)
    pbar.currval = start_val
    pbar.start()
    return pbar


def print_opening_header(file_id):
    log.info('')
    log.info('v{}v'.format('{s:{c}^{n}}'.format(
        s=' {} '.format(file_id), n=50, c='-')))


def print_closing_header(file_id):
    log.info('^{}^'.format('{s:{c}^{n}}'.format(
        s=' {} '.format(file_id), n=50, c='-')))


def write_offset(path, data, offset):
    try:
        f = open(path, 'r+b')
        f.seek(offset)
        f.write(data)
        f.close()
    except Exception as e:
        raise Exception('Unable to write offset: {}'.format(str(e)))


def read_offset(path, offset, size):
    try:
        f = open(path, 'r+b')
        f.seek(offset)
        data = f.read(size)
        f.close()
        return data
    except Exception as e:
        raise Exception('Unable to read offset: {}'.format(str(e)))


def set_file_length(path, length):
    try:
        if os.path.isfile(path) and os.path.getsize(path) == length:
            return
        f = open(path, 'wb')
        f.seek(length-1)
        f.write('\0')
        f.truncate()
        f.close()
    except Exception as e:
        raise Exception('Unable to set file length: {}'.format(str(e)))


def get_file_type(path):
    try:
        mode = os.stat(path).st_mode
        if stat.S_ISDIR(mode):
            return 'directory'
        elif stat.S_ISCHR(mode):
            return 'character device'
        elif stat.S_ISBLK(mode):
            return 'block device'
        elif stat.S_ISREG(mode):
            return 'regular'
        elif stat.S_ISFIFO(mode):
            return 'fifo'
        elif stat.S_ISLNK(mode):
            return 'link'
        elif stat.S_ISSOCK(mode):
            return 'socket'
        else:
            return 'unknown'
    except Exception as e:
        raise RuntimeError('Unable to get file type: {}'.format(str(e)))


def calculate_segments(start, stop, block):
    """return a list of blocks in sizes no larger than `block`, the last
    block can be smaller.

    """
    return [(a, min(stop, a+block)-1) for a in range(start, stop, block)]


def md5sum(block):
    m = hashlib.md5()
    m.update(block)
    return m.hexdigest()


@contextmanager
def mmap_open(path):
    try:
        with open(path, "r+b") as f:
            mm = mmap.mmap(f.fileno(), 0)
            yield mm
    except Exception as e:
        raise RuntimeError('Unable to get file type: {}'.format(str(e)))


def STRIP(comment):
    return ' '.join(comment.split())
