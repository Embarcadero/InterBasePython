# coding:utf-8
#
#   PROGRAM/MODULE: idb
#   FILE:           test_stream_blobs.py
#   DESCRIPTION:    Python driver for InterBase
#   CREATED:        12.10.2011
#
#  Software distributed under the License is distributed AS IS,
#  WITHOUT WARRANTY OF ANY KIND, either express or implied.
#  See the License for the specific language governing rights
#  and limitations under the License.
#
#  The Original Code was created by Pavel Cisar
#
#  Copyright (c) 2011 Pavel Cisar <pcisar@users.sourceforge.net>
#  and all contributors signed below.
#
#  All Rights Reserved.
#  Contributor(s): Philippe Makowski <pmakowski@ibphoenix.fr>
#  ______________________________________.
#
#  Portions created by Embarcadero Technologies to support
#  InterBase are Copyright (c) 2023 by Embarcadero Technologies, Inc.
#
#  See LICENSE.TXT for details.

import os
import idb

from io import StringIO
from core import IDBTestBase
from contextlib import closing
from constants import IBTEST_HOST, IBTEST_USER, IBTEST_PASSWORD, IBTEST_DB_PATH, IBTEST_SQL_DIALECT,\
    IBTEST_SERVER_PUBLIC_FILE


class TestStreamBLOBs(IDBTestBase):
    def setUp(self):
        self.con = idb.connect(
            host=IBTEST_HOST,
            database=IBTEST_DB_PATH,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            sql_dialect=IBTEST_SQL_DIALECT,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE
        )

    def tearDown(self):
        self.con.execute_immediate("delete from t")
        self.con.execute_immediate("delete from t2")
        self.con.commit()
        self.con.close()

    def testBlobBasic(self):
        blob = """InterBase supports two types of blobs, stream and segmented.
The database stores segmented blobs in chunks.
Each chunk starts with a two byte length indicator followed by however many bytes of data were passed as a segment.
Stream blobs are stored as a continuous array of data bytes with no length indicators included."""
        cur = self.con.cursor()
        cur.execute('insert into T2 (C1,C9) values (?,?)', [4, StringIO(blob)])
        self.con.commit()
        p = cur.prep('select C1,C9 from T2 where C1 = 4')
        p.set_stream_blob('C9')
        cur.execute(p)
        row = cur.fetchone()
        blob_reader = row[1]
        ## Necessary to avoid bad BLOB handle on BlobReader.close in tearDown
        ## because BLOB handle is no longer valid after table purge
        with closing(p):
            self.assertEqual(blob_reader.read(20), 'InterBase supports t')
            self.assertEqual(blob_reader.read(20), 'wo types of blobs, s')
            self.assertEqual(
                blob_reader.read(400),
                'tream and segmented.\nThe database stores segmented blobs in chunks.\n'
                'Each chunk starts with a two byte length indicator followed by however many '
                'bytes of data were passed as a segment.\n'
                'Stream blobs are stored as a continuous array of data bytes with no length indicators included.'
            )
            self.assertEqual(blob_reader.read(20), '')
            self.assertEqual(blob_reader.tell(), 319)
            blob_reader.seek(20)
            self.assertEqual(blob_reader.tell(), 20)
            self.assertEqual(blob_reader.read(20), 'wo types of blobs, s')
            blob_reader.seek(0)
            self.assertEqual(blob_reader.tell(), 0)
            self.assertListEqual(blob_reader.readlines(), StringIO(blob).readlines())
            blob_reader.seek(0)
            for line in blob_reader:
                self.assertIn(line.rstrip('\n'), blob.split('\n'))
            blob_reader.seek(0)
            self.assertEqual(blob_reader.read(), blob)
            blob_reader.seek(-9, os.SEEK_END)
            self.assertEqual(blob_reader.read(), 'included.')
            blob_reader.seek(-20, os.SEEK_END)
            blob_reader.seek(11, os.SEEK_CUR)
            self.assertEqual(blob_reader.read(), 'included.')
            blob_reader.seek(61)
            self.assertEqual(
                blob_reader.readline(),
                'The database stores segmented blobs in chunks.\n'
            )

    def testBlobExtended(self):
        blob = """InterBase supports two types of blobs, stream and segmented.
The database stores segmented blobs in chunks.
Each chunk starts with a two byte length indicator followed by however many bytes of data were passed as a segment.
Stream blobs are stored as a continuous array of data bytes with no length indicators included."""
        cur = self.con.cursor()
        cur.execute('insert into T2 (C1,C9) values (?,?)', [1, StringIO(blob)])
        cur.execute('insert into T2 (C1,C9) values (?,?)', [2, StringIO(blob)])
        self.con.commit()
        p = cur.prep('select C1,C9 from T2')
        p.set_stream_blob('C9')
        cur.execute(p)
        # rows = [row for row in cur]
        # Necessary to avoid bad BLOB handle on BlobReader.close in tearDown
        # because BLOB handle is no longer valid after table purge
        with closing(p):
            for row in cur:
                blob_reader = row[1]
                self.assertEqual(blob_reader.read(20), 'InterBase supports t')
                self.assertEqual(blob_reader.read(20), 'wo types of blobs, s')
                self.assertEqual(
                    blob_reader.read(400),
                    'tream and segmented.\nThe database stores segmented blobs in chunks.\n'
                    'Each chunk starts with a two byte length indicator followed by however many '
                    'bytes of data were passed as a segment.\n'
                    'Stream blobs are stored as a continuous array of data bytes with no length indicators included.'
                )
                self.assertEqual(blob_reader.read(20), '')
                self.assertEqual(blob_reader.tell(), 319)
                blob_reader.seek(20)
                self.assertEqual(blob_reader.tell(), 20)
                self.assertEqual(blob_reader.read(20), 'wo types of blobs, s')
                blob_reader.seek(0)
                self.assertEqual(blob_reader.tell(), 0)
                self.assertListEqual(blob_reader.readlines(),
                                     StringIO(blob).readlines())
                blob_reader.seek(0)
                for line in blob_reader:
                    self.assertIn(line.rstrip('\n'), blob.split('\n'))
                blob_reader.seek(0)
                self.assertEqual(blob_reader.read(), blob)
                blob_reader.seek(-9, os.SEEK_END)
                self.assertEqual(blob_reader.read(), 'included.')
                blob_reader.seek(-20, os.SEEK_END)
                blob_reader.seek(11, os.SEEK_CUR)
                self.assertEqual(blob_reader.read(), 'included.')
                blob_reader.seek(61)
                self.assertEqual(
                    blob_reader.readline(),
                    'The database stores segmented blobs in chunks.\n'
                )
