# coding:utf-8
#
#   PROGRAM/MODULE: interbase
#   FILE:           test_cursor.py
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

from core import InterBaseTestBase
from constants import IBTEST_PASSWORD, IBTEST_USER, IBTEST_HOST, \
    IBTEST_DB_PATH, IBTEST_USE_EMBEDDED, IBTEST_SQL_DIALECT, IBTEST_SERVER_PUBLIC_FILE


class TestCursor(InterBaseTestBase):
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

    def tearDown(self):
        self.con.execute_immediate("delete from t")
        self.con.commit()
        self.con.close()

    def test_iteration(self):
        data = [
            ('USA', 'Dollar'), ('England', 'Pound'), ('Canada', 'CdnDlr'),
            ('Switzerland', 'SFranc'), ('Japan', 'Yen'), ('Italy', 'Lira'),
            ('France', 'FFranc'), ('Germany', 'D-Mark'), ('Australia', 'ADollar'),
            ('Hong Kong', 'HKDollar'), ('Netherlands', 'Guilder'),
            ('Belgium', 'BFranc'), ('Austria', 'Schilling'), ('Fiji', 'FDollar')
        ]
        cur = self.con.cursor()
        cur.execute('select * from country')
        rows = [row for row in cur]
        self.assertEqual(len(rows), 14)
        self.assertListEqual(
            rows,
            [
                ('USA', 'Dollar'), ('England', 'Pound'), ('Canada', 'CdnDlr'),
                ('Switzerland', 'SFranc'), ('Japan', 'Yen'), ('Italy', 'Lira'),
                ('France', 'FFranc'), ('Germany', 'D-Mark'), ('Australia', 'ADollar'),
                ('Hong Kong', 'HKDollar'), ('Netherlands', 'Guilder'),
                ('Belgium', 'BFranc'), ('Austria', 'Schilling'), ('Fiji', 'FDollar')
            ]
        )
        cur.execute('select * from country')
        rows = []
        for row in cur:
            rows.append(row)

        self.assertEqual(len(rows), 14)
        self.assertListEqual(
            rows,
            [
                ('USA', 'Dollar'), ('England', 'Pound'), ('Canada', 'CdnDlr'),
                ('Switzerland', 'SFranc'), ('Japan', 'Yen'), ('Italy', 'Lira'),
                ('France', 'FFranc'), ('Germany', 'D-Mark'), ('Australia', 'ADollar'),
                ('Hong Kong', 'HKDollar'), ('Netherlands', 'Guilder'),
                ('Belgium', 'BFranc'), ('Austria', 'Schilling'), ('Fiji', 'FDollar')
            ]
        )
        cur.execute('select * from country')
        i = 0
        for row in cur:
            i += 1
            self.assertIn(row,data)
        self.assertEqual(i, 14)

    def test_description(self):
        cursor = self.con.cursor()
        cursor.execute('select * from country')
        self.assertEqual(len(cursor.description), 2)
        self.assertEqual(
            repr(cursor.description),
            "(('COUNTRY', <class 'str'>, 60, 60, 0, 0, False),"
            " ('CURRENCY', <class 'str'>, 40, 40, 0, 0, False))"
        )

        cursor.execute('select country as CT, currency as CUR from country')
        self.assertEqual(len(cursor.description), 2)
        cursor.execute('select * from customer')

        self.assertEqual(
            repr(cursor.description),
            "(('CUST_NO', <class 'int'>, 11, 4, 0, 0, False), "
            "('CUSTOMER', <class 'str'>, 100, 100, 0, 0, False), "
            "('CONTACT_FIRST', <class 'str'>, 60, 60, 0, 0, True), "
            "('CONTACT_LAST', <class 'str'>, 80, 80, 0, 0, True), "
            "('PHONE_NO', <class 'str'>, 80, 80, 0, 0, True), "
            "('ADDRESS_LINE1', <class 'str'>, 120, 120, 0, 0, True), "
            "('ADDRESS_LINE2', <class 'str'>, 120, 120, 0, 0, True), "
            "('CITY', <class 'str'>, 100, 100, 0, 0, True), "
            "('STATE_PROVINCE', <class 'str'>, 60, 60, 0, 0, True), "
            "('COUNTRY', <class 'str'>, 60, 60, 0, 0, True), "
            "('POSTAL_CODE', <class 'str'>, 48, 48, 0, 0, True), "
            "('ON_HOLD', <class 'str'>, 4, 4, 0, 0, True))"
        )

        cursor.execute('select * from job')

        self.assertEqual(
            repr(cursor.description),
            "(('JOB_CODE', <class 'str'>, 20, 20, 0, 0, False), "
            "('JOB_GRADE', <class 'int'>, 6, 2, 0, 0, False), "
            "('JOB_COUNTRY', <class 'str'>, 60, 60, 0, 0, False), "
            "('JOB_TITLE', <class 'str'>, 100, 100, 0, 0, False), "
            "('MIN_SALARY', <class 'decimal.Decimal'>, " +
            ("20, 8, 10" if IBTEST_SQL_DIALECT == 3 else "17, 8, None") + ", -2, False), "
            "('MAX_SALARY', <class 'decimal.Decimal'>, " +
            ("20, 8, 10" if IBTEST_SQL_DIALECT == 3 else "17, 8, None") + ", -2, False), "
            "('JOB_REQUIREMENT', <class 'str'>, 0, 8, 0, 1, True), "
            "('LANGUAGE_REQ', <class 'list'>, -1, 8, 0, 0, True))"
        )

        cursor.execute('select * from proj_dept_budget')
        self.assertEqual(
            repr(cursor.description),
            "(('FISCAL_YEAR', <class 'int'>, 11, 4, 0, 0, False), "
            "('PROJ_ID', <class 'str'>, 20, 20, 0, 0, False), "
            "('DEPT_NO', <class 'str'>, 12, 12, 0, 0, False), "
            "('QUART_HEAD_CNT', <class 'list'>, -1, 8, 0, 0, True), "
            "('PROJECTED_BUDGET', <class 'decimal.Decimal'>, " +
            ("20, 8, 12" if IBTEST_SQL_DIALECT == 3 else "17, 8, None") + ", -2, True))"
        )
        # Check for precision cache
        cur2 = self.con.cursor()
        cur2.execute('select * from proj_dept_budget')

        self.assertEqual(
            repr(cur2.description),
            "(('FISCAL_YEAR', <class 'int'>, 11, 4, 0, 0, False), "
            "('PROJ_ID', <class 'str'>, 20, 20, 0, 0, False), "
            "('DEPT_NO', <class 'str'>, 12, 12, 0, 0, False), "
            "('QUART_HEAD_CNT', <class 'list'>, -1, 8, 0, 0, True), "
            "('PROJECTED_BUDGET', <class 'decimal.Decimal'>, " +
            ("20, 8, 12" if IBTEST_SQL_DIALECT == 3 else "17, 8, None") + ", -2, True))"
        )

    def test_exec_after_close(self):
        cur = self.con.cursor()
        cur.execute('select * from country')
        row = cur.fetchone()
        self.assertTupleEqual(row, ('USA', 'Dollar'))
        cur.close()
        cur.execute('select * from country')
        row = cur.fetchone()
        self.assertTupleEqual(row, ('USA', 'Dollar'))

    def test_fetchone(self):
        cur = self.con.cursor()
        cur.execute('select * from country')
        row = cur.fetchone()
        self.assertTupleEqual(row, ('USA', 'Dollar'))

    def test_fetchall(self):
        cur = self.con.cursor()
        cur.execute('select * from country')
        rows = cur.fetchall()
        self.assertListEqual(
            rows,
            [
                ('USA', 'Dollar'), ('England', 'Pound'), ('Canada', 'CdnDlr'),
                ('Switzerland', 'SFranc'), ('Japan', 'Yen'), ('Italy', 'Lira'),
                ('France', 'FFranc'), ('Germany', 'D-Mark'), ('Australia', 'ADollar'),
                ('Hong Kong', 'HKDollar'), ('Netherlands', 'Guilder'),
                ('Belgium', 'BFranc'), ('Austria', 'Schilling'), ('Fiji', 'FDollar')
            ]
        )

    def test_fetchmany(self):
        cur = self.con.cursor()
        cur.execute('select * from country')
        rows = cur.fetchmany(10)
        self.assertListEqual(
            rows,
            [
                ('USA', 'Dollar'), ('England', 'Pound'), ('Canada', 'CdnDlr'),
                ('Switzerland', 'SFranc'), ('Japan', 'Yen'), ('Italy', 'Lira'),
                ('France', 'FFranc'), ('Germany', 'D-Mark'), ('Australia', 'ADollar'),
                ('Hong Kong', 'HKDollar')
            ]
        )
        rows = cur.fetchmany(10)
        self.assertListEqual(
            rows,
            [
                ('Netherlands', 'Guilder'), ('Belgium', 'BFranc'),
                ('Austria', 'Schilling'), ('Fiji', 'FDollar')
            ]
        )
        rows = cur.fetchmany(10)
        self.assertEqual(len(rows), 0)

    def test_fetchonemap(self):
        cur = self.con.cursor()
        cur.execute('select * from country')
        row = cur.fetchonemap()
        self.assertListEqual(row.items(), [('COUNTRY', 'USA'), ('CURRENCY', 'Dollar')])

    def test_fetchallmap(self):
        cur = self.con.cursor()
        cur.execute('select * from country')
        rows = cur.fetchallmap()
        self.assertListEqual(
            [row.items() for row in rows],
            [
                [('COUNTRY', 'USA'), ('CURRENCY', 'Dollar')],
                [('COUNTRY', 'England'), ('CURRENCY', 'Pound')],
                [('COUNTRY', 'Canada'), ('CURRENCY', 'CdnDlr')],
                [('COUNTRY', 'Switzerland'), ('CURRENCY', 'SFranc')],
                [('COUNTRY', 'Japan'), ('CURRENCY', 'Yen')],
                [('COUNTRY', 'Italy'), ('CURRENCY', 'Lira')],
                [('COUNTRY', 'France'), ('CURRENCY', 'FFranc')],
                [('COUNTRY', 'Germany'), ('CURRENCY', 'D-Mark')],
                [('COUNTRY', 'Australia'), ('CURRENCY', 'ADollar')],
                [('COUNTRY', 'Hong Kong'), ('CURRENCY', 'HKDollar')],
                [('COUNTRY', 'Netherlands'), ('CURRENCY', 'Guilder')],
                [('COUNTRY', 'Belgium'), ('CURRENCY', 'BFranc')],
                [('COUNTRY', 'Austria'), ('CURRENCY', 'Schilling')],
                [('COUNTRY', 'Fiji'), ('CURRENCY', 'FDollar')]
            ]
        )

    def test_fetchmanymap(self):
        cur = self.con.cursor()
        cur.execute('select * from country')
        rows = cur.fetchmanymap(10)
        self.assertListEqual(
            [row.items() for row in rows],
            [
                [('COUNTRY', 'USA'), ('CURRENCY', 'Dollar')],
                [('COUNTRY', 'England'), ('CURRENCY', 'Pound')],
                [('COUNTRY', 'Canada'), ('CURRENCY', 'CdnDlr')],
                [('COUNTRY', 'Switzerland'), ('CURRENCY', 'SFranc')],
                [('COUNTRY', 'Japan'), ('CURRENCY', 'Yen')],
                [('COUNTRY', 'Italy'), ('CURRENCY', 'Lira')],
                [('COUNTRY', 'France'), ('CURRENCY', 'FFranc')],
                [('COUNTRY', 'Germany'), ('CURRENCY', 'D-Mark')],
                [('COUNTRY', 'Australia'), ('CURRENCY', 'ADollar')],
                [('COUNTRY', 'Hong Kong'), ('CURRENCY', 'HKDollar')]
            ]
        )
        rows = cur.fetchmanymap(10)
        self.assertListEqual(
            [row.items() for row in rows],
            [
                [('COUNTRY', 'Netherlands'), ('CURRENCY', 'Guilder')],
                [('COUNTRY', 'Belgium'), ('CURRENCY', 'BFranc')],
                [('COUNTRY', 'Austria'), ('CURRENCY', 'Schilling')],
                [('COUNTRY', 'Fiji'), ('CURRENCY', 'FDollar')]
            ]
        )
        rows = cur.fetchmany(10)
        self.assertEqual(len(rows), 0)

    def test_rowcount(self):
        cur = self.con.cursor()
        self.assertEqual(cur.rowcount, -1)
        cur.execute('select * from project')
        self.assertEqual(cur.rowcount, 0)
        cur.fetchone()
        rcount = 1 if IBTEST_USE_EMBEDDED else 6
        self.assertEqual(cur.rowcount, rcount)

    def test_name(self):
        def assign_name():
            cur.name = 'testx'

        cur = self.con.cursor()
        self.assertIsNone(cur.name)
        self.assertRaises(interbase.ProgrammingError, assign_name)
        cur.execute('select * from country')
        cur.name = 'test'
        self.assertEqual(cur.name, 'test')
        self.assertRaises(interbase.ProgrammingError, assign_name)

    def test_use_after_close(self):
        cmd = 'select * from country'
        cur = self.con.cursor()
        cur.execute(cmd)
        cur.close()
        cur.execute(cmd)
        row = cur.fetchone()
        self.assertTupleEqual(row, ('USA', 'Dollar'))
