# coding:utf-8
#
#   PROGRAM/MODULE: interbase
#   FILE:           test_stored_proc.py
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

from core import InterbaseTestBase
from decimal import Decimal
from constants import IBTEST_USER, IBTEST_HOST, IBTEST_PASSWORD, IBTEST_DB_PATH, IBTEST_SQL_DIALECT,\
    IBTEST_SERVER_PUBLIC_FILE


class TestStoredProc(InterbaseTestBase):
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
        self.con.close()

    def test_callproc(self):
        cur = self.con.cursor()
        result = cur.callproc('sub_tot_budget', ['100'])
        self.assertListEqual(result, ['100'])
        row = cur.fetchone()
        self.assertTupleEqual(
            row,
            (
                Decimal('3800000'),
                Decimal('760000'),
                Decimal('500000'),
                Decimal('1500000')
            )
        )
        result = cur.callproc('sub_tot_budget', [100])
        self.assertListEqual(result, [100])
        row = cur.fetchone()
        self.assertTupleEqual(
            row,
            (
                Decimal('3800000'),
                Decimal('760000'),
                Decimal('500000'),
                Decimal('1500000')
            )
        )
