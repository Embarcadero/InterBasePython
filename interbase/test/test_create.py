# coding:utf-8
#
#   PROGRAM/MODULE: interbase
#   FILE:           test_bugs.py
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

from core import InterBaseTestBase
from contextlib import closing
from constants import IBTEST_HOST, IBTEST_USER, IBTEST_PASSWORD, IBTEST_DB_DIR_PATH,\
    IBTEST_SQL_DIALECT, IBTEST_SERVER_PUBLIC_FILE


class TestCreateDrop(InterBaseTestBase):
    def setUp(self):
        self.db_file = os.path.join(IBTEST_DB_DIR_PATH, 'droptest.ib')
        if os.path.exists(self.db_file):
            os.remove(self.db_file)

    def test_create_drop(self):
        with closing(interbase.create_database(
                host=IBTEST_HOST,
                database=self.db_file,
                user=IBTEST_USER, password=IBTEST_PASSWORD,
                sql_dialect=IBTEST_SQL_DIALECT,
                ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
                server_public_file=IBTEST_SERVER_PUBLIC_FILE)
        ) as con:
            con.drop_database()
