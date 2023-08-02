# coding:utf-8
#
#   PROGRAM/MODULE: interbase
#   FILE:           test_charset_conversion.py
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
from constants import IBTEST_HOST, IBTEST_USER, IBTEST_PASSWORD, IBTEST_DB_PATH, IBTEST_SQL_DIALECT,\
    IBTEST_SERVER_PUBLIC_FILE


class TestCharsetConversion(InterbaseTestBase):
    def setUp(self):
        self.con = interbase.connect(
            host=IBTEST_HOST,
            database=IBTEST_DB_PATH,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            charset='utf8',
            sql_dialect=IBTEST_SQL_DIALECT,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE
        )

    def tearDown(self):
        self.con.execute_immediate("delete from t3")
        self.con.execute_immediate("delete from t4")
        self.con.commit()
        self.con.close()

    def test_octets(self):
        bytestring = interbase.ibcore.bs([1, 2, 3, 4, 5])
        cur = self.con.cursor()
        cur.execute("insert into T4 (C1, C_OCTETS, V_OCTETS) values (?,?,?)",
                    (1, bytestring, bytestring))
        self.con.commit()
        cur.execute("select C1, C_OCTETS, V_OCTETS from T4 where C1 = 1")
        row = cur.fetchone()
        self.assertTupleEqual(
            row,
            (1, b'\x01\x02\x03\x04\x05', b'\x01\x02\x03\x04\x05')
        )

    def test_utf82win1250(self):
        str_5utf8 = 'ěščřž'
        str_30utf8 = 'ěščřžýáíéúůďťňóĚŠČŘŽÝÁÍÉÚŮĎŤŇÓ'
        str_5win1250 = 'abcde'
        str_30win1250 = '012345678901234567890123456789'

        con1250 = interbase.connect(
            host=IBTEST_HOST,
            database=IBTEST_DB_PATH,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            charset='win1250',
            sql_dialect=IBTEST_SQL_DIALECT,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE
        )
        c_utf8 = self.con.cursor()
        c_win1250 = con1250.cursor()

        # Insert unicode data
        c_utf8.execute("insert into T4 (C1, C_WIN1250, V_WIN1250, C_UTF8, V_UTF8) values (?,?,?,?,?)",
                       (1, str_5win1250, str_30win1250, str_5utf8, str_30utf8))
        self.con.commit()

        # Should return the same unicode content when read from win1250 or utf8 connection
        c_win1250.execute("select C1, C_WIN1250, V_WIN1250,"
                          "C_UTF8, V_UTF8 from T4 where C1 = 1")
        row = c_win1250.fetchone()
        self.assertTupleEqual(row, (1, str_5win1250, str_30win1250, str_5utf8, str_30utf8))
        c_utf8.execute("select C1, C_WIN1250, V_WIN1250,"
                       "C_UTF8, V_UTF8 from T4 where C1 = 1")
        row = c_utf8.fetchone()
        self.assertTupleEqual(row, (1, str_5win1250, str_30win1250, str_5utf8, str_30utf8))

    def testCharVarchar(self):
        s = 'Introdução'
        self.assertEqual(len(s), 10)
        data = tuple([1, s, s])
        cur = self.con.cursor()
        cur.execute('insert into T3 (C1,C2,C3) values (?,?,?)', data)
        self.con.commit()
        cur.execute('select C1,C2,C3 from T3 where C1 = 1')
        row = cur.fetchone()
        self.assertEqual(row, data)

    def testBlob(self):
        s = """Introdução

Este artigo descreve como você pode fazer o InterBase e o InterBase 1.5
coehabitarem pacificamente seu computador Windows. Por favor, note que esta
solução não permitirá que o InterBase e o InterBase rodem ao mesmo tempo.
Porém você poderá trocar entre ambos com um mínimo de luta. """
        self.assertEqual(len(s), 294)
        data = tuple([2, s])
        b_data = tuple([3, interbase.ibase.b('bytestring')])
        cur = self.con.cursor()
        # Text BLOB
        cur.execute('insert into T3 (C1,C4) values (?,?)', data)
        self.con.commit()
        cur.execute('select C1,C4 from T3 where C1 = 2')
        row = cur.fetchone()
        self.assertEqual(row, data)
        # Insert Unicode into non-textual BLOB
        with self.assertRaises(TypeError) as cm:
            cur.execute('insert into T3 (C1,C5) values (?,?)', data)
            self.con.commit()
        self.assertTupleEqual(
            cm.exception.args,
            ('Unicode strings are not acceptable input for a non-textual BLOB column.',)
        )
        # Read binary from non-textual BLOB
        cur.execute('insert into T3 (C1,C5) values (?,?)', b_data)
        self.con.commit()
        cur.execute('select C1,C5 from T3 where C1 = 3')
        row = cur.fetchone()
        self.assertEqual(row, b_data)
