from flask import Flask, request, make_response
import mmap
import os
import contextlib
import tempfile

app = Flask(__name__)
directory = tempfile.gettempdir()


def send_range(f, file_id, ranges):
    with contextlib.closing(mmap.mmap(
            f.fileno(), 0, access=mmap.ACCESS_READ)) as m:
        start, end = parse_ranges(ranges)
        return m[start:end+1]


@app.route('/<file_id>', methods=['POST', 'GET'])
def download(file_id):
    path = os.path.join(directory, file_id)
    headers = request.headers
    with open(path, 'r') as f:
        if 'Range' in headers:
            content = send_range(f, file_id, headers['Range'])
        else:
            content = f.read()
    response = make_response(content)
    response.headers["Content-Disposition"] = (
        "attachment; filename={}".format(file_id))
    response.headers["Content-Length"] = len(content)
    return response


def parse_ranges(ranges):
    """Validate an HTTP ranges, throwing an exception if it isn't something
    we support. For now we only support things of the form bytes={begin}-{end}

    .. note: this is taken from https://github.com/NCI-GDC/gdcapi/blob/master/gdcapi/download/__init__.py ecfefb9ac1767e6659c9c816232ef18cb21f5817

    """
    try:
        ranges = ranges.strip()
        unit, nums = ranges.split("=")
        if unit != "bytes":
            raise RuntimeError("Only byte rangess are supported, not {}".format(unit))
        begin, end = nums.split("-")
        begin, end = int(begin), int(end)
        if end < begin:
            raise RuntimeError("impossible ranges: {}".format(ranges))
        else:
            return begin, end
    except ValueError:
        raise RuntimeError("Malformed ranges: {}".format(ranges))
