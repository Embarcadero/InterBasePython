# coding:utf-8
#
#   PROGRAM/MODULE: idb
#   FILE:           core.py
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

import sys
import idb
import unittest

from io import StringIO


class IDBTestBase(unittest.TestCase):
    def __init__(self, method_name='runTest'):
        super(IDBTestBase, self).__init__(method_name)
        self.output = StringIO()

    def clear_output(self):
        self.output.close()
        self.output = StringIO()

    def show_output(self):
        sys.stdout.write(self.output.getvalue())
        sys.stdout.flush()

    def printout(self, text='', newline=True):
        self.output.write(text)
        if newline:
            self.output.write('\n')
        self.output.flush()

    def printData(self, cur):
        """Print data from open cursor to stdout."""
        # Print a header.
        for field_desc in cur.description:
            self.printout(
                field_desc[idb.DESCRIPTION_NAME].ljust(field_desc[idb.DESCRIPTION_DISPLAY_SIZE]),
                newline=False
            )
        self.printout()
        for field_desc in cur.description:
            self.printout(
                "-" * max((len(field_desc[idb.DESCRIPTION_NAME]),
                field_desc[idb.DESCRIPTION_DISPLAY_SIZE])),
                newline=False
            )
        self.printout()
        # For each row, print the value of each field left-justified within
        # the maximum possible width of that field.
        field_indices = range(len(cur.description))
        for row in cur:
            for fieldIndex in field_indices:
                field_value = str(row[fieldIndex])
                field_max_width = max(
                    (
                        len(cur.description[fieldIndex][idb.DESCRIPTION_NAME]),
                        cur.description[fieldIndex][idb.DESCRIPTION_DISPLAY_SIZE]
                     )
                )
                self.printout(field_value.ljust(field_max_width), newline=False)
            self.printout()


class SchemaVisitor(idb.schema.SchemaVisitor):
    def __init__(self, test, action, follow='dependencies'):
        self.test = test
        self.seen = []
        self.action = action
        self.follow = follow

    def default_action(self, obj):
        if not obj.issystemobject() and self.action in obj.actions:
            if self.follow == 'dependencies':
                for dependency in obj.get_dependencies():
                    d = dependency.depended_on
                    if d and d not in self.seen:
                        d.accept_visitor(self)
            elif self.follow == 'dependents':
                for dependency in obj.get_dependents():
                    d = dependency.dependent
                    if d and d not in self.seen:
                        d.accept_visitor(self)
            if obj not in self.seen:
                self.test.printout(obj.get_sql_for(self.action))
                self.seen.append(obj)

    def visitSchema(self, schema):
        pass

    def visitMetadataItem(self, item):
        pass

    def visitTableColumn(self, column):
        column.table.accept_visitor(self)

    def visitViewColumn(self, column):
        column.view.accept_visitor(self)

    def visitDependency(self, dependency):
        pass

    def visitConstraint(self, constraint):
        pass

    def visitProcedureParameter(self, param):
        param.procedure.accept_visitor(self)

    def visitFunctionArgument(self, arg):
        arg.function.accept_visitor(self)

    def visitDatabaseFile(self, dbfile):
        pass

    def visitShadow(self, shadow):
        pass
