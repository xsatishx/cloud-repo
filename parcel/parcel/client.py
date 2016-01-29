from . import const
from . import utils
from .download_stream import DownloadStream
from .log import get_logger
from .portability import colored
from .portability import Process
from .segment import SegmentProducer

import os
import tempfile
import time

# Logging
log = get_logger('client')


class Client(object):

    def __init__(self, uri, token, n_procs, directory=None,
                 debug=False, **kwargs):
        """Creates a parcel client object.

        :param str uri:
            The uri path [scheme://server:port/path] of the remote server
        :param str token:
            The authentication token that will be added to the HTTP
            X-Auth-Token header
        :param int n_procs:
            The number of processes to use in download
        :param str directory:
            The directory to which any data will be downloaded

        """

        DownloadStream.http_chunk_size = kwargs.get(
            'http_chunk_size', const.HTTP_CHUNK_SIZE)
        DownloadStream.check_segment_md5sums = kwargs.get(
            'segment_md5sums', True)
        SegmentProducer.save_interval = kwargs.get(
            'save_interval', const.SAVE_INTERVAL)

        self.debug = debug
        self.directory = directory or os.path.abspath(os.getcwd())
        self.directory = os.path.expanduser(self.directory)
        self.n_procs = n_procs
        self.start = None
        self.stop = None
        self.token = token
        self.uri = self.fix_uri(uri)

    @staticmethod
    def fix_uri(uri):
        """Fix an improperly formatted url that is missing a scheme

        :params str url: The url to be fixed
        :returns: Fixed url with trailing / and scheme

        """

        uri = uri if uri.endswith('/') else '{}/'.format(uri)
        if not (uri.startswith('https://') or uri.startswith('http://')):
            uri = 'https://{}'.format(uri)
        return uri

    @staticmethod
    def raise_for_write_permissions(directory):
        try:
            tempfile.NamedTemporaryFile(dir=directory).close()
        except (OSError, IOError) as e:
            raise IOError(utils.STRIP("""Unable to write
            to download to directory '{directory}': {err}.  This
            error likely occurred because the program was launched
            from (or specified to download to) a protected
            directory.  If you are running this executable from an
            archive (*.zip, *.tar.gz, etc.) then extracting it
            from the archive might solve this problem. Otherwise,
            please see documentation on how to change/specify
            directory.""").format(err=str(e), directory=directory))

    def start_timer(self):
        """Start a download timer.

        :returns: None

        """

        self.start_time = time.time()

    def stop_timer(self, file_size=None):
        """Stop a download timer and pring a summary.

        :returns: None

        """

        self.stop_time = time.time()
        if file_size > 0:
            rate = (int(file_size)*8/1e9) / (self.stop_time - self.start_time)
            log.info(
                'Download complete: {0:.2f} Gbps average'.format(rate))

    def download_files(self, file_ids, *args, **kwargs):
        """Download a list of files.

        :params list file_ids:
            A list of strings containing the ids of the entities to download

        """

        # Short circuit of no ids given
        if not file_ids:
            log.warn('No file ids given.')
            return

        self.raise_for_write_permissions(self.directory)

        # Log file ids
        for file_id in file_ids:
            log.info('Given file id: {}'.format(file_id))

        # Download each file
        downloaded, errors = [], {}
        for file_id in set(file_ids):

            # Construct download stream
            directory = os.path.join(self.directory, file_id)
            stream = DownloadStream(file_id, self.uri, directory, self.token)

            # Download file
            try:
                self.parallel_download(stream)
                downloaded.append(file_id)

            # Handle file download error, store error to print out later
            except Exception as e:
                log.error('Unable to download {}: {}'.format(file_id, str(e)))
                errors[file_id] = str(e)
                if self.debug:
                    raise

            finally:
                utils.print_closing_header(file_id)

        # Print error messages
        self.print_summary(downloaded, errors)
        for file_id, error in errors.iteritems():
            print('ERROR: {}: {}'.format(file_id, error))

        return downloaded, errors

    def print_summary(self, downloaded, errors):
        print('\nSUMMARY:')
        if downloaded:
            print('{}: {}'.format(
                colored('Successfully downloaded', 'green'), len(downloaded)))
        if errors:
            print('{}: {}'.format(
                colored('Failed to download', 'red'), len(errors)))
        print('')

    def serial_download(self, stream):
        """Download file to directory serially.

        """
        self._download(1, stream)

    def parallel_download(self, stream):
        """Download file to directory in parallel.

        """
        self._download(self.n_procs, stream)

    def _download(self, nprocs, stream):
        """Start ``self.n_procs`` to download the file.

        :params str file_id:
            String containing the id of the entity to download

        """

        # Start stream
        utils.print_opening_header(stream.ID)
        log.info('Getting file information...')
        stream.init()

        # Create segments producer to stream
        n_procs = 1 if stream.size < .01 * const.GB else nprocs
        producer = SegmentProducer(stream, n_procs)

        def download_worker():
            while True:
                try:
                    segment = producer.q_work.get()
                    if segment is None:
                        return log.debug('Producer returned with no more work')
                    stream.write_segment(segment, producer.q_complete)
                except Exception as e:
                    if self.debug:
                        raise
                    else:
                        log.error("Download aborted: {}".format(str(e)))

        # Divide work amongst process pool
        pool = [Process(target=download_worker) for i in range(n_procs)]

        # Start pool
        map(lambda p: p.start(), pool)
        self.start_timer()

        # Wait for file to finish download
        producer.wait_for_completion()
        self.stop_timer()
