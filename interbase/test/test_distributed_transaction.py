# coding:utf-8
#
#   PROGRAM/MODULE: idb
#   FILE:           test_distributed_transaction.py
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

from core import InterbaseTestBase
from constants import IBTEST_HOST, IBTEST_USER, IBTEST_PASSWORD, IBTEST_DB_DIR_PATH,\
    IBTEST_SQL_DIALECT, IBTEST_SERVER_PUBLIC_FILE
from unittest import skip


class TestDistributedTransaction(InterbaseTestBase):
    def setUp(self):
        self.db1 = os.path.join(IBTEST_DB_DIR_PATH, 'ibtest-1.ib')
        self.db2 = os.path.join(IBTEST_DB_DIR_PATH, 'ibtest-2.ib')

        if os.path.exists(self.db1):
            os.remove(self.db1)

        if os.path.exists(self.db2):
            os.remove(self.db2)

        self.con1 = idb.create_database(
            host=IBTEST_HOST,
            database=self.db1,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            sql_dialect=IBTEST_SQL_DIALECT,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE
        )
        self.con1 = idb.connect(
            host=IBTEST_HOST,
            database=self.db1,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            sql_dialect=IBTEST_SQL_DIALECT,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE
        )
        self.con1.execute_immediate("create table T (PK integer, C1 integer)")
        self.con1.commit()

        self.con2 = idb.create_database(
            host=IBTEST_HOST,
            database=self.db2,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            sql_dialect=IBTEST_SQL_DIALECT,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE
        )
        self.con2 = idb.connect(
            host=IBTEST_HOST,
            database=self.db2,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            sql_dialect=IBTEST_SQL_DIALECT,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE
        )
        self.con2.execute_immediate("create table T (PK integer, C1 integer)")
        self.con2.commit()

    def tearDown(self):
        if self.con1 and self.con1.group:
            # We can't drop database via connection in group
            self.con1.group.disband()
        if not self.con1:
            self.con1 = idb.connect(
                host=IBTEST_HOST,
                database=self.db1,
                user=IBTEST_USER,
                password=IBTEST_PASSWORD,
                sql_dialect=IBTEST_SQL_DIALECT,
                ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
                server_public_file=IBTEST_SERVER_PUBLIC_FILE
            )
        self.con1.drop_database()
        self.con1.close()
        if not self.con2:
            self.con2 = idb.connect(
                host=IBTEST_HOST,
                database=self.db2,
                user=IBTEST_USER,
                password=IBTEST_PASSWORD,
                sql_dialect=IBTEST_SQL_DIALECT,
                ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
                server_public_file=IBTEST_SERVER_PUBLIC_FILE
            )
        self.con2.drop_database()
        self.con2.close()

    def test_context_manager(self):
        cg = idb.ConnectionGroup((self.con1, self.con2))

        q = 'select * from T order by pk'
        c1 = cg.cursor(self.con1)
        cc1 = self.con1.cursor()
        p1 = cc1.prep(q)

        c2 = cg.cursor(self.con2)
        cc2 = self.con2.cursor()
        p2 = cc2.prep(q)

        # Distributed transaction: COMMIT
        with idb.TransactionContext(cg):
            c1.execute('insert into t (pk) values (1)')
            c2.execute('insert into t (pk) values (1)')

        self.con1.commit()
        cc1.execute(p1)
        result = cc1.fetchall()
        self.assertListEqual(result, [(1, None)])
        self.con2.commit()
        cc2.execute(p2)
        result = cc2.fetchall()
        self.assertListEqual(result, [(1, None)])

        # Distributed transaction: ROLLBACK
        try:
            with idb.TransactionContext(cg):
                c1.execute('insert into t (pk) values (2)')
                c2.execute('insert into t (pk) values (2)')
                raise Exception()
        except Exception as e:
            pass

        c1.execute(q)
        result = c1.fetchall()
        self.assertListEqual(result, [(1, None)])
        c2.execute(q)
        result = c2.fetchall()
        self.assertListEqual(result, [(1, None)])

        cg.disband()

    def test_simple_dt(self):
        cg = idb.ConnectionGroup((self.con1, self.con2))
        self.assertEqual(self.con1.group, cg)
        self.assertEqual(self.con2.group, cg)

        q = 'select * from T order by pk'
        c1 = cg.cursor(self.con1)
        cc1 = self.con1.cursor()
        p1 = cc1.prep(q)

        c2 = cg.cursor(self.con2)
        cc2 = self.con2.cursor()
        p2 = cc2.prep(q)

        # Distributed transaction: COMMIT
        c1.execute('insert into t (pk) values (1)')
        c2.execute('insert into t (pk) values (1)')
        cg.commit()

        self.con1.commit()
        cc1.execute(p1)
        result = cc1.fetchall()
        self.assertListEqual(result, [(1, None)])
        self.con2.commit()
        cc2.execute(p2)
        result = cc2.fetchall()
        self.assertListEqual(result, [(1, None)])

        # Distributed transaction: PREPARE+COMMIT
        c1.execute('insert into t (pk) values (2)')
        c2.execute('insert into t (pk) values (2)')
        cg.prepare()
        cg.commit()

        self.con1.commit()
        cc1.execute(p1)
        result = cc1.fetchall()
        self.assertListEqual(result, [(1, None), (2, None)])
        self.con2.commit()
        cc2.execute(p2)
        result = cc2.fetchall()
        self.assertListEqual(result, [(1, None), (2, None)])

        # Distributed transaction: SAVEPOINT+ROLLBACK to it
        c1.execute('insert into t (pk) values (3)')
        cg.create_savepoint('CG_SAVEPOINT')
        c2.execute('insert into t (pk) values (3)')
        cg.rollback(savepoint='CG_SAVEPOINT')

        c1.execute(q)
        result = c1.fetchall()
        self.assertListEqual(result, [(1, None), (2, None), (3, None)])
        c2.execute(q)
        result = c2.fetchall()
        self.assertListEqual(result, [(1, None), (2, None)])

        # Distributed transaction: ROLLBACK
        cg.rollback()

        self.con1.commit()
        cc1.execute(p1)
        result = cc1.fetchall()
        self.assertListEqual(result, [(1, None), (2, None)])
        self.con2.commit()
        cc2.execute(p2)
        result = cc2.fetchall()
        self.assertListEqual(result, [(1, None), (2, None)])

        # Distributed transaction: EXECUTE_IMMEDIATE
        cg.execute_immediate('insert into t (pk) values (3)')
        cg.commit()

        self.con1.commit()
        cc1.execute(p1)
        result = cc1.fetchall()
        self.assertListEqual(result, [(1, None), (2, None), (3, None)])
        self.con2.commit()
        cc2.execute(p2)
        result = cc2.fetchall()
        self.assertListEqual(result, [(1, None), (2, None), (3, None)])

        cg.disband()
        self.assertIsNone(self.con1.group)
        self.assertIsNone(self.con2.group)

    @skip("issue #44: test_limbo_transactions fails with exception: access violation on win x32")
    def test_limbo_transactions(self):
        cg = idb.ConnectionGroup((self.con1, self.con2))
        svc = idb.services.connect(host=IBTEST_HOST,
                                   user=IBTEST_USER,
                                   password=IBTEST_PASSWORD,
                                   ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
                                   server_public_file=IBTEST_SERVER_PUBLIC_FILE)

        ids1 = svc.get_limbo_transaction_ids(self.db1)
        self.assertEqual(ids1, [])
        ids2 = svc.get_limbo_transaction_ids(self.db2)
        self.assertEqual(ids2, [])

        cg.execute_immediate('insert into t (pk) values (3)')
        cg.prepare()

        # Force out both connections
        self.con1._set_group(None)
        cg._cons.remove(self.con1)
        del self.con1
        self.con1 = None

        self.con2._set_group(None)
        cg._cons.remove(self.con2)
        del self.con2
        self.con2 = None

        # Disband will raise an error
        with self.assertRaises(idb.DatabaseError) as cm:
            cg.disband()
        self.assertTupleEqual(
            cm.exception.args,
            (
                "Error while rolling back transaction:\n- SQLCODE: -901\n- b'invalid transaction handle (expecting explicit transaction start)'",
                -901, 335544332
            )
        )

        ids1 = svc.get_limbo_transaction_ids(self.db1)
        id1 = ids1[0]
        ids2 = svc.get_limbo_transaction_ids(self.db2)
        id2 = ids2[0]

        # Data chould be blocked by limbo transaction
        if not self.con1:
            self.con1 = idb.connect(
                dsn=self.db1,
                user=IBTEST_USER,
                password=IBTEST_PASSWORD,
                sql_dialect=IBTEST_SQL_DIALECT,
                ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
                server_public_file=IBTEST_SERVER_PUBLIC_FILE
            )
        if not self.con2:
            self.con2 = idb.connect(
                dsn=self.db2,
                user=IBTEST_USER,
                password=IBTEST_PASSWORD,
                sql_dialect=IBTEST_SQL_DIALECT,
                ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
                server_public_file=IBTEST_SERVER_PUBLIC_FILE
            )
        c1 = self.con1.cursor()
        c1.execute('select * from t')
        with self.assertRaises(idb.DatabaseError) as cm:
            row = c1.fetchall()
        self.assertTupleEqual(
            cm.exception.args,
            ("Cursor.fetchone:\n- SQLCODE: -911\n- b'record from transaction %i is stuck in limbo'" % id1,
             -911, 335544459)
        )
        c2 = self.con2.cursor()
        c2.execute('select * from t')
        with self.assertRaises(idb.DatabaseError) as cm:
            row = c2.fetchall()
        self.assertTupleEqual(
            cm.exception.args,
            ("Cursor.fetchone:\n- SQLCODE: -911\n- b'record from transaction %i is stuck in limbo'" % id2,
             -911, 335544459)
        )

        # resolve via service
        svc = idb.services.connect(host=IBTEST_HOST,
                                   user=IBTEST_USER,
                                   password=IBTEST_PASSWORD,
                                   ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
                                   server_public_file=IBTEST_SERVER_PUBLIC_FILE)
        svc.commit_limbo_transaction(self.db1, id1)
        svc.rollback_limbo_transaction(self.db2, id2)

        # check the resolution
        c1 = self.con1.cursor()
        c1.execute('select * from t')
        row = c1.fetchall()
        self.assertListEqual(row, [(3, None)])
        c2 = self.con2.cursor()
        c2.execute('select * from t')
        row = c2.fetchall()
        self.assertListEqual(row, [])

        svc.close()
