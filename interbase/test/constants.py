# coding:utf-8
#
#   PROGRAM/MODULE: idb
#   FILE:           constants.py
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

# Note: since client library is cached (see ibcore.py:29),
# it makes sense to either run all tests as embedded or server
IBTEST_USE_EMBEDDED = False
os.environ['IBTEST_USE_EMBEDDED'] = str(IBTEST_USE_EMBEDDED)

IBTEST_DB = 'test2020v4.ib'

# IBTEST_HOST = 'localhost'
# IBTEST_HOST = 'localhost/gds_ssl'
# Best practice tip: It is recommended to have 'gds_ssl' service assigned to port 3065 in your services file.
IBTEST_HOST = None

IBTEST_USER = 'SYSDBA'

IBTEST_PASSWORD = 'masterkey'
# Path to dir for test db and temp files
IBTEST_DB_DIR_PATH = os.path.join(os.getcwd(), 'files')
# Full path to test database file
IBTEST_DB_PATH = os.path.join(IBTEST_DB_DIR_PATH, IBTEST_DB)

# Define the IBTEST_SERVER_PUBLIC_FILE location to enable OTW, Set it to None to disable OTW
# Also remember to set IBTEST_HOST explicitly if OTW is enabled
# IBTEST_SERVER_PUBLIC_FILE = os.path.join(IBTEST_DB_DIR_PATH, "ibserverCAfile.pem")
# IBTEST_SERVER_PUBLIC_FILE = os.path.join(IBTEST_DB_DIR_PATH, "cert")
IBTEST_SERVER_PUBLIC_FILE = None

IBTEST_SQL_DIALECT = 3
