# coding:utf-8
#
#   PROGRAM/MODULE: idb
#   FILE:           test_connection.py
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
import os

from unittest import skipUnless
from sys import platform
from core import InterbaseTestBase
from contextlib import closing
from constants import IBTEST_PASSWORD, IBTEST_USER, IBTEST_DB_PATH, IBTEST_HOST,\
    IBTEST_USE_EMBEDDED, IBTEST_SQL_DIALECT, IBTEST_SERVER_PUBLIC_FILE

class TestConnection(InterbaseTestBase):

    def test_connect(self):
        with closing(
            idb.connect(
                #dsn=IBTEST_HOST + ":" + IBTEST_DB_PATH if IBTEST_HOST else IBTEST_DB_PATH,
                host=IBTEST_HOST,
                database=IBTEST_DB_PATH,
                user=IBTEST_USER,
                password=IBTEST_PASSWORD,
                sql_dialect=IBTEST_SQL_DIALECT,
                ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
                server_public_file=IBTEST_SERVER_PUBLIC_FILE)
        ) as con:
            self.assertIsNotNone(con._db_handle)
            dpb = [1, 0x1c, len(IBTEST_USER)]
            dpb.extend(ord(x) for x in IBTEST_USER)
            dpb.extend((0x1d, len(IBTEST_PASSWORD)))
            dpb.extend(ord(x) for x in IBTEST_PASSWORD)
            dpb.extend((ord('?'), 1, IBTEST_SQL_DIALECT))
            self.assertEqual(con._dpb, idb.bs(dpb))

    def test_properties(self):
        with closing(
                idb.connect(#dsn=IBTEST_HOST + ":" + IBTEST_DB_PATH if IBTEST_HOST else IBTEST_DB_PATH,
                            host=IBTEST_HOST,
                            database=IBTEST_DB_PATH,
                            user=IBTEST_USER,
                            password=IBTEST_PASSWORD,
                            sql_dialect=IBTEST_SQL_DIALECT,
                            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
                            server_public_file=IBTEST_SERVER_PUBLIC_FILE)
        ) as con:
            if platform == 'win32':
                # InterBase Server and Embedded (ToGo) on Windows
                self.assertRegex(con.server_version, r"^W[IE]-V[\d\.]+")
            elif platform == 'darwin':
                # InterBase Server and Embedded (ToGo) on macOS (ARM64 and x86_64 respectively)
                self.assertRegex(con.server_version, r"^D[DMWE]-V[\d\.]+")
            elif platform == 'linux':
                # InterBase Server and Embedded (ToGo) on Linux
                self.assertRegex(con.server_version, r"^L[IE]-V[\d\.]+")
            else:
                self.fail("Platform is not supported.")
            self.assertIsInstance(con.version, str)
            self.assertGreaterEqual(con.engine_version, 2.0)
            self.assertGreaterEqual(con.ods, 11.0)
            self.assertIsNone(con.group)
            self.assertIsNone(con.charset)
            self.assertEqual(len(con.transactions), 2)
            self.assertIn(con.main_transaction, con.transactions)
            self.assertIn(con.query_transaction, con.transactions)
            self.assertEqual(con.default_tpb, idb.ISOLATION_LEVEL_READ_COMMITED)
            self.assertIsInstance(con.schema, idb.schema.Schema)
            self.assertFalse(con.closed)

    def test_connect_role(self):
        role_name = 'role'
        with closing(
                idb.connect(#dsn=IBTEST_HOST + ":" + IBTEST_DB_PATH if IBTEST_HOST else IBTEST_DB_PATH,
                            host=IBTEST_HOST,
                            database=IBTEST_DB_PATH,
                            user=IBTEST_USER,
                            password=IBTEST_PASSWORD,
                            role=role_name,
                            sql_dialect=IBTEST_SQL_DIALECT,
                            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
                            server_public_file=IBTEST_SERVER_PUBLIC_FILE)
        ) as con:
            self.assertIsNotNone(con._db_handle)
            dpb = [1, 0x1c, len(IBTEST_USER)]
            dpb.extend(ord(x) for x in IBTEST_USER)
            dpb.extend((0x1d, len(IBTEST_PASSWORD)))
            dpb.extend(ord(x) for x in IBTEST_PASSWORD)
            dpb.extend((ord('<'), len(role_name)))
            dpb.extend(ord(x) for x in role_name)
            dpb.extend((ord('?'), 1, IBTEST_SQL_DIALECT))
            self.assertEqual(con._dpb, idb.bs(dpb))

    def test_transaction(self):
        with closing(
                idb.connect(#dsn=IBTEST_HOST + ":" + IBTEST_DB_PATH if IBTEST_HOST else IBTEST_DB_PATH,
                            host=IBTEST_HOST,
                            database=IBTEST_DB_PATH,
                            user=IBTEST_USER,
                            password=IBTEST_PASSWORD,
                            sql_dialect=IBTEST_SQL_DIALECT,
                            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
                            server_public_file=IBTEST_SERVER_PUBLIC_FILE)
        ) as con:
            self.assertIsNotNone(con.main_transaction)
            self.assertFalse(con.main_transaction.active)
            self.assertFalse(con.main_transaction.closed)
            self.assertEqual(con.main_transaction.default_action, 'commit')
            self.assertEqual(len(con.main_transaction._connections), 1)
            self.assertEqual(con.main_transaction._connections[0](), con)
            con.begin()
            self.assertFalse(con.main_transaction.closed)
            con.commit()
            self.assertFalse(con.main_transaction.active)
            con.begin()
            con.rollback()
            self.assertFalse(con.main_transaction.active)
            con.begin()
            con.commit(retaining=True)
            self.assertTrue(con.main_transaction.active)
            con.rollback(retaining=True)
            self.assertTrue(con.main_transaction.active)
            transaction = con.trans()
            self.assertIsInstance(transaction, idb.Transaction)
            self.assertFalse(con.main_transaction.closed)
            self.assertEqual(len(con.transactions), 3)
            transaction.begin()
            self.assertFalse(transaction.closed)
            con.begin()
            con.close()
            self.assertFalse(con.main_transaction.active)
            self.assertTrue(con.main_transaction.closed)
            self.assertFalse(transaction.active)
            self.assertTrue(transaction.closed)

    def test_execute_immediate(self):
        with closing(
                idb.connect(#dsn=IBTEST_HOST + ":" + IBTEST_DB_PATH if IBTEST_HOST else IBTEST_DB_PATH,
                            host=IBTEST_HOST,
                            database=IBTEST_DB_PATH,
                            user=IBTEST_USER,
                            password=IBTEST_PASSWORD,
                            sql_dialect=IBTEST_SQL_DIALECT,
                            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
                            server_public_file=IBTEST_SERVER_PUBLIC_FILE)
        ) as con:
            con.execute_immediate("create table tmp (c1 integer)")
            con.commit()
            con.execute_immediate("drop table tmp")
            con.commit()

    def test_database_info(self):
        with closing(
                idb.connect(#dsn=IBTEST_HOST + ":" + IBTEST_DB_PATH if IBTEST_HOST else IBTEST_DB_PATH,
                            host=IBTEST_HOST,
                            database=IBTEST_DB_PATH,
                            user=IBTEST_USER,
                            password=IBTEST_PASSWORD,
                            sql_dialect=IBTEST_SQL_DIALECT,
                            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
                            server_public_file=IBTEST_SERVER_PUBLIC_FILE)
        ) as con:
            self.assertEqual(con.database_info(idb.isc_info_db_read_only, 'i'), 0)
            self.assertEqual(con.database_info(idb.isc_info_page_size, 'i'), 4096)
            self.assertEqual(con.database_info(idb.isc_info_db_sql_dialect, 'i'), IBTEST_SQL_DIALECT)

    def test_db_info(self):
        with closing(
                idb.connect(#dsn=IBTEST_HOST + ":" + IBTEST_DB_PATH if IBTEST_HOST else IBTEST_DB_PATH,
                            host=IBTEST_HOST,
                            database=IBTEST_DB_PATH,
                            user=IBTEST_USER,
                            password=IBTEST_PASSWORD,
                            sql_dialect=IBTEST_SQL_DIALECT,
                            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
                            server_public_file=IBTEST_SERVER_PUBLIC_FILE)) as con:
            res = con.db_info(
                [
                    idb.isc_info_page_size,
                    idb.isc_info_db_read_only,
                    idb.isc_info_db_sql_dialect,
                    idb.isc_info_user_names
                ]
            )
            #if you have more than 1 for SYSDBA, check if you have other connections to the test db!
            #check API guide page 28 for more info.
            self.assertDictEqual(res, {53: {'SYSDBA': 1}, 62: IBTEST_SQL_DIALECT, 14: 4096, 63: 0})
            res = con.db_info(idb.isc_info_read_seq_count)
            del res[0]  # remove this element (number of reads) because it changes often
            if 10 in res:
                del res[10]  # remove this element, because embedded version does not return it
            self.assertDictEqual(res, {1: 3, 6: 65, 32: 1})

    def test_connection(self):
        with closing(
                idb.connect(
                    user=IBTEST_USER,
                    password=IBTEST_PASSWORD,
                    database=IBTEST_DB_PATH,
                    host=IBTEST_HOST,
                    ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
                    server_public_file=IBTEST_SERVER_PUBLIC_FILE,
                    sql_dialect=IBTEST_SQL_DIALECT
                )
        ) as connection:
            cursor = connection.cursor()
            cursor.execute("CREATE TABLE test_ssl_table (number INTEGER)")
            connection.commit()

            cursor.execute("INSERT INTO test_ssl_table (number) VALUES (10)")
            cursor.execute("INSERT INTO test_ssl_table (number) VALUES (40)")
            connection.commit()

            cursor.execute("SELECT * FROM test_ssl_table")
            data = cursor.fetchall()

            self.assertEqual(len(data), 2)

            cursor.execute("DROP TABLE test_ssl_table")
            connection.commit()
