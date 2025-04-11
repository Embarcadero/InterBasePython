# coding:utf-8
#
#   PROGRAM/MODULE: interbase
#   FILE:           test_prepared_statement.py
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

from .core import InterBaseTestBase
from .constants import IBTEST_HOST, IBTEST_USER, IBTEST_PASSWORD, IBTEST_DB_PATH, IBTEST_SQL_DIALECT,\
    IBTEST_SERVER_PUBLIC_FILE


class TestPreparedStatement(InterBaseTestBase):
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

    def test_basic(self):
        cur = self.con.cursor()
        ps = cur.prep('select * from country')
        self.assertEqual(ps._in_sqlda.sqln, 10)
        self.assertEqual(ps._in_sqlda.sqld, 0)
        self.assertEqual(ps._out_sqlda.sqln, 10)
        self.assertEqual(ps._out_sqlda.sqld, 2)
        self.assertEqual(ps.statement_type, 1)
        self.assertEqual(ps.sql, 'select * from country')

    def test_get_plan(self):
        cur = self.con.cursor()
        ps = cur.prep('select * from job')
        self.assertEqual(ps.plan, "PLAN (JOB NATURAL)")

    def test_execution(self):
        cur = self.con.cursor()
        ps = cur.prep('select * from country')
        cur.execute(ps)
        row = cur.fetchone()
        self.assertTupleEqual(row, ('USA', 'Dollar'))

    def test_wrong_cursor(self):
        cur = self.con.cursor()
        cur2 = self.con.cursor()
        ps = cur.prep('select * from country')
        with self.assertRaises(ValueError) as cm:
            cur2.execute(ps)
        self.assertTupleEqual(
            cm.exception.args,
            ('PreparedStatement was created by different Cursor.',)
        )
