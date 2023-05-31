# coding:utf-8
#
#   PROGRAM/MODULE: idb
#   FILE:           test_services.py
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
from datetime import datetime
import idb

from sys import platform
from unittest import skipUnless, skip
from core import IDBTestBase
from contextlib import closing
from constants import IBTEST_HOST, IBTEST_PASSWORD, IBTEST_DB_PATH, \
    IBTEST_USER, IBTEST_DB_DIR_PATH, IBTEST_USE_EMBEDDED, IBTEST_SQL_DIALECT, IBTEST_SERVER_PUBLIC_FILE


class TestServices(IDBTestBase):
    def setUp(self):
        self.deleteTempFiles()

    def tearDown(self):
        pass
        #self.deleteTempFiles()

    def deleteTempFiles(self):
        files_to_delete = ['JOURNAL', 'DATABASE', 'ARCHIVE.IB']
        for filename in os.listdir(IBTEST_DB_DIR_PATH):
            if any([x in filename for x in files_to_delete]):
                os.remove(os.path.join(IBTEST_DB_DIR_PATH, filename))

    def test_attach(self):
        svc = idb.services.connect(
            host=IBTEST_HOST,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE
        )
        svc.close()

    def test_query(self):
        svc = idb.services.connect(host=IBTEST_HOST,
                                   user=IBTEST_USER,
                                   password=IBTEST_PASSWORD,
                                   ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
                                   server_public_file=IBTEST_SERVER_PUBLIC_FILE)

        self.assertEqual(svc.get_service_manager_version(), 2)
        if platform == 'win32':
            self.assertRegex(svc.get_server_version(), r"^W[IE]-V[\d\.]+")
        elif platform == 'darwin':
            self.assertIn('DW-V', svc.get_server_version())
        elif platform == 'linux':
            self.assertRegex(svc.get_server_version(), r"^L[IE]-V[\d\.]+")
        else:
            self.fail("Platform is not supported.")

        self.assertIn('InterBase', svc.get_architecture())

        self.assertIn('admin.ib', svc.get_security_database_path())

        x = svc.get_lock_file_directory()
        # self.assertEqual(x, '/opt/interbase/')

        x = svc.get_server_capabilities()
        self.assertIsInstance(x, type(tuple()))

        x = svc.get_message_file_directory()
        # self.assertEqual(x, '/opt/interbase/')

        _ = idb.connect(
            host=IBTEST_HOST,
            database=IBTEST_DB_PATH,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            sql_dialect=IBTEST_SQL_DIALECT,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE
        )
        _ = idb.connect(
            host=IBTEST_HOST,
            database=IBTEST_DB_PATH,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            sql_dialect=IBTEST_SQL_DIALECT,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE
        )

        self.assertGreaterEqual(len(svc.get_attached_database_names()), 2)
        self.assertIn(IBTEST_DB_PATH.upper(), [s.upper() for s in svc.get_attached_database_names()])
        # self.assertIn('/opt/interbase/',x)
        self.assertGreaterEqual(svc.get_connection_count(), 2)
        svc.close()

    def test_running(self):
        svc = idb.services.connect(host=IBTEST_HOST,
                                   user=IBTEST_USER,
                                   password=IBTEST_PASSWORD,
                                   ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
                                   server_public_file=IBTEST_SERVER_PUBLIC_FILE)
        self.assertFalse(svc.isrunning())
        svc.get_log()
        self.assertTrue(svc.fetching)
        # fetch materialized
        log = svc.readlines()
        self.assertFalse(svc.isrunning())
        svc.close()

    def test_alias(self):
        svc = idb.services.connect(
            host=IBTEST_HOST,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE
        )
        test_alias_name = "test_alias"
        aliases = svc.get_db_alias()
        if aliases.get(test_alias_name):
            svc.delete_db_alias(test_alias_name)
            aliases = svc.get_db_alias()
            self.assertIsNone(aliases.get(test_alias_name))

        svc.add_db_alias(test_alias_name, IBTEST_DB_PATH)
        svc.wait()
        aliases = svc.get_db_alias()

        self.assertIsNotNone(aliases.get(test_alias_name))
        self.assertEqual(IBTEST_DB_PATH, aliases.get(test_alias_name))

        svc.delete_db_alias(test_alias_name)
        aliases = svc.get_db_alias()

        self.assertIsNone(aliases.get(test_alias_name))
        svc.close()

    @skipUnless(not IBTEST_USE_EMBEDDED, "Embedded client does not support this feature: Journal and Online dump")
    def test_create_db_dump(self):
        dump_path = os.path.join(IBTEST_DB_DIR_PATH, 'test_dump.ib')
        db_path = os.path.join(IBTEST_DB_DIR_PATH, 'test_db.ib')

        if os.path.exists(dump_path):
            os.remove(dump_path)
        if os.path.exists(db_path):
            os.remove(db_path)

        connection = idb.create_database(
            host=IBTEST_HOST,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            database=db_path,
            sql_dialect=IBTEST_SQL_DIALECT,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE,
        )
        connection.close()

        svc = idb.services.connect(
            host=IBTEST_HOST,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE,
        )
        svc.create_dump(db_path, dump_path)

        svc.wait()

        self.assertTrue(os.path.exists(dump_path))
        svc.close()

    @skipUnless(not IBTEST_USE_EMBEDDED, "Embedded client does not support this feature: Journal and Online dump")
    def test_overwrite_dump(self):
        dump_path = os.path.join(IBTEST_DB_DIR_PATH, 'test_overwrite.ib')
        db_path = os.path.join(IBTEST_DB_DIR_PATH, 'temp.ib')

        if os.path.exists(dump_path):
            os.remove(dump_path)
        if os.path.exists(db_path):
            os.remove(db_path)

        connection = idb.create_database(
            host=IBTEST_HOST,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            database=db_path,
            sql_dialect=IBTEST_SQL_DIALECT,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE,
        )
        connection.close()

        svc = idb.services.connect(
            host=IBTEST_HOST,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE,
        )
        svc.create_dump(db_path, dump_path, overwrite=True)

    def test_ssl_connection(self):
        svc = idb.services.connect(
            host=IBTEST_HOST,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE,
        )
        svc.close()
        svc = idb.services.connect(
            host=IBTEST_HOST,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            client_pass_phrase="masterkey",
            server_public_file=IBTEST_SERVER_PUBLIC_FILE,
        )
        svc.close()

    @skip("issue #49: client lib ignores server_public_path")
    def test_ssl_with_server_public_path(self):
        svc = idb.services.connect(
            host=IBTEST_HOST,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE,
        )
        svc.close()
        svc = idb.services.connect(
            host=IBTEST_HOST,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            client_pass_phrase="masterkey",
            server_public_file=IBTEST_SERVER_PUBLIC_FILE,
        )
        svc.close()

    def test_wait(self):
        svc = idb.services.connect(
            host=IBTEST_HOST,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE,
        )
        self.assertFalse(svc.isrunning())
        svc.get_log()
        self.assertTrue(svc.fetching)
        svc.wait()
        self.assertFalse(svc.isrunning())
        self.assertFalse(svc.fetching)
        svc.close()

    @skipUnless(not IBTEST_USE_EMBEDDED, "Embedded client does not support this feature: Journal and Online dump")
    def test_archive(self):
        temp_db_path = os.path.join(IBTEST_DB_DIR_PATH, "ARCHIVE.IB")

        connection = idb.create_database(
            host=IBTEST_HOST,
            database=temp_db_path,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            sql_dialect=IBTEST_SQL_DIALECT,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE,
        )
        connection.execute_immediate("""CREATE TABLE T1 (number INTEGER)""")
        connection.commit()
        connection.execute_immediate("""INSERT INTO T1 (number) VALUES (1)""")
        connection.commit()
        connection.execute_immediate("""CREATE JOURNAL '%s'""" % (IBTEST_DB_DIR_PATH + '/'))
        connection.execute_immediate("""CREATE JOURNAL ARCHIVE '%s'""" % IBTEST_DB_DIR_PATH)
        connection.commit()

        save_point_1 = datetime.now()
        with idb.services.connect(host=IBTEST_HOST,
                                  user=IBTEST_USER,
                                  password=IBTEST_PASSWORD,
                                  ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
                                  server_public_file=IBTEST_SERVER_PUBLIC_FILE
                                  ) as service:
            service.archive_backup(temp_db_path)
            service.wait()

        with idb.services.connect(host=IBTEST_HOST,
                                  user=IBTEST_USER,
                                  password=IBTEST_PASSWORD,
                                  ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
                                  server_public_file=IBTEST_SERVER_PUBLIC_FILE
                                  ) as service:
            for filename in os.listdir(IBTEST_DB_DIR_PATH):
                if '1.DATABASE' in filename:
                    service.archive_restore(os.path.join(IBTEST_DB_DIR_PATH, filename),
                                            temp_db_path + ".restored", save_point_1)

        new_connection = idb.connect(
            host=IBTEST_HOST,
            database=temp_db_path + '.restored',
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            sql_dialect=IBTEST_SQL_DIALECT,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE
        )

        cursor = new_connection.cursor()
        cursor.execute("""SELECT * FROM T1""")
        data = cursor.fetchall()
        self.assertEqual(1, len(data))
        cursor.close()
        new_connection.close()

    def test_tablespace(self):
        temp_db_path = os.path.join(IBTEST_DB_DIR_PATH, 'tablespace.ib')
        table_space_file = os.path.join(IBTEST_DB_DIR_PATH, 'tablespace.its')
        table_space_bk_file = os.path.join(IBTEST_DB_DIR_PATH, 'tablespace.itbk')

        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)
        if os.path.exists(table_space_file):
            os.remove(table_space_file)
        if os.path.exists(table_space_bk_file):
            os.remove(table_space_bk_file)

        with closing(
            idb.create_database(
                host=IBTEST_HOST,
                database=temp_db_path,
                user=IBTEST_USER,
                password=IBTEST_PASSWORD,
                ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
                server_public_file=IBTEST_SERVER_PUBLIC_FILE,
                sql_dialect=IBTEST_SQL_DIALECT
            )
        ) as connection:
            cursor = connection.cursor()
            cursor.execute("""CREATE TABLESPACE MYTABLESPACE FILE '%s'""" % table_space_file)
            connection.commit()

        with idb.services.connect(host=IBTEST_HOST,
                                  user=IBTEST_USER,
                                  password=IBTEST_PASSWORD,
                                  ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
                                  server_public_file=IBTEST_SERVER_PUBLIC_FILE
                                  ) as service:
            service.backup_tablespace(temp_db_path, 'MYTABLESPACE', table_space_bk_file)
            self.assertTrue(os.path.exists(table_space_bk_file))

