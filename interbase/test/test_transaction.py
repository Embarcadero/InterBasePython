# coding:utf-8
#
#   PROGRAM/MODULE: idb
#   FILE:           test_transaction.py
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

import idb

from core import IDBTestBase
from constants import IBTEST_HOST, IBTEST_USER, IBTEST_PASSWORD, IBTEST_DB_PATH, IBTEST_SQL_DIALECT,\
    IBTEST_SERVER_PUBLIC_FILE


class TestTransaction(IDBTestBase):
    def setUp(self):
        self.connection = idb.connect(
            host=IBTEST_HOST,
            database=IBTEST_DB_PATH,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            sql_dialect=IBTEST_SQL_DIALECT,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE
        )

    def tearDown(self):
        self.connection.execute_immediate("delete from t")
        self.connection.commit()
        self.connection.close()

    def test_cursor(self):
        transaction = self.connection.main_transaction
        transaction.begin()
        cur = transaction.cursor()
        cur.execute("insert into t (c1) values (1)")
        transaction.commit()
        cur.execute("select * from t")
        rows = cur.fetchall()
        self.assertListEqual(rows, [(1,)])
        cur.execute("delete from t")
        transaction.commit()
        self.assertEqual(len(transaction.cursors), 1)
        self.assertIs(transaction.cursors[0], cur)

    def test_context_manager(self):
        with idb.TransactionContext(self.connection) as tr:
            cursor = tr.cursor()
            cursor.execute("insert into t (c1) values (1)")

        cursor.execute("select * from t")
        rows = cursor.fetchall()
        self.assertListEqual(rows, [(1,)])

        try:
            with idb.TransactionContext(self.connection):
                cursor.execute("delete from t")
                raise Exception()
        except Exception as e:
            pass

        cursor.execute("select * from t")
        rows = cursor.fetchall()
        self.assertListEqual(rows, [(1,)])

        with idb.TransactionContext(self.connection):
            cursor.execute("delete from t")

        cursor.execute("select * from t")
        rows = cursor.fetchall()
        self.assertListEqual(rows, [])

    def test_savepoint(self):
        self.connection.begin()
        transaction = self.connection.main_transaction
        self.connection.execute_immediate("insert into t (c1) values (1)")
        transaction.create_savepoint('test')
        self.connection.execute_immediate("insert into t (c1) values (2)")
        transaction.rollback(savepoint='test')
        transaction.commit()
        cursor = transaction.cursor()
        cursor.execute("select * from t")
        rows = cursor.fetchall()
        self.assertListEqual(rows, [(1,)])

    def test_fetch_after_commit(self):
        self.connection.execute_immediate("insert into t (c1) values (1)")
        self.connection.commit()
        cur = self.connection.cursor()
        cur.execute("select * from t")
        self.connection.commit()
        with self.assertRaises(idb.DatabaseError) as cm:
            rows = cur.fetchall()
        self.assertTupleEqual(cm.exception.args,
                              ('Cannot fetch from this cursor because it has not executed a statement.',))

    def test_fetch_after_rollback(self):
        self.connection.execute_immediate("insert into t (c1) values (1)")
        self.connection.rollback()
        cur = self.connection.cursor()
        cur.execute("select * from t")
        self.connection.commit()
        with self.assertRaises(idb.DatabaseError) as cm:
            rows = cur.fetchall()
        self.assertTupleEqual(cm.exception.args,
                              ('Cannot fetch from this cursor because it has not executed a statement.',))

    def test_tpb(self):
        tpb = idb.TPB()
        tpb.access_mode = idb.isc_tpb_write
        tpb.isolation_level = idb.isc_tpb_read_committed
        tpb.isolation_level = (idb.isc_tpb_read_committed, idb.isc_tpb_rec_version)
        tpb.lock_resolution = idb.isc_tpb_wait
        # tpb.lock_timeout = 10 #lock timeouts are not supported since 2017
        tpb.table_reservation['COUNTRY'] = (idb.isc_tpb_protected, idb.isc_tpb_lock_write)
        transaction = self.connection.trans(tpb)
        transaction.begin()
        transaction.commit()

    def test_transaction_info(self):
        self.connection.begin()
        transaction = self.connection.main_transaction
        info = transaction.transaction_info(idb.ibase.isc_info_tra_id, 's')
        self.assertIn(b'\x04\x04\x00', info)
        transaction.commit()
