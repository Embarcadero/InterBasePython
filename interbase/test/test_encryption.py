# coding:utf-8
#
#   PROGRAM/MODULE: interbase
#   FILE:           test_encryption.py
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
import interbase
import time

from .core import InterBaseTestBase
from .constants import IBTEST_HOST, IBTEST_USER, IBTEST_PASSWORD, IBTEST_DB_DIR_PATH, \
    IBTEST_SQL_DIALECT, IBTEST_SERVER_PUBLIC_FILE


class TestEncryption(InterBaseTestBase):
    def setUp(self) -> None:
        self.test_db_path = os.path.join(IBTEST_DB_DIR_PATH, "encrypt.ib")
        self.backup_file = os.path.join(IBTEST_DB_DIR_PATH, "backup.ib")
        self.encrypt_key = "test_key"
        self.protecred_enc_key = "protected_key"
        self.test_username, self.test_password = 'TEST_USER', 'masterkey'

        self.user_connection = None
        self.sysdba_connection = None
        self.sysdso_connection = None

        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

        self.sysdba_connection: interbase.Connection = interbase.create_database(
            host=IBTEST_HOST,
            database=self.test_db_path,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            sql_dialect=IBTEST_SQL_DIALECT,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE
        )
        self.sysdba_connection.execute_immediate("""CREATE USER SYSDSO SET PASSWORD '%s'""" % self.test_password)
        self.sysdba_connection.execute_immediate(
            """CREATE USER %s SET PASSWORD '%s'""" % (self.test_username, self.test_password)
        )
        self.sysdba_connection.execute_immediate(
            """CREATE USER %s SET PASSWORD '%s'""" % ('TEST_USER_2', 'TEST')
        )
        self.sysdba_connection.commit()

        self.sysdso_connection: interbase.Connection = interbase.connect(
            user='SYSDSO',
            password=self.test_password,
            database=self.test_db_path,
            sql_dialect=IBTEST_SQL_DIALECT,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE
        )
        self.user_connection: interbase.Connection = interbase.connect(
            user=self.test_username,
            password=self.test_password,
            database=self.test_db_path,
            sql_dialect=IBTEST_SQL_DIALECT,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE
        )

        self.sysdso_connection.execute_immediate("""ALTER DATABASE SET SYSTEM ENCRYPTION PASSWORD 'masterkey'""")
        self.sysdso_connection.execute_immediate("""CREATE ENCRYPTION %s FOR AES""" % self.encrypt_key)
        self.sysdso_connection.execute_immediate(
            """CREATE ENCRYPTION %s FOR AES PASSWORD 'masterkey'""" % self.protecred_enc_key
        )
        self.sysdso_connection.commit()

    def tearDown(self) -> None:
        self.sysdso_connection.close()
        self.user_connection.close()
        self.sysdba_connection.close()
        time.sleep(1)  # wait for the client lib to release the db file

        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

        if os.path.exists(self.backup_file):
            os.remove(self.backup_file)

    def test_encrypt_backup(self):
        with interbase.services.connect(
            host=IBTEST_HOST,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE,
        ) as service:
            service.backup(
                self.test_db_path,
                self.backup_file,
                sep_password="masterkey",
                encrypt_name=self.protecred_enc_key
            )
            self.assertTrue(os.path.exists(self.backup_file))
            service.wait()
            service.restore(
                self.backup_file,
                self.test_db_path,
                replace=1,
                sep_password="masterkey",
                decrypt_password="masterkey",
            )

    def test_encrypt_database(self):
        self.sysdso_connection.execute_immediate(
            """GRANT ENCRYPT ON ENCRYPTION %s TO SYSDBA""" % self.encrypt_key
        )
        self.sysdso_connection.commit()

        sysdba_cursor = self.sysdba_connection.cursor()
        sysdba_cursor.execute("""ALTER DATABASE ENCRYPT with %s""" % self.encrypt_key)
        self.sysdba_connection.commit()

        with self.assertRaises(interbase.ibcore.DatabaseError):
            # should raise exception because database is already encrypted
            sysdba_cursor.execute("""ALTER DATABASE ENCRYPT with %s""" % self.encrypt_key)

        conn: interbase.Connection = interbase.connect(
            dsn=self.test_db_path,
            user='TEST_USER_2',
            password='TEST',
            sql_dialect=IBTEST_SQL_DIALECT,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE
        )
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE v_table (number INTEGER)")
        conn.commit()
        conn.close()

    def test_encryption(self):
        self.sysdso_connection.execute_immediate(
            """CREATE TABLE user_table (number INTEGER ENCRYPT with %s decrypt default 10)""" % self.encrypt_key
        )
        self.sysdso_connection.commit()

        self.sysdso_connection.execute_immediate(
            """ALTER TABLE user_table ADD total_value INTEGER ENCRYPT with test_key"""
        )
        self.sysdso_connection.commit()

        self.sysdso_connection.execute_immediate(
            """CREATE TABLE test_table (number INTEGER ENCRYPT with test_key decrypt default 10)"""
        )
        self.sysdso_connection.execute_immediate(
            """GRANT INSERT, SELECT, DECRYPT (number) ON test_table TO %s""" % self.test_username
        )
        self.sysdso_connection.commit()

        self.user_connection.execute_immediate("""INSERT INTO test_table (number) VALUES (90)""")
        self.user_connection.execute_immediate("""INSERT INTO test_table (number) VALUES (15)""")
        self.user_connection.execute_immediate("""INSERT INTO test_table (number) VALUES (30)""")
        self.user_connection.commit()

        cursor = self.user_connection.cursor()
        cursor.execute("SELECT * FROM test_table")
        data = cursor.fetchall()

        self.assertEqual(len(data), 3)

        self.sysdso_connection.execute_immediate("""GRANT ENCRYPT ON ENCRYPTION test_key to SYSDBA;""")
        self.sysdso_connection.commit()

        self.sysdba_connection.execute_immediate(
            """CREATE TABLE T4 (number INTEGER ENCRYPT WITH test_key DECRYPT DEFAULT 10);"""
        )
        self.sysdba_connection.execute_immediate(
            """GRANT INSERT, SELECT ON TABLE T4 to %s;""" % self.test_username
        )
        self.sysdba_connection.commit()

        self.user_connection.execute_immediate("""INSERT INTO T4 (number) VALUES (77)""")
        self.user_connection.commit()

        user_cursor = self.user_connection.cursor()
        user_cursor.execute("SELECT * FROM T4")
        data = user_cursor.fetchone()
        self.assertEqual(data[0], 77)
        user_cursor.close()
