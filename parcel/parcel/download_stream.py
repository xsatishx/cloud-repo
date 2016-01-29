from .log import get_logger
from . import utils
from . import const

from intervaltree import Interval
import os
import requests
import urlparse


class DownloadStream(object):

    http_chunk_size = const.HTTP_CHUNK_SIZE
    check_segment_md5sums = True

    def __init__(self, ID, uri, directory, token=None):
        self.ID = ID
        self.initialized = False
        self.is_regular_file = True
        self.log = get_logger(str(ID))
        self.name = None
        self.directory = directory
        self.size = None
        self.token = token
        self.uri = uri

    def init(self):
        self.get_information()
        self.print_download_information()
        self.initialized = True
        return self

    def setup_file(self):
        self.setup_directories()
        try:
            utils.set_file_length(self.path, self.size)
        except:
            self.log.warn(utils.STRIP(
                """Unable to set file length. File appears to
                be a {} file, attempting to proceed.
                """.format(utils.get_file_type(self.path))))
            self.is_regular_file = False

    def setup_directories(self):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        if not os.path.exists(self.state_directory):
            os.makedirs(self.state_directory)

    @property
    def path(self):
        """Function to standardize the output path for a download.

        :returns: A string specifying the full download path
        """
        return os.path.join(self.directory, self.name)

    @property
    def state_path(self):
        """Function to standardize the state path for a download.

        :returns: A string specifying the download state path
        """
        return os.path.join(
            self.state_directory, '{}.parcel'.format(self.name))

    @property
    def state_directory(self):
        """Function to standardize the state directory for a download.

        :returns: A string specifying the download state directory
        """
        return os.path.join(self.directory, 'logs')

    def header(self, start=None, end=None):
        """Return a standard header for any parcel HTTP request.  If ``start``
        and ``end`` are specified, then the header will contain a Range
        request.

        :param int start: optional. The beginning of the range interval
        :param int end: optional.
            The end of the range interval. This value is inclusive.
            If give range A-B, then both bytes A and B will be
            included.
        :returns: A dictionary header containing the token
        """

        header = {
            'X-Auth-Token': self.token,
        }
        if start is not None and end is not None:
            header['Range'] = 'bytes={}-{}'.format(start, end)
            # provide host because it's mandatory, range request
            # may not work otherwise
            scheme, host, path, params, q, frag = urlparse.urlparse(self.uri)
            header['host'] = host
        return header

    def request(self, headers=None, verify=False, close=False,
                max_retries=16):
        """Make request for file and return the response.

        :param str file_id: The id of the entity being requested.
        :param dict headers: Request headers. see :func:`construct_header()`.
        :param bool verify: Verify SSL hostname
        :param bool close:
            Automatically close the connection. Set to true if you just
            the response header.
        :returns: A `requests` response.

        """
        url = urlparse.urljoin(self.uri, self.ID)
        self.log.debug('Request to {}'.format(url))

        # Set urllib3 retries and mount for session
        a = requests.adapters.HTTPAdapter(max_retries=max_retries)
        s = requests.Session()
        s.mount(urlparse.urlparse(url).scheme, a)

        headers = self.headers() if headers is None else headers
        try:
            r = s.get(url, headers=headers, verify=verify, stream=True)
        except Exception as e:
            raise RuntimeError((
                "Unable to connect to API: ({}). Is this url correct: '{}'? "
                "Is there a connection to the API? Is the server running?"
            ).format(str(e), self.uri))
        try:
            r.raise_for_status()
        except Exception as e:
            raise RuntimeError('{}: {}'.format(str(e), r.text))

        if close:
            r.close()
        return r

    def get_information(self):
        """Make a request to the data server for information on the file.

        :param str file_id: The id of the entity being requested.
        :returns: Tuple containing the name and size of the entity

        """

        headers = self.header()
        r = self.request(headers, close=True)
        content_length = r.headers.get('Content-Length')
        if not content_length:
            raise ValueError(
                'Unexpected response from server: missing content length.')
        self.size = long(content_length)
        self.log.info('Request responded   : {} bytes'.format(self.size))
        attachment = r.headers.get('content-disposition', None)
        self.name = (attachment.split('filename=')[-1]
                     if attachment else 'untitled')
        return self.name, self.size

    def write_segment(self, segment, q_complete, retries=5):

        """Read data from the data server and write it to a file.

        :param str file_id: The id of the file
        :params str path: A string specifying the full download path
        :params tuple segment:
            A tuple containing the interval to download (start, end)
        :params q_out: A multiprocessing Queue used for async reporting
        :returns: The total number of bytes written

        """

        written = 0
        # Create header that specifies range and make initial stream
        # request. Note the 1 subtracted from the end of the interval
        # is because the HTTP range request is inclusive of the top of
        # the interval.
        start, end = segment.begin, segment.end-1
        assert end >= start, 'Invalid segment range.'

        try:
            # Initialize segment request
            r = self.request(self.header(start, end))

            # Iterate over the data stream
            self.log.debug('Initializing segment: {}-{}'.format(start, end))
            for chunk in r.iter_content(chunk_size=self.http_chunk_size):
                if not chunk:
                    continue  # Empty are keep-alives.
                offset = start + written
                written += len(chunk)

                # Write the chunk to disk, create an interval that
                # represents the chunk, get md5 info if necessary, and
                # report completion back to the producer
                utils.write_offset(self.path, chunk, offset)
                if self.check_segment_md5sums:
                    iv_data = {'md5sum': utils.md5sum(chunk)}
                else:
                    iv_data = None
                complete_segment = Interval(offset, offset+len(chunk), iv_data)
                q_complete.put(complete_segment)

        except KeyboardInterrupt:
            return self.log.error('Process stopped by user.')

        # Retry on exception if we haven't exceeded max retries
        except Exception as e:
            self.log.warn(
                'Unable to download part of file: {}\n.'.format(str(e)))
            if retries > 0:
                self.log.warn('Retrying download of this segment')
                return self.write_segment(segment, q_complete, retries-1)
            else:
                self.log.error('Max retries exceeded.')
                return 0

        # Check that the data is not truncated or elongated
        if written != segment.end-segment.begin:
            self.log.warn('Segment corruption: {}'.format(
                '(non-fatal) retrying' if retries else 'max retries exceeded'))
            if retries:
                return self.write_segment(segment, q_complete, retries-1)
            else:
                raise RuntimeError('Segment corruption. Max retries exceeded.')

        r.close()
        return written

    def print_download_information(self):
        self.log.info('Starting download   : {}'.format(self.ID))
        self.log.info('File name           : {}'.format(self.name))
        self.log.info('Download size       : {} B ({:.2f} GB)'.format(
            self.size, (self.size / float(const.GB))))
        self.log.info('Downloading file to : {}'.format(self.path))
