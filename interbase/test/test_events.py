# coding:utf-8
#
#   PROGRAM/MODULE: interbase
#   FILE:           test_events.py
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
import threading

from unittest import skip
from core import InterBaseTestBase
from constants import IBTEST_DB_DIR_PATH, IBTEST_HOST, IBTEST_USER, IBTEST_PASSWORD, IBTEST_SQL_DIALECT,\
    IBTEST_SERVER_PUBLIC_FILE


class TestEvents(InterBaseTestBase):
    def setUp(self):
        self.dbfile = os.path.join(IBTEST_DB_DIR_PATH, 'ibevents.ib')
        if os.path.exists(self.dbfile):
            os.remove(self.dbfile)
        self.con = interbase.create_database(
            host=IBTEST_HOST,
            database=self.dbfile,
            user=IBTEST_USER,
            password=IBTEST_PASSWORD,
            sql_dialect=IBTEST_SQL_DIALECT,
            ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
            server_public_file=IBTEST_SERVER_PUBLIC_FILE
        )
        c = self.con.cursor()
        c.execute("CREATE TABLE T (PK Integer, C1 Integer)")
        c.execute("""CREATE TRIGGER EVENTS_AU FOR T ACTIVE
BEFORE UPDATE POSITION 0
AS
BEGIN
    if (old.C1 <> new.C1) then
        post_event 'c1_updated' ;
END""")
        c.execute("""CREATE TRIGGER EVENTS_AI FOR T ACTIVE
AFTER INSERT POSITION 0
AS
BEGIN
    if (new.c1 = 1) then
        post_event 'insert_1' ;
    else if (new.c1 = 2) then
        post_event 'insert_2' ;
    else if (new.c1 = 3) then
        post_event 'insert_3' ;
    else
        post_event 'insert_other' ;
END""")
        self.con.commit()

    def tearDown(self):
        self.con.drop_database()
        self.con.close()

    def send_events(self, command_list):
        c = self.con.cursor()
        for cmd in command_list:
            c.execute(cmd)
        self.con.commit()

    @skip("issue #53: test_events.py freezes on ibcore.py:1829 queue.get()")
    def test_one_event(self):
        timed_event = threading.Timer(3.0, self.send_events, args=[["insert into T (PK,C1) values (1,1)", ]])
        with self.con.event_conduit(['insert_1']) as events:
            timed_event.start()
            e = events.wait()
        timed_event.join()
        self.assertDictEqual(e, {'insert_1': 1})

    @skip("issue #53: test_events.py freezes on ibcore.py:1829 queue.get()")
    def test_multiple_events(self):
        cmds = [
            "insert into T (PK,C1) values (1,1)",
            "insert into T (PK,C1) values (1,2)",
            "insert into T (PK,C1) values (1,3)",
            "insert into T (PK,C1) values (1,1)",
            "insert into T (PK,C1) values (1,2)",
        ]
        timed_event = threading.Timer(3.0, self.send_events, args=[cmds])
        with self.con.event_conduit(['insert_1', 'insert_3']) as events:
            timed_event.start()
            e = events.wait()
        timed_event.join()
        self.assertDictEqual(e, {'insert_3': 1, 'insert_1': 2})

    def test_14_events(self):
        cmds = [
            "insert into T (PK,C1) values (1,1)",
            "insert into T (PK,C1) values (1,2)",
            "insert into T (PK,C1) values (1,3)",
            "insert into T (PK,C1) values (1,1)",
            "insert into T (PK,C1) values (1,2)",
        ]
        self.e = {}
        timed_event = threading.Timer(1.0, self.send_events, args=[cmds])
        with self.con.event_conduit(
                [
                    'insert_1', 'A', 'B', 'C', 'D',
                    'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
                    'insert_3'
                ]
        ) as events:
            timed_event.start()
            time.sleep(3)
            e = events.wait()
        timed_event.join()
        self.assertDictEqual(
            e,
            {
                'A': 0, 'C': 0, 'B': 0, 'E': 0, 'D': 0, 'G': 0, 'insert_1': 2,
                'I': 0, 'H': 0, 'K': 0, 'J': 0, 'L': 0, 'insert_3': 1, 'F': 0
            }
        )

    @skip("issue #53: test_events.py freezes on ibcore.py:1829 queue.get()")
    def test_flush_events(self):
        timed_event = threading.Timer(3.0, self.send_events, args=[["insert into T (PK,C1) values (1,1)"]])
        with self.con.event_conduit(['insert_1']) as events:
            self.send_events(["insert into T (PK,C1) values (1,1)", "insert into T (PK,C1) values (1,1)"])
            time.sleep(2)
            events.flush()
            timed_event.start()
            e = events.wait()
        timed_event.join()
        self.assertDictEqual(e, {'insert_1': 1})
