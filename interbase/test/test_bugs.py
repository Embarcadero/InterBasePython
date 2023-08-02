# coding:utf-8
#
#   PROGRAM/MODULE: idb
#   FILE:           test_bugs.py
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
import datetime

from io import BytesIO
from core import InterbaseTestBase
from constants import IBTEST_HOST, IBTEST_USER, IBTEST_PASSWORD, IBTEST_DB_DIR_PATH, IBTEST_DB_PATH,\
    IBTEST_SQL_DIALECT, IBTEST_SERVER_PUBLIC_FILE


class TestBugs(InterbaseTestBase):
    def setUp(self):
        self.dbfile = os.path.join(IBTEST_DB_DIR_PATH, 'ibbugs.ib')
        if os.path.exists(self.dbfile):
            os.remove(self.dbfile)
        self.con = idb.create_database(
            host=IBTEST_HOST,
            database=self.dbfile,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            sql_dialect=IBTEST_SQL_DIALECT,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE
        )

    def tearDown(self):
        self.con.drop_database()
        self.con.close()

    def test_pyib_17(self):
        create_table = """
        Create Table table1  (
            ID Integer,
            C1 Integer NOT Null
        );
        """
        # removed "OR UPDATE POSITION 0" because "Token unknown - line 3, char 30\n- OR"
        create_trigger = """
        CREATE TRIGGER BIU_Trigger FOR table1
        ACTIVE BEFORE INSERT
        AS
        BEGIN
            if (new.C1 IS NULL) then
            begin
                new.C1 = 1;
            end
        END
        """

        cur = self.con.cursor()
        cur.execute(create_table)
        cur.execute(create_trigger)
        self.con.commit()
        cur.execute('insert into table1 (ID, C1) values(1, ?)', (None,))

    def test_pyib_22(self):
        create_table = """
        CREATE TABLE IDBTEST (
            ID INTEGER,
            TEST80 VARCHAR(80),
            TEST128 VARCHAR(128),
            TEST255 VARCHAR(255),
            TEST1024 VARCHAR(1024),
            TESTCLOB BLOB SUB_TYPE 1 SEGMENT SIZE 255
        );
        """
        cur = self.con.cursor()
        cur.execute(create_table)
        self.con.commit()
        # test data
        data = ("1234567890" * 25) + "12345"
        for i in idb.ibase.xrange(255):
            cur.execute(
                "insert into idbtest (id, test255) values (?, ?)",
                (i, data[:i])
            )
        self.con.commit()
        cur.execute("select test255 from idbtest order by id")
        i = 0
        for row in cur:
            value = row[0]
            self.assertEqual(len(value), i)
            self.assertEqual(value, data[:i])
            i += 1

    def test_pyib_25(self):
        create_table = """
        CREATE TABLE IDBTEST2 (
            ID INTEGER,
            TEST5000 VARCHAR(5000)
        );
        """
        cur = self.con.cursor()
        cur.execute(create_table)
        self.con.commit()
        # test data
        data = "1234567890" * 500
        cur.execute(
            "insert into idbtest2 (id, test5000) values (?, ?)",
            (1, data)
        )
        self.con.commit()
        cur.execute("select test5000 from idbtest2")
        row = cur.fetchone()
        self.assertEqual(row[0], data)

    def test_pyib_30(self):
        create_table = """
        CREATE TABLE IDBTEST3 (
            ID INTEGER,
            T_BLOB BLOB sub_type 2
        );
        """
        cur = self.con.cursor()
        cur.execute(create_table)
        self.con.commit()

        # test data
        data_bytes = (1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
        blob_data = idb.bs(data_bytes)
        cur.execute(
            "insert into idbtest3 (id, t_blob) values (?, ?)",
            (1, blob_data)
        )
        cur.execute(
            "insert into idbtest3 (id, t_blob) values (?, ?)",
            (2, BytesIO(blob_data))
        )
        self.con.commit()

        # PYFB-XX: binary blob trucated at zero-byte
        cur.execute("select t_blob from idbtest3 where id = 1")
        row = cur.fetchone()
        self.assertEqual(row[0], blob_data)

        cur.execute("select t_blob from idbtest3 where id = 2")
        row = cur.fetchone()
        self.assertEqual(row[0], blob_data)

        p = cur.prep("select t_blob from idbtest3 where id = 2")
        p.set_stream_blob('T_BLOB')
        cur.execute(p)
        blob_reader = cur.fetchone()[0]
        value = blob_reader.read()
        self.assertEqual(value, blob_data)

    def test_pyib_34(self):
        cur = self.con.cursor()
        cur.execute("select * from RDB$Relations")
        cur.fetchall()
        del cur

    def test_pyib_35(self):
        create_table = """
        Create Table table1  (
            ID Integer,
            C1 Integer NOT Null
        );
        """

        c = self.con.cursor()
        c.execute(create_table)
        self.con.commit()
        del c

        cur = self.con.cursor()
        with self.assertRaises(idb.DatabaseError) as cm:
            cur.fetchall()
        self.assertTupleEqual(
            cm.exception.args,
            ("Cannot fetch from this cursor because it has not executed a statement.",)
        )

        cur.execute("select * from RDB$DATABASE")
        cur.fetchall()
        cur.execute("create generator seqtest")
        with self.assertRaises(idb.DatabaseError) as cm:
            cur.fetchall()
        self.assertTupleEqual(
            cm.exception.args,
            ("Attempt to fetch row of results after statement that does not produce result set.",)
        )

    def test_pyib_44(self):
        self.con2 = idb.connect(
            host=IBTEST_HOST,
            database=IBTEST_DB_PATH,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            sql_dialect=IBTEST_SQL_DIALECT,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE
        )
        try:
            cur = self.con2.cursor()
            now = datetime.datetime(2011, 11, 13, 15, 00, 1, 200)
            cur.execute('insert into T2 (C1,C8) values (?,?)', [3, now.date()])
            self.con2.commit()
            cur.execute('select C1,C8 from T2 where C1 = 3')
            rows = cur.fetchall()
            self.assertListEqual(
                rows,
                [(3, datetime.datetime(2011, 11, 13, 0, 0, 0, 0))]
            )
        finally:
            self.con2.execute_immediate("delete from t2")
            self.con2.commit()
            self.con2.close()
