# coding:utf-8
#
#   PROGRAM/MODULE: interbase
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

import interbase
import decimal
import datetime

from core import InterbaseTestBase
from constants import IBTEST_USER, IBTEST_HOST, IBTEST_PASSWORD, IBTEST_DB_PATH, IBTEST_SQL_DIALECT,\
    IBTEST_SERVER_PUBLIC_FILE


class TestInsertData(InterbaseTestBase):
    def setUp(self):
        self.con = interbase.connect(
            host=IBTEST_HOST,
            database=IBTEST_DB_PATH,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            sql_dialect=IBTEST_SQL_DIALECT,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE
        )
        self.con2 = interbase.connect(
            host=IBTEST_HOST,
            database=IBTEST_DB_PATH,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            charset='UTF8',
            sql_dialect=IBTEST_SQL_DIALECT,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE
        )

    def tearDown(self):
        self.con2.close()
        self.con.execute_immediate("delete from t")
        self.con.execute_immediate("delete from t2")
        self.con.commit()
        self.con.close()

    def test_insert_integers(self):
        cur = self.con.cursor()
        cur.execute('insert into T2 (C1,C2,C3) values (?,?,?)', [1, 1, 1])
        self.con.commit()
        cur.execute('select C1,C2,C3 from T2 where C1 = 1')
        rows = cur.fetchall()
        self.assertListEqual(rows, [(1, 1, 1)])
        cur.execute(
            'insert into T2 (C1,C2,C3) values (?,?,?)',
            [2, 1, 2147483647]
        )
        cur.execute(
            'insert into T2 (C1,C2,C3) values (?,?,?)',
            [2, 1, -2147483647 - 1]
        )
        self.con.commit()
        cur.execute('select C1,C2,C3 from T2 where C1 = 2')
        rows = cur.fetchall()
        self.assertListEqual(
            rows,
            [(2, 1, 2147483647), (2, 1, -2147483648)]
        )

    def test_insert_char_varchar(self):
        cur = self.con.cursor()
        cur.execute('insert into T2 (C1,C4,C5) values (?,?,?)', [2, 'AA', 'AA'])
        self.con.commit()
        cur.execute('select C1,C4,C5 from T2 where C1 = 2')
        rows = cur.fetchall()
        self.assertListEqual(rows, [(2, 'AA   ', 'AA')])
        # Too long values
        with self.assertRaises(ValueError) as cm:
            cur.execute('insert into T2 (C1,C4) values (?,?)', [3, '🐍🐍🐍🐍🐍🐍'])
            self.con.commit()
        self.assertTupleEqual(
            cm.exception.args,
            ('Value of parameter (1) is too long, expected 20, found 24',)
        )
        with self.assertRaises(ValueError) as cm:
            cur.execute('insert into T2 (C1,C5) values (?,?)', [3, '🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍'])
            self.con.commit()
        self.assertTupleEqual(
            cm.exception.args,
            ('Value of parameter (1) is too long, expected 40, found 44',)
        )

    def test_insert_datetime(self):
        cur = self.con.cursor()
        now = datetime.datetime(2011, 11, 13, 15, 00, 1, 200)
        time = now.time() if IBTEST_SQL_DIALECT == 3 else now.date()
        cur.execute('insert into T2 (C1,C6,C7,C8) values (?,?,?,?)',
                    [3, now.date(), time, now])
        self.con.commit()
        cur.execute('select C1,C6,C7,C8 from T2 where C1 = 3')
        rows = cur.fetchall()
        self.assertListEqual(
            rows,
            [
                (
                    3,
                    datetime.date(2011, 11, 13) if IBTEST_SQL_DIALECT == 3 else datetime.datetime(2011, 11, 13),
                    datetime.time(15, 0, 1, 200) if IBTEST_SQL_DIALECT == 3 else datetime.datetime(2011, 11, 13),
                    datetime.datetime(2011, 11, 13, 15, 0, 1, 200)
                )
            ]
        )

        cur.execute(
            'insert into T2 (C1,C6,C7,C8) values (?,?,?,?)',
            [4, '2011-11-13',
             '15:0:1:200' if IBTEST_SQL_DIALECT == 3 else '2011-11-13',
             '2011-11-13 15:0:1:200']
        )
        self.con.commit()
        cur.execute('select C1,C6,C7,C8 from T2 where C1 = 4')
        rows = cur.fetchall()
        self.assertListEqual(
            rows,
            [
                (4,
                 datetime.date(2011, 11, 13) if IBTEST_SQL_DIALECT == 3 else datetime.datetime(2011, 11, 13),
                 datetime.time(15, 0, 1, 200000) if IBTEST_SQL_DIALECT == 3 else datetime.datetime(2011, 11, 13),
                datetime.datetime(2011, 11, 13, 15, 0, 1, 200000))
            ]
        )

    def test_insert_blob(self):
        cur = self.con.cursor()
        cur2 = self.con2.cursor()
        cur.execute('insert into T2 (C1,C9) values (?,?)', [4, 'This is a BLOB!'])
        cur.transaction.commit()
        cur.execute('select C1,C9 from T2 where C1 = 4')
        rows = cur.fetchall()
        self.assertListEqual(rows, [(4, 'This is a BLOB!')])
        # Non-textual BLOB
        blob_data = interbase.bs([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        cur.execute('insert into T2 (C1,C16) values (?,?)', [8, blob_data])
        cur.transaction.commit()
        cur.execute('select C1,C16 from T2 where C1 = 8')
        rows = cur.fetchall()
        self.assertListEqual(rows, [(8, blob_data)])
        # BLOB bigger than max. segment size
        big_blob = '123456789' * 10000
        cur.execute('insert into T2 (C1,C9) values (?,?)', [5, big_blob])
        cur.transaction.commit()
        cur.execute('select C1,C9 from T2 where C1 = 5')
        row = cur.fetchone()
        self.assertEqual(row[1], big_blob)
        # Unicode in BLOB
        blob_text = 'This is a BLOB!'
        if not isinstance(blob_text, interbase.ibase.myunicode):
            blob_text = blob_text.decode('utf-8')
        cur2.execute('insert into T2 (C1,C9) values (?,?)', [6, blob_text])
        cur2.transaction.commit()
        cur2.execute('select C1,C9 from T2 where C1 = 6')
        rows = cur2.fetchall()
        self.assertListEqual(rows, [(6, blob_text)])
        # Unicode non-textual BLOB
        with self.assertRaises(TypeError) as cm:
            cur2.execute('insert into T2 (C1,C16) values (?,?)', [7, blob_text])
        self.assertTupleEqual(
            cm.exception.args,
            ("Unicode strings are not acceptable input for a non-textual BLOB column.",)
        )

    def test_insert_float_double(self):
        cur = self.con.cursor()
        cur.execute('insert into T2 (C1,C12,C13) values (?,?,?)', [5, 1.0, 1.0])
        self.con.commit()
        cur.execute('select C1,C12,C13 from T2 where C1 = 5')
        rows = cur.fetchall()
        self.assertListEqual(rows, [(5, 1.0, 1.0)])
        cur.execute('insert into T2 (C1,C12,C13) values (?,?,?)', [6, 1, 1])
        self.con.commit()
        cur.execute('select C1,C12,C13 from T2 where C1 = 6')
        rows = cur.fetchall()
        self.assertListEqual(rows, [(6, 1.0, 1.0)])

    def test_insert_numeric_decimal(self):
        cur = self.con.cursor()
        cur.execute('insert into T2 (C1,C10,C11) values (?,?,?)', [6, 1.1, 1.1])
        cur.execute(
            'insert into T2 (C1,C10,C11) values (?,?,?)',
            [6, decimal.Decimal('100.11'), decimal.Decimal('100.11')]
        )
        self.con.commit()
        cur.execute('select C1,C10,C11 from T2 where C1 = 6')
        rows = cur.fetchall()
        self.assertListEqual(
            rows,
            [
                (
                    6,
                    decimal.Decimal('1.1') if IBTEST_SQL_DIALECT == 3 else 1.1,
                    decimal.Decimal('1.1') if IBTEST_SQL_DIALECT == 3 else 1.1
                 ),
                (
                    6,
                    decimal.Decimal('100.11') if IBTEST_SQL_DIALECT == 3 else 100.11,
                    decimal.Decimal('100.11') if IBTEST_SQL_DIALECT == 3 else 100.11
                )
            ]
        )

