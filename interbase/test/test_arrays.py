# coding:utf-8
#
#   PROGRAM/MODULE: idb
#   FILE:           test_arrays.py
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
import datetime
import decimal

from core import InterbaseTestBase
from constants import IBTEST_HOST, IBTEST_USER, IBTEST_PASSWORD, IBTEST_DB_PATH, IBTEST_SQL_DIALECT,\
    IBTEST_SERVER_PUBLIC_FILE


class TestArrays(InterbaseTestBase):
    def setUp(self):
        self.con = idb.connect(
            host=IBTEST_HOST,
            database=IBTEST_DB_PATH,
            user=IBTEST_USER, password=IBTEST_PASSWORD,
            sql_dialect=IBTEST_SQL_DIALECT,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE,
        )
        #
        self.c2 = [[[1, 1], [2, 2], [3, 3], [4, 4]], [[5, 5], [6, 6], [7, 7], [8, 8]],
                   [[9, 9], [10, 10], [11, 11], [12, 12]], [[13, 13], [14, 14], [15, 15], [16, 16]]]
        self.c3 = [['a', 'a'], ['bb', 'bb'], ['ccc', 'ccc'], ['dddd', 'dddd'], ['eeeee', 'eeeee'],
                   ['fffffff78901234', 'fffffff78901234']]
        self.c4 = ['a    ', 'bb   ', 'ccc  ', 'dddd ', 'eeeee']
        self.c5 = [datetime.datetime(2012, 11, 22, 12, 8, 24, 474800),
                   datetime.datetime(2012, 11, 22, 12, 8, 24, 474800)]
        self.c6 = [datetime.time(12, 8, 24, 474800), datetime.time(12, 8, 24, 474800)]
        self.c7 = [decimal.Decimal('10.22'), decimal.Decimal('100000.33')]\
            if IBTEST_SQL_DIALECT == 3 else [float('10.22'), float('100000.33')]
        self.c8 = [decimal.Decimal('10.22'), decimal.Decimal('100000.33')]\
            if IBTEST_SQL_DIALECT == 3 else [float('10.22'), float('100000.33')]
        self.c9 = [1, 0]
        self.c10 = [5555555, 7777777]
        self.c11 = [3.140000104904175, 3.140000104904175]
        self.c12 = [3.14, 3.14]
        self.c13 = [decimal.Decimal('10.2'), decimal.Decimal('100000.3')]\
            if IBTEST_SQL_DIALECT == 3 else [float('10.2'), float('100000.3')]
        self.c14 = [decimal.Decimal('10.22222'), decimal.Decimal('100000.333')]\
            if IBTEST_SQL_DIALECT == 3 else [float('10.22222'), float('100000.333')]
        self.c15 = [decimal.Decimal('1000000000000.22222'), decimal.Decimal('1000000000000.333')]\
            if IBTEST_SQL_DIALECT == 3 else [float('1000000000000.22222'), float('1000000000000.333')]

        self.JOB_CODE = [
            'Accnt', 'Admin', 'Admin', 'Admin', 'CEO', 'CFO', 'Dir', 'Doc', 'Doc', 'Eng', 'Eng', 'Eng',
            'Eng', 'Eng', 'Eng', 'Finan', 'Mktg', 'Mktg', 'Mngr', 'Mngr', 'PRel', 'SRep', 'SRep', 'SRep',
            'SRep', 'SRep', 'SRep', 'SRep', 'Sales', 'Sales', 'VP',
        ]
        self.JOB_GRADE = [4, 4, 5, 5, 1, 1, 2, 3, 5, 2, 3, 3, 4, 4, 5, 3, 3, 4, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3, 2]
        self.JOB_COUNTRY = [
            'USA', 'USA', 'England', 'USA', 'USA', 'USA', 'USA', 'USA', 'USA', 'USA', 'Japan', 'USA',
            'England', 'USA', 'USA', 'USA', 'USA', 'USA', 'USA', 'USA', 'USA', 'Canada', 'England',
            'France', 'Italy', 'Japan', 'Switzerland', 'USA', 'England', 'USA', 'USA'
        ]
        self.JOB_TITLE = [
            'Accountant', 'Administrative Assistant', 'Administrative Assistant',
            'Administrative Assistant', 'Chief Executive Officer', 'Chief Financial Officer', 'Director',
            'Technical Writer', 'Technical Writer', 'Engineer', 'Engineer', 'Engineer', 'Engineer',
            'Engineer', 'Engineer', 'Financial Analyst', 'Marketing Analyst', 'Marketing Analyst',
            'Manager', 'Manager', 'Public Relations Rep.', 'Sales Representative', 'Sales Representative',
            'Sales Representative', 'Sales Representative', 'Sales Representative',
            'Sales Representative', 'Sales Representative', 'Sales Co - ordinator',
            'Sales Co - ordinator', 'Vice President'
        ]
        self.MIN_SALARY = [
            28000, 35000, 13400, 20000, 130000, 85000, 75000, 38000, 22000, 70000, 5400000, 50000, 20100,
            30000, 25000, 35000, 40000, 20000, 60000, 30000, 25000, 26400, 13400, 118200, 33600000.00,
            2160000, 28000, 20000, 26800, 40000, 80000
        ]
        self.MAX_SALARY = [
            55000, 55000, 26800, 40000, 250000, 140000, 120000, 60000, 40000, 110000, 9720000, 90000,
            43550, 65000, 35000, 85000, 80000, 50000, 100000, 60000, 65000, 132000, 67000, 591000,
            168000000.00, 10800000, 149000, 100000, 46900, 70000, 130000
        ]
        self.JOB_REQUIREMENT = [
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", ""
        ]
        self.LANGUAGE_REQ = [
            ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''],
            ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''],
            ['', '', '', '', ''], ['', '', '', '', ''],
            ['Japanese\n', 'Mandarin\n', 'English\n', '\n', '\n'], ['', '', '', '', ''],
            ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''],
            ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''],
            ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''],
            ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''],
            ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', '']
        ]
        self.FISCAL_YEAR = [
            1994, 1994, 1993, 1994, 1994, 1994, 1994, 1994, 1994,
            1994, 1994, 1994, 1994, 1994, 1995, 1995, 1995, 1995,
            1994, 1995, 1994, 1994, 1995, 1996
        ]
        self.PROJ_ID = [
            'GUIDE', 'GUIDE', 'MAPDB', 'MAPDB', 'MAPDB', 'MAPDB', 'HWRII', 'HWRII', 'HWRII', 'MKTPR',
            'MKTPR', 'MKTPR', 'MKTPR', 'MKTPR', 'MKTPR', 'MKTPR', 'MKTPR', 'MKTPR', 'VBASE', 'VBASE',
            'VBASE', 'VBASE', 'VBASE', 'VBASE'
        ]
        self.DEPT_NO = [
            '100', '671', '621', '621', '622', '671', '670', '621', '622', '623', '672', '100', '110',
            '000', '623', '672', '100', '110', '621', '621', '622', '100', '100', '100'
        ]
        self.QUART_HEAD_CNT = [
            [1, 1, 1, 0], [3, 2, 1, 0], [0, 0, 0, 1], [2, 1, 0, 0], [1, 1, 0, 0], [1, 1, 0, 0],
            [1, 1, 1, 1], [2, 3, 2, 1], [1, 1, 2, 2], [1, 1, 1, 2], [1, 1, 1, 2], [4, 5, 6, 6],
            [2, 2, 0, 3], [1, 1, 2, 2], [7, 7, 4, 4], [2, 3, 3, 3], [4, 5, 6, 6], [1, 1, 1, 1],
            [4, 5, 5, 3], [4, 3, 2, 2], [2, 2, 2, 1], [1, 1, 2, 3], [3, 3, 1, 1], [1, 1, 0, 0]
        ]
        self.PROJECTED_BUDGET = [
            200000.00, 450000.00, 20000.00, 40000.00, 60000.00, 11000.00, 20000.00, 400000.00,
            100000.00, 80000.00, 100000.00, 1000000.00, 200000.00, 100000.00, 1200000.00,
            800000.00, 2000000.00, 1200000.00, 1900000.00, 900000.00, 400000.00, 300000.00,
            1500000.00, 150000.00
        ]

    def tearDown(self):
        self.con.execute_immediate("delete from AR where c1>=100")
        self.con.commit()
        self.con.close()

    def test_basic(self):
        cur = self.con.cursor()
        cur.execute("delete from job")
        self.con.commit()
        for index in range(len(self.JOB_CODE)):
            cur.execute(
                "insert into job (JOB_CODE, JOB_GRADE, JOB_COUNTRY, JOB_TITLE, MIN_SALARY, MAX_SALARY, JOB_REQUIREMENT, LANGUAGE_REQ) values (?,?,?,?,?,?,?,?)",
                [
                    self.JOB_CODE[index], self.JOB_GRADE[index], self.JOB_COUNTRY[index], self.JOB_TITLE[index],
                    self.MIN_SALARY[index], self.MAX_SALARY[index], self.JOB_REQUIREMENT[index],
                    self.LANGUAGE_REQ[index]
                ]
            )
            self.con.commit()

        cur.execute("select LANGUAGE_REQ from job where job_code='Eng' and job_grade=3 and job_country='Japan'")
        row = cur.fetchone()
        self.assertTupleEqual(
            row,
            (
                ['Japanese\n', 'Mandarin\n', 'English\n', '\n', '\n'],
            )
        )

        cur.execute("delete from proj_dept_budget")
        self.con.commit()
        for index in range(len(self.FISCAL_YEAR)):
            cur.execute(
                "insert into proj_dept_budget (FISCAL_YEAR,PROJ_ID,DEPT_NO,QUART_HEAD_CNT,PROJECTED_BUDGET) values (?,?,?,?,?)",
                [
                    self.FISCAL_YEAR[index], self.PROJ_ID[index], self.DEPT_NO[index], self.QUART_HEAD_CNT[index],
                    self.PROJECTED_BUDGET[index]
                ]
            )
            self.con.commit()
        cur.execute('select QUART_HEAD_CNT from proj_dept_budget')
        row = cur.fetchall()
        self.assertListEqual(
            row,
            [
                ([1, 1, 1, 0],), ([3, 2, 1, 0],), ([0, 0, 0, 1],), ([2, 1, 0, 0],),
                ([1, 1, 0, 0],), ([1, 1, 0, 0],), ([1, 1, 1, 1],), ([2, 3, 2, 1],),
                ([1, 1, 2, 2],), ([1, 1, 1, 2],), ([1, 1, 1, 2],), ([4, 5, 6, 6],),
                ([2, 2, 0, 3],), ([1, 1, 2, 2],), ([7, 7, 4, 4],), ([2, 3, 3, 3],),
                ([4, 5, 6, 6],), ([1, 1, 1, 1],), ([4, 5, 5, 3],), ([4, 3, 2, 2],),
                ([2, 2, 2, 1],), ([1, 1, 2, 3],), ([3, 3, 1, 1],), ([1, 1, 0, 0],)
            ]
        )

    def test_read_full(self):
        cur = self.con.cursor()
        cur.execute("delete from ar")
        self.con.commit()

        cur.execute("insert into ar (c1,c2) values (2,?)", [self.c2])
        self.con.commit()
        cur.execute("select c1,c2 from ar where c1=2")
        row = cur.fetchone()
        self.assertListEqual(row[1], self.c2)

        cur.execute("insert into ar (c1,c3) values (3,?)", [self.c3])
        self.con.commit()
        cur.execute("select c1,c3 from ar where c1=3")
        row = cur.fetchone()
        self.assertListEqual(row[1], self.c3)

        cur.execute("insert into ar (c1,c4) values (4,?)", [self.c4])
        self.con.commit()
        cur.execute("select c1,c4 from ar where c1=4")
        row = cur.fetchone()
        self.assertListEqual(row[1], self.c4)

        cur.execute("insert into ar (c1,c5) values (5,?)", [self.c5])
        self.con.commit()
        cur.execute("select c1,c5 from ar where c1=5")
        row = cur.fetchone()
        self.assertListEqual(row[1], self.c5)

        if IBTEST_SQL_DIALECT == 3:
            cur.execute("insert into ar (c1,c6) values (6,?)", [self.c6])
            self.con.commit()
            cur.execute("select c1,c6 from ar where c1=6")
            row = cur.fetchone()
            self.assertListEqual(row[1], self.c6)

        cur.execute("insert into ar (c1,c7) values (7,?)", [self.c7])
        self.con.commit()
        cur.execute("select c1,c7 from ar where c1=7")
        row = cur.fetchone()
        self.assertListEqual(row[1], self.c7)

        cur.execute("insert into ar (c1,c8) values (8,?)", [self.c8])
        self.con.commit()
        cur.execute("select c1,c8 from ar where c1=8")
        row = cur.fetchone()
        self.assertListEqual(row[1], self.c8)

        cur.execute("insert into ar (c1,c9) values (9,?)", [self.c9])
        self.con.commit()
        cur.execute("select c1,c9 from ar where c1=9")
        row = cur.fetchone()
        self.assertListEqual(row[1], self.c9)

        cur.execute("insert into ar (c1,c10) values (10,?)", [self.c10])
        self.con.commit()
        cur.execute("select c1,c10 from ar where c1=10")
        row = cur.fetchone()
        self.assertListEqual(row[1], self.c10)

        cur.execute("insert into ar (c1,c11) values (11,?)", [self.c11])
        self.con.commit()
        cur.execute("select c1,c11 from ar where c1=11")
        row = cur.fetchone()
        self.assertListEqual(row[1], self.c11)

        cur.execute("insert into ar (c1,c12) values (12,?)", [self.c12])
        self.con.commit()
        cur.execute("select c1,c12 from ar where c1=12")
        row = cur.fetchone()
        self.assertListEqual(row[1], self.c12)

        cur.execute("insert into ar (c1,c13) values (13,?)", [self.c13])
        self.con.commit()
        cur.execute("select c1,c13 from ar where c1=13")
        row = cur.fetchone()
        self.assertListEqual(row[1], self.c13)

        cur.execute("insert into ar (c1,c14) values (14,?)", [self.c14])
        self.con.commit()
        cur.execute("select c1,c14 from ar where c1=14")
        row = cur.fetchone()
        self.assertListEqual(row[1], self.c14)

        cur.execute("insert into ar (c1,c15) values (15,?)", [self.c15])
        self.con.commit()
        cur.execute("select c1,c15 from ar where c1=15")
        row = cur.fetchone()
        self.assertListEqual(row[1], self.c15)

    def test_write_full(self):
        cur = self.con.cursor()
        # INTEGER
        cur.execute("insert into ar (c1,c2) values (102,?)", [self.c2])
        self.con.commit()
        cur.execute("select c1,c2 from ar where c1=102")
        row = cur.fetchone()
        self.assertListEqual(row[1], self.c2)

        # VARCHAR
        cur.execute("insert into ar (c1,c3) values (103,?)", [self.c3])
        self.con.commit()
        cur.execute("select c1,c3 from ar where c1=103")
        row = cur.fetchone()
        self.assertListEqual(row[1], self.c3)

        cur.execute("insert into ar (c1,c3) values (103,?)", [tuple(self.c3)])
        self.con.commit()
        cur.execute("select c1,c3 from ar where c1=103")
        row = cur.fetchone()
        self.assertListEqual(row[1], self.c3)

        # CHAR
        cur.execute("insert into ar (c1,c4) values (104,?)", [self.c4])
        self.con.commit()
        cur.execute("select c1,c4 from ar where c1=104")
        row = cur.fetchone()
        self.assertListEqual(row[1], self.c4)

        # TIMESTAMP
        cur.execute("insert into ar (c1,c5) values (105,?)", [self.c5])
        self.con.commit()
        cur.execute("select c1,c5 from ar where c1=105")
        row = cur.fetchone()
        self.assertListEqual(row[1], self.c5)

        if IBTEST_SQL_DIALECT == 3:
            # TIME OK
            cur.execute("insert into ar (c1,c6) values (106,?)", [self.c6])
            self.con.commit()
            cur.execute("select c1,c6 from ar where c1=106")
            row = cur.fetchone()
            self.assertListEqual(row[1], self.c6)

        # DECIMAL(10,2)
        cur.execute("insert into ar (c1,c7) values (107,?)", [self.c7])
        self.con.commit()
        cur.execute("select c1,c7 from ar where c1=107")
        row = cur.fetchone()
        self.assertListEqual(row[1], self.c7)

        # NUMERIC(10,2)
        cur.execute("insert into ar (c1,c8) values (108,?)", [self.c8])
        self.con.commit()
        cur.execute("select c1,c8 from ar where c1=108")
        row = cur.fetchone()
        self.assertListEqual(row[1], self.c8)

        # SMALLINT
        cur.execute("insert into ar (c1,c9) values (109,?)", [self.c9])
        self.con.commit()
        cur.execute("select c1,c9 from ar where c1=109")
        row = cur.fetchone()
        self.assertListEqual(row[1], self.c9)

        # BIGINT
        cur.execute("insert into ar (c1,c10) values (110,?)", [self.c10])
        self.con.commit()
        cur.execute("select c1,c10 from ar where c1=110")
        row = cur.fetchone()
        self.assertListEqual(row[1], self.c10)

        # FLOAT
        cur.execute("insert into ar (c1,c11) values (111,?)", [self.c11])
        self.con.commit()
        cur.execute("select c1,c11 from ar where c1=111")
        row = cur.fetchone()
        self.assertListEqual(row[1], self.c11)

        # DOUBLE PRECISION
        cur.execute("insert into ar (c1,c12) values (112,?)", [self.c12])
        self.con.commit()
        cur.execute("select c1,c12 from ar where c1=112")
        row = cur.fetchone()
        self.assertListEqual(row[1], self.c12)

        # DECIMAL(10,1) OK
        cur.execute("insert into ar (c1,c13) values (113,?)", [self.c13])
        self.con.commit()
        cur.execute("select c1,c13 from ar where c1=113")
        row = cur.fetchone()
        self.assertListEqual(row[1], self.c13)

        # DECIMAL(10,5)
        cur.execute("insert into ar (c1,c14) values (114,?)", [self.c14])
        self.con.commit()
        cur.execute("select c1,c14 from ar where c1=114")
        row = cur.fetchone()
        self.assertListEqual(row[1], self.c14)

        # DECIMAL(18,5)
        cur.execute("insert into ar (c1,c15) values (115,?)", [self.c15])
        self.con.commit()
        cur.execute("select c1,c15 from ar where c1=115")
        row = cur.fetchone()
        self.assertListEqual(row[1], self.c15)

    def test_write_wrong(self):
        cur = self.con.cursor()

        with self.assertRaises(ValueError) as cm:
            cur.execute("insert into ar (c1,c2) values (102,?)", [self.c3])
        self.assertTupleEqual(cm.exception.args, ('Incorrect ARRAY field value.',))
        with self.assertRaises(ValueError) as cm:
            cur.execute("insert into ar (c1,c2) values (102,?)", [self.c2[:-1]])
        self.assertTupleEqual(cm.exception.args, ('Incorrect ARRAY field value.',))