class TestServices2(IDBTestBase):
    def setUp(self):
        self.ibk = os.path.join(IBTEST_DB_DIR_PATH, 'test_employee.ibk')
        self.ibk2 = os.path.join(IBTEST_DB_DIR_PATH, 'test_employee.ibk2')
        self.ridb = os.path.join(IBTEST_DB_DIR_PATH, 'test_employee.ib')
        self.svc = idb.services.connect(
            host=IBTEST_HOST,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE,
        )
        self.con = idb.connect(
            host=IBTEST_HOST,
            database=IBTEST_DB_PATH,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            sql_dialect=IBTEST_SQL_DIALECT,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE
        )
        if not os.path.exists(self.ridb):
            c = idb.create_database(
                host=IBTEST_HOST,
                database=self.ridb,
                user=IBTEST_USER,
                password=IBTEST_PASSWORD,
                sql_dialect=IBTEST_SQL_DIALECT,
                ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
                server_public_file=IBTEST_SERVER_PUBLIC_FILE
            )
            c.close()

    def tearDown(self):
        self.svc.close()
        self.con.execute_immediate("delete from t")
        self.con.commit()
        self.con.close()
        if os.path.exists(self.ridb):
            os.remove(self.ridb)
        if os.path.exists(self.ibk):
            os.remove(self.ibk)
        if os.path.exists(self.ibk2):
            os.remove(self.ibk2)

    def test_log(self):

        def fetchline(line):
            output.append(line)

        self.svc.get_log()
        self.assertTrue(self.svc.fetching)
        # fetch materialized
        log = self.svc.readlines()
        self.assertFalse(self.svc.fetching)
        self.assertTrue(log)
        self.assertIsInstance(log, type(list()))
        # iterate over result
        self.svc.get_log()
        for line in self.svc:
            self.assertIsNotNone(line)
            self.assertIsInstance(line, idb.StringType)
        self.assertFalse(self.svc.fetching)
        # callback
        output = []
        self.svc.get_log(callback=fetchline)
        self.assertGreater(len(output), 0)

    def test_get_limbo_transactions_ids(self):
        ids = self.svc.get_limbo_transaction_ids(self.ridb)
        self.assertIsInstance(ids, type(list()))

    def test_getStatistics(self):
        def fetchline(line):
            output.append(line)

        self.svc.get_statistics(self.ridb)
        self.assertTrue(self.svc.fetching)
        self.assertTrue(self.svc.isrunning())
        # fetch materialized
        stats = self.svc.readlines()
        self.assertFalse(self.svc.fetching)
        self.assertFalse(self.svc.isrunning())
        self.assertIsInstance(stats, type(list()))
        # iterate over result
        self.svc.get_statistics(self.ridb,
                                show_system_tables_and_indexes=True,
                                show_record_versions=True)
        for line in self.svc:
            self.assertIsInstance(line, idb.StringType)
        self.assertFalse(self.svc.fetching)
        # callback
        output = []
        self.svc.get_statistics(self.ridb, callback=fetchline)
        self.assertGreater(len(output), 0)

    def test_backup(self):
        def fetchline(line):
            output.append(line)

        self.svc.backup(self.ridb, self.ibk)
        self.assertTrue(self.svc.fetching)
        self.assertTrue(self.svc.isrunning())
        # fetch materialized
        report = self.svc.readlines()
        self.assertFalse(self.svc.fetching)
        self.assertFalse(self.svc.isrunning())
        self.assertTrue(os.path.exists(self.ibk))
        self.assertIsInstance(report, type(list()))
        self.assertIsInstance(report, type(list()))
        # iterate over result
        self.svc.backup(
            self.ridb,
            self.ibk,
            ignore_checksums=1,
            ignore_limbo_transactions=1,
            metadata_only=1,
            collect_garbage=0,
            transportable=0,
            convert_external_tables_to_internal=1,
            compressed=0,
            no_db_triggers=0
        )
        for line in self.svc:
            self.assertIsNotNone(line)
            self.assertIsInstance(line, idb.StringType)
        self.assertFalse(self.svc.fetching)
        # callback
        output = []
        self.svc.backup(self.ridb, self.ibk, callback=fetchline)
        self.assertGreater(len(output), 0)

    def test_restore(self):
        def fetchline(line):
            output.append(line)

        output = []
        self.svc.backup(self.ridb, self.ibk, callback=fetchline)
        self.assertTrue(os.path.exists(self.ibk))
        self.svc.restore(self.ibk, self.ridb, replace=1)
        self.assertTrue(self.svc.fetching)
        self.assertTrue(self.svc.isrunning())
        # fetch materialized
        report = self.svc.readlines()
        self.assertFalse(self.svc.fetching)
        self.assertFalse(self.svc.isrunning())
        self.assertIsInstance(report, type(list()))
        # iterate over result
        self.svc.restore(self.ibk, self.ridb, replace=1)
        for line in self.svc:
            self.assertIsNotNone(line)
            self.assertIsInstance(line, idb.StringType)
        self.assertFalse(self.svc.fetching)
        # callback
        output = []
        self.svc.restore(self.ibk, self.ridb, replace=1, callback=fetchline)
        self.assertGreater(len(output), 0)

    def test_setDefaultPageBuffers(self):
        self.svc.set_default_page_buffers(self.ridb, 100)

    def test_setSweepInterval(self):
        self.svc.set_sweep_interval(self.ridb, 10000)

    def test_setShouldReservePageSpace(self):
        self.svc.set_reserve_page_space(self.ridb, False)
        self.svc.get_statistics(self.ridb, show_only_db_header_pages=1)
        self.assertIn('no reserve', ''.join(self.svc.readlines()))
        self.svc.set_reserve_page_space(self.ridb, True)
        self.svc.get_statistics(self.ridb, show_only_db_header_pages=1)
        self.assertNotIn('no reserve', ''.join(self.svc.readlines()))

    def test_setWriteMode(self):
        # Forced writes
        self.svc.set_write_mode(self.ridb, idb.services.WRITE_FORCED)
        self.svc.get_statistics(self.ridb, show_only_db_header_pages=1)
        self.assertIn('force write', ''.join(self.svc.readlines()))
        # No Forced writes
        self.svc.set_write_mode(self.ridb, idb.services.WRITE_BUFFERED)
        self.svc.get_statistics(self.ridb, show_only_db_header_pages=1)
        self.assertNotIn('force write', ''.join(self.svc.readlines()))

    def test_setAccessMode(self):
        # Read Only
        self.svc.set_access_mode(self.ridb, idb.services.ACCESS_READ_ONLY)
        self.svc.get_statistics(self.ridb, show_only_db_header_pages=1)
        self.assertIn('read only', ''.join(self.svc.readlines()))
        # Read/Write
        self.svc.set_access_mode(self.ridb, idb.services.ACCESS_READ_WRITE)
        self.svc.get_statistics(self.ridb, show_only_db_header_pages=1)
        self.assertNotIn('read only', ''.join(self.svc.readlines()))

    def test_setSQLDialect(self):
        self.svc.set_sql_dialect(self.ridb, 1)
        self.svc.get_statistics(self.ridb, show_only_db_header_pages=1)
        self.assertIn('Database dialect\t 1', ''.join(self.svc.readlines()))
        self.svc.set_sql_dialect(self.ridb, 3)
        self.svc.get_statistics(self.ridb, show_only_db_header_pages=1)
        self.assertIn('Database dialect\t 3', ''.join(self.svc.readlines()))

    def test_activateShadowFile(self):
        self.svc.activate_shadow(self.ridb)

    def test_sweep(self):
        self.svc.sweep(self.ridb)

    def test_repair(self):
        result = self.svc.repair(self.ridb)
        self.assertFalse(result)

    def test_getUsers(self):
        users = [user for user in self.svc.get_users() if user.name == 'SYSDBA']
        self.assertIsInstance(users, type(list()))
        self.assertIsInstance(users[0], idb.services.User)
        self.assertEqual(users[0].name, 'SYSDBA')

    def test_manage_user(self):
        user = idb.services.User('IDB_TEST')
        user.password = 'IDB_TEST'
        user.first_name = 'IDB'
        user.middle_name = 'X.'
        user.last_name = 'TEST'
        self.svc.add_user(user)
        self.assertTrue(self.svc.user_exists(user))
        self.assertTrue(self.svc.user_exists('IDB_TEST'))
        users = [user for user in self.svc.get_users() if user.name == 'IDB_TEST']
        self.assertIsNotNone(users)
        self.assertEqual(len(users), 1)
        # self.assertEqual(users[0].password,'IDB_TEST')
        self.assertEqual(users[0].first_name, 'IDB')
        self.assertEqual(users[0].middle_name, 'X.')
        self.assertEqual(users[0].last_name, 'TEST')
        user.password = 'XIDB_TEST'
        user.first_name = 'XIDB'
        user.middle_name = 'XX.'
        user.last_name = 'XTEST'
        self.svc.modify_user(user)
        users = [user for user in self.svc.get_users() if user.name == 'IDB_TEST']
        self.assertTrue(users)
        self.assertEqual(len(users), 1)
        # self.assertEqual(users[0].password,'XIDB_TEST')
        self.assertEqual(users[0].first_name, 'XIDB')
        self.assertEqual(users[0].middle_name, 'XX.')
        self.assertEqual(users[0].last_name, 'XTEST')
        self.svc.remove_user(user)
        self.assertFalse(self.svc.user_exists('IDB_TEST'))
