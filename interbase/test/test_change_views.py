# coding:utf-8
#
#   PROGRAM/MODULE: interbase
#   FILE:           test_change_views.py
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
from .constants import IBTEST_HOST, IBTEST_USER, IBTEST_PASSWORD, IBTEST_DB_PATH, IBTEST_SQL_DIALECT,\
    IBTEST_SERVER_PUBLIC_FILE


class TestChangeView(InterBaseTestBase):
    def setUp(self):
        self.cwd = os.getcwd()
        self.dbpath = os.path.join(self.cwd, "test")
        self.dbfile = os.path.join(self.dbpath, IBTEST_DB_PATH)
        self.con = interbase.connect(
            host=IBTEST_HOST,
            database=self.dbfile,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            isolation_level=interbase.ISOLATION_LEVEL_SERIALIZABLE,
            sql_dialect=IBTEST_SQL_DIALECT,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE
        )

    def test_table_subscription(self):
        cur = self.con.cursor()
        cur.execute(
            "CREATE TABLE CUSTOMER2 ("
            "CUST_NO INTEGER NOT NULL,"
            "CUSTOMER VARCHAR(25),"
            "CONSTRAINT RDB$PRIMARY2503 PRIMARY KEY(CUST_NO))"
        )
        self.con.commit()

        original_values = ((1, "first dummy string"), (2, "second dummy string"))
        for row in original_values:
            statement = f"INSERT INTO CUSTOMER2 (CUST_NO, CUSTOMER) VALUES ({row[0]}, '{row[1]}')"
            cur.execute(statement)
        self.con.commit()

        cur.execute(
            "CREATE SUBSCRIPTION SUB_CUSTOMER2_CHANGE ON CUSTOMER2 (CUST_NO, CUSTOMER)"
            "FOR ROW (INSERT, UPDATE, DELETE)"
        )
        cur.execute(
            f"GRANT SUBSCRIBE ON SUBSCRIPTION SUB_CUSTOMER2_CHANGE to {IBTEST_USER}"
        )
        self.con.execute_immediate("SET SUBSCRIPTION SUB_CUSTOMER2_CHANGE ACTIVE")
        self.con.commit()

        inserted_record = (3, "inserted string")
        statement = f"INSERT INTO CUSTOMER2 (CUST_NO, CUSTOMER) VALUES ({inserted_record[0]}, '{inserted_record[1]}')"
        self.con.execute_immediate(statement)
        self.con.commit()

        new_customer_string = "new dummy string"
        self.con.execute_immediate(
            f"UPDATE CUSTOMER2 SET CUSTOMER='{new_customer_string}' WHERE CUST_NO=2"
        )
        self.con.commit()

        deleted_record_id = 1
        statement = f"DELETE FROM CUSTOMER2 WHERE CUST_NO = {deleted_record_id}"
        self.con.execute_immediate(statement)
        self.con.commit()

        time.sleep(1)  # last operation takes time to appear in change_view?

        self.con.execute_immediate("SET SUBSCRIPTION SUB_CUSTOMER2_CHANGE ACTIVE")
        cur = self.con.cursor()
        statement = cur.prep("SELECT * FROM CUSTOMER2")
        cur.execute(statement)
        changed_records = cur.fetchall()

        statement.close()
        self.con.commit()
        self.con.close()

        changed_records.sort()

        deleted_record = changed_records[0]
        updated_record = changed_records[1]
        inserted_record = changed_records[2]

        assert updated_record[1][1] & interbase.SQLIND_UPDATE
        assert inserted_record[1][1] & interbase.SQLIND_INSERT
        assert deleted_record[1][1] & interbase.SQLIND_DELETE
        assert len(changed_records) == 3

    def tearDown(self):
        self.con = interbase.connect(
            host=IBTEST_HOST,
            database=self.dbfile,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            sql_dialect=IBTEST_SQL_DIALECT,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE
        )
        self.con.execute_immediate("DROP SUBSCRIPTION SUB_CUSTOMER2_CHANGE CASCADE")
        self.con.commit()
        self.con.execute_immediate("DROP TABLE CUSTOMER2")
        self.con.commit()
        self.con.close()
