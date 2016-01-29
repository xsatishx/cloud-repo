import unittest
from parcel import mock_server
from tempfile import NamedTemporaryFile, mkdtemp, gettempdir
import random
from multiprocessing import Process
from subprocess import check_call
import shutil
import os
import time


server_host = 'localhost'
server_port = 8888


class TestParcelUDT(unittest.TestCase):

    def setUp(self):
        self.files = [NamedTemporaryFile() for i in range(4)]
        for f in self.files:
            f.write(str(range(random.randint(100, 300))))
            f.flush()
        self.server = Process(
            target=mock_server.app.run,
            args=(server_host, server_port),
            kwargs=dict(debug=True, threaded=True))
        self.server.start()
        self.file_ids = [f.name.split('/')[-1] for f in self.files]
        self.dest_dir = mkdtemp()
        time.sleep(1)

    def tearDown(self):
        self.server.terminate()
        for f in self.files:
            f.close()
        shutil.rmtree(self.dest_dir)

    def validate_file(self, src, dst):
        with open(src, 'r') as s:
            with open(dst, 'r') as d:
                self.assertEqual(s.read(), d.read())

    @unittest.skip("UDT tests unfinished")
    def test_serial(self):
        for file_id in self.file_ids:
            print file_id
            check_call(
                ['parcel', 'udt', '-v',
                 '-n1',
                 '-d', self.dest_dir,
                 'http://{}:{}'.format(server_host, server_port),
                 file_id])
            self.validate_file(
                os.path.join(gettempdir(), file_id),
                os.path.join(gettempdir(), self.dest_dir, '{}_{}'.format(
                    file_id, file_id)))

    @unittest.skip("UDT tests unfinished")
    def test_parallel(self):
        for file_id in self.file_ids:
            print file_id
            check_call(
                ['parcel', 'udt', '-v',
                 '-n4',
                 '-d', self.dest_dir,
                 'http://{}:{}'.format(server_host, server_port),
                 file_id])
            self.validate_file(
                os.path.join(gettempdir(), file_id),
                os.path.join(gettempdir(), self.dest_dir, '{}_{}'.format(
                    file_id, file_id)))
