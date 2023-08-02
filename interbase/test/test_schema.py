# coding:utf-8
#
#   PROGRAM/MODULE: idb
#   FILE:           test_schema.py
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

from unittest import skip
from idb import schema as sm
from contextlib import closing
from core import InterbaseTestBase, SchemaVisitor
from constants import IBTEST_HOST, IBTEST_USER, IBTEST_PASSWORD, IBTEST_DB_PATH, IBTEST_SQL_DIALECT,\
    IBTEST_SERVER_PUBLIC_FILE


class TestSchema(InterbaseTestBase):
    def setUp(self):
        self.con = idb.connect(
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

    def testSchemaBindClose(self):
        s = idb.schema.Schema()
        self.assertTrue(s.closed)
        s.bind(self.con)
        # properties
        self.assertIsNone(s.description)
        self.assertEqual(s.owner_name, 'SYSDBA')
        # CreateDb.sql script generate db with default character set utf-8
        self.assertEqual(s.default_character_set.name, 'UTF8')
        self.assertIsNone(s.security_class)
        self.assertFalse(s.closed)
        #
        s.close()
        self.assertTrue(s.closed)
        s.bind(self.con)
        self.assertFalse(s.closed)
        #
        s.bind(self.con)
        self.assertFalse(s.closed)
        #
        del s

    def testSchemaFromConnection(self):
        s = self.con.schema
        # enum_* disctionaries
        self.assertDictEqual(s.enum_param_type_from,
                             {0: 'DATATYPE', 1: 'DOMAIN', 2: 'TYPE OF DOMAIN', 3: 'TYPE OF COLUMN'})
        self.assertDictEqual(s.enum_object_types,
            {0: 'RELATION', 1: 'VIEW', 2: 'TRIGGER', 3: 'COMPUTED_FIELD',
             4: 'VALIDATION', 5: 'PROCEDURE', 6: 'EXPRESSION_INDEX',
             7: 'EXCEPTION', 8: 'USER', 9: 'FIELD', 10: 'INDEX',
             11: 'GENERATOR', 12: 'USER_GROUP', 13: 'ROLE',
             14: 'UDF', 15: 'ENCRYPTION', 16: 'SUBSCRIPTION'})
        self.assertDictEqual(s.enum_object_type_codes,
            {'RELATION': 0, 'VIEW': 1, 'TRIGGER': 2, 'COMPUTED_FIELD': 3,
             'VALIDATION': 4, 'PROCEDURE': 5, 'EXPRESSION_INDEX': 6,
             'EXCEPTION': 7, 'USER': 8, 'FIELD': 9, 'INDEX': 10,
             'GENERATOR': 11, 'USER_GROUP': 12, 'ROLE': 13, 'UDF': 14,
             'ENCRYPTION': 15, 'SUBSCRIPTION': 16})
        self.assertDictEqual(s.enum_character_set_names,
            {0: 'NONE', 1: 'BINARY', 2: 'ASCII7', 8: 'UCS2BE',
             64: 'UCS2LE', 3: 'SQL_TEXT', 59: 'UTF_8', 126: 'BASE64',
             5: 'SJIS', 6: 'EUCJ', 10: 'DOS_437', 11: 'DOS_850', 12: 'DOS_865',
             21: 'ANSI', 22: 'ISO-8859-2', 39: 'ISO-8859-15', 58: 'KOI8R', 45: 'DOS_852',
             46: 'DOS_857', 13: 'DOS_860', 47: 'DOS_861', 14: 'DOS_863',
             50: 'CYRL', 51: 'WIN_1250', 52: 'WIN_1251', 53: 'WIN_1252', 54: 'WIN_1253',
             55: 'WIN_1254', 19: 'NEXT', 44: 'WIN_949', 56: 'WIN_950', 57: 'WIN_936'})
        self.assertDictEqual(s.enum_field_types,
                {14: 'TEXT', 7: 'SHORT', 8: 'LONG', 9: 'QUAD',
                 10: 'FLOAT', 27: 'DOUBLE', 35: 'TIMESTAMP',
                 37: 'VARYING', 261: 'BLOB', 40: 'CSTRING',
                 45: 'BLOB_ID', 12: 'DATE', 13: 'TIME', 17: 'BOOLEAN'})
        self.assertDictEqual(s.enum_field_subtypes,
            {1: 'TEXT', 2: 'BLR', 3: 'ACL',
             4: 'RANGES', 5: 'SUMMARY', 6: 'FORMAT',
             7: 'TRANSACTION_DESCRIPTIO', 8: 'EXTERNAL_FILE_DESCRIPT'})
        self.assertDictEqual(s.enum_function_types, {0: 'VALUE', 1: 'BOOLEAN'})
        self.assertDictEqual(s.enum_mechanism_types,
                             {0: 'BY_VALUE', 1: 'BY_REFERENCE', 2: 'BY_VMS_DESCRIPTOR',
                              3: 'BY_ISC_DESCRIPTOR', 4: 'BY_SCALAR_ARRAY_DESCRI'})
        self.assertDictEqual(s.enum_procedure_types,
                             {0: 'LEGACY', 1: 'SELECTABLE', 2: 'EXECUTABLE'})
        self.assertDictEqual(s.enum_transaction_state_types,
                             {1: 'LIMBO', 2: 'COMMITTED', 3: 'ROLLED_BACK'})
        self.assertDictEqual(s.enum_trigger_types,
            {1: 'PRE_STORE', 2: 'POST_STORE', 3: 'PRE_MODIFY',
             4: 'POST_MODIFY', 5: 'PRE_ERASE', 6: 'POST_ERASE'})
        # properties
        self.assertIsNone(s.description)
        self.assertEqual(s.owner_name,'SYSDBA')
        self.assertEqual(s.default_character_set.name,'UTF8')
        self.assertIsNone(s.security_class)
        # Lists of db objects
        self.assertIsInstance(s.collations, list)
        self.assertIsInstance(s.character_sets, list)
        self.assertIsInstance(s.exceptions, list)
        self.assertIsInstance(s.generators, list)
        self.assertIsInstance(s.sysgenerators, list)
        self.assertIsInstance(s.sequences, list)
        self.assertIsInstance(s.syssequences, list)
        self.assertIsInstance(s.domains, list)
        self.assertIsInstance(s.sysdomains, list)
        self.assertIsInstance(s.indices, list)
        self.assertIsInstance(s.sysindices, list)
        self.assertIsInstance(s.tables, list)
        self.assertIsInstance(s.systables, list)
        self.assertIsInstance(s.views, list)
        self.assertIsInstance(s.sysviews, list)
        self.assertIsInstance(s.triggers, list)
        self.assertIsInstance(s.systriggers, list)
        self.assertIsInstance(s.procedures, list)
        self.assertIsInstance(s.sysprocedures, list)
        self.assertIsInstance(s.constraints, list)
        self.assertIsInstance(s.roles, list)
        self.assertIsInstance(s.dependencies, list)
        self.assertIsInstance(s.functions, list)
        self.assertIsInstance(s.files, list)
        s.reload()
        self.assertEqual(len(s.character_sets),32)
        self.assertEqual(len(s.exceptions),5)
        self.assertEqual(len(s.generators),2)
        self.assertEqual(len(s.sysgenerators),10)
        self.assertEqual(len(s.domains),15)
        self.assertEqual(len(s.sysdomains), 256)
        self.assertEqual(len(s.indices),28)
        self.assertEqual(len(s.sysindices),77)
        self.assertEqual(len(s.tables),15)
        self.assertEqual(len(s.systables), 49)
        self.assertEqual(len(s.views),1)
        self.assertEqual(len(s.sysviews),0)
        self.assertEqual(len(s.triggers),5)
        self.assertEqual(len(s.systriggers),41)
        self.assertEqual(len(s.procedures),11)
        self.assertEqual(len(s.sysprocedures),0)
        self.assertEqual(len(s.constraints),56)
        self.assertEqual(len(s.dependencies),95)
        self.assertEqual(len(s.functions),0)
        self.assertEqual(len(s.sysfunctions),0)
        self.assertEqual(len(s.files),1)
        #
        self.assertIsInstance(s.collations[0],sm.Collation)
        self.assertIsInstance(s.character_sets[0],sm.CharacterSet)
        self.assertIsInstance(s.exceptions[0],sm.DatabaseException)
        self.assertIsInstance(s.sysgenerators[0],sm.Sequence)
        self.assertIsInstance(s.syssequences[0],sm.Sequence)
        self.assertIsInstance(s.sysdomains[0],sm.Domain)
        self.assertIsInstance(s.indices[0],sm.Index)
        self.assertIsInstance(s.sysindices[0],sm.Index)
        self.assertIsInstance(s.tables[0],sm.Table)
        self.assertIsInstance(s.systables[0],sm.Table)
        #self.assertIsInstance(s.sysviews[0],sm.View)
        self.assertIsInstance(s.systriggers[0],sm.Trigger)
        #self.assertIsInstance(s.sysprocedures[0],sm.Procedure)
        self.assertIsInstance(s.constraints[0],sm.Constraint)
        #self.assertIsInstance(s.roles[0],sm.Role)
        self.assertIsInstance(s.dependencies[0],sm.Dependency)
        #self.assertIsInstance(s.files[0],sm.DatabaseFile)
        #
        self.assertEqual(s.get_collation('OCTETS').name,'OCTETS')
        self.assertEqual(s.get_character_set('WIN1250').name,'WIN1250')
        self.assertEqual(s.get_exception('UNKNOWN_EMP_ID').name,'UNKNOWN_EMP_ID')
        self.assertEqual(s.get_index('MINSALX').name,'MINSALX')
        self.assertEqual(s.get_table('COUNTRY').name,'COUNTRY')
        self.assertEqual(s.get_constraint('INTEG_1').name,'INTEG_1')
        #self.assertEqual(s.get_role('X').name,'X')
        self.assertEqual(s.get_collation_by_id(0,0).name,'NONE')
        self.assertEqual(s.get_character_set_by_id(0).name,'NONE')
        #
        self.assertFalse(s.closed)
        #
        with self.assertRaises(idb.ProgrammingError) as cm:
            s.close()
        self.assertTupleEqual(cm.exception.args,
                              ("Call to 'close' not allowed for embedded Schema.",))
        with self.assertRaises(idb.ProgrammingError) as cm:
            s.bind(self.con)
        self.assertTupleEqual(cm.exception.args,
                              ("Call to 'bind' not allowed for embedded Schema.",))

    def testCollation(self):
        # System collation
        c = self.con.schema.get_collation('ES_ES')
        # common properties
        self.assertEqual(c.name, 'ES_ES')
        self.assertIsNone(c.description)
        self.assertListEqual(c.actions, [])
        self.assertTrue(c.issystemobject())
        self.assertEqual(c.get_quoted_name(), 'ES_ES')
        self.assertListEqual(c.get_dependents(), [])
        self.assertListEqual(c.get_dependencies(), [])
        #
        self.assertEqual(c.id,10)
        self.assertEqual(c.character_set.name,'ISO8859_1')
        self.assertIsNone(c.function_name)


    def testCharacterSet(self):
        c = self.con.schema.get_character_set('UTF8')
        # common properties
        self.assertEqual(c.name, 'UTF8')
        self.assertIsNone(c.description)
        self.assertListEqual(c.actions, ['alter'])
        self.assertTrue(c.issystemobject())
        self.assertEqual(c.get_quoted_name(), 'UTF8')
        self.assertListEqual(c.get_dependents(), [])
        self.assertListEqual(c.get_dependencies(), [])
        #
        self.assertEqual(c.id,59)
        self.assertEqual(c.bytes_per_character,4)
        self.assertEqual(c.default_collate.name,'UTF8')
        self.assertListEqual([x.name for x in c.collations], ['UTF8'])
        #
        self.assertEqual(c.get_sql_for('alter', collation='UCS_BASIC'),
                         "ALTER CHARACTER SET UTF8 SET DEFAULT COLLATION UCS_BASIC")
        with self.assertRaises(idb.ProgrammingError) as cm:
            c.get_sql_for('alter', badparam='UCS_BASIC')
        self.assertTupleEqual(cm.exception.args,
                              ("Unsupported parameter(s) 'badparam'",))
        with self.assertRaises(idb.ProgrammingError) as cm:
            c.get_sql_for('alter')
        self.assertTupleEqual(cm.exception.args, ("Missing required parameter: 'collation'.",))
        #
        self.assertEqual(c.get_collation('UTF8').name, 'UTF8')
        self.assertEqual(c.get_collation_by_id(c.get_collation('UTF8').id).name, 'UTF8')

    def testException(self):
        c = self.con.schema.get_exception('UNKNOWN_EMP_ID')
        # common properties
        self.assertEqual(c.name, 'UNKNOWN_EMP_ID')
        self.assertIsNone(c.description)
        self.assertListEqual(c.actions,
                             ['create', 'recreate', 'alter', 'create_or_alter', 'drop'])
        self.assertFalse(c.issystemobject())
        self.assertEqual(c.get_quoted_name(), 'UNKNOWN_EMP_ID')
        d = c.get_dependents()
        self.assertEqual(len(d), 1)
        d = d[0]
        self.assertEqual(d.dependent_name, 'ADD_EMP_PROJ')
        self.assertEqual(d.dependent_type, 5)
        self.assertIsInstance(d.dependent, sm.Procedure)
        self.assertEqual(d.depended_on_name, 'UNKNOWN_EMP_ID')
        self.assertEqual(d.depended_on_type, 7)
        self.assertIsInstance(d.depended_on, sm.DatabaseException)
        self.assertListEqual(c.get_dependencies(), [])
        #
        self.assertEqual(c.id,5)
        self.assertEqual(c.message,"Invalid employee number or project id.")
        #
        self.assertEqual(c.get_sql_for('create'),
                         "CREATE EXCEPTION UNKNOWN_EMP_ID 'Invalid employee number or project id.'")
        self.assertEqual(c.get_sql_for('drop'),
                         "DROP EXCEPTION UNKNOWN_EMP_ID")
        self.assertEqual(c.get_sql_for('alter', message="New message."),
                         "ALTER EXCEPTION UNKNOWN_EMP_ID 'New message.'")
        with self.assertRaises(idb.ProgrammingError) as cm:
            c.get_sql_for('alter', badparam="New message.")
        self.assertTupleEqual(cm.exception.args,
                              ("Unsupported parameter(s) 'badparam'",))
        with self.assertRaises(idb.ProgrammingError) as cm:
            c.get_sql_for('alter')
        self.assertTupleEqual(cm.exception.args,
                              ("Missing required parameter: 'message'.",))
        self.assertEqual(c.get_sql_for('create_or_alter'),
                         "CREATE OR ALTER EXCEPTION UNKNOWN_EMP_ID 'Invalid employee number or project id.'")

    def testTableColumn(self):
        # System column
        column = self.con.schema.get_table('RDB$PAGES').get_column('RDB$PAGE_NUMBER')
        # common properties
        self.assertEqual(column.name, 'RDB$PAGE_NUMBER')
        self.assertIsNone(column.description)
        self.assertListEqual(column.actions, [])
        self.assertTrue(column.issystemobject())
        self.assertEqual(column.get_quoted_name(), 'RDB$PAGE_NUMBER')
        self.assertListEqual(column.get_dependents(), [])
        self.assertListEqual(column.get_dependencies(), [])
        # User column
        column = self.con.schema.get_table('DEPARTMENT').get_column('PHONE_NO')
        # common properties
        self.assertEqual(column.name, 'PHONE_NO')
        self.assertIsNone(column.description)
        self.assertListEqual(column.actions, ['alter', 'drop'])
        self.assertFalse(column.issystemobject())
        self.assertEqual(column.get_quoted_name(), 'PHONE_NO')
        dependency_list = column.get_dependents()
        self.assertEqual(0, len(dependency_list))
        self.assertListEqual(column.get_dependencies(), [])
        #
        self.assertEqual(column.table.name, 'DEPARTMENT')
        self.assertEqual(column.position, 6)
        self.assertIsNone(column.security_class)
        self.assertEqual(column.default, " DEFAULT '555-1234'")
        self.assertEqual(column.datatype, 'VARCHAR(20)')
        #
        self.assertTrue(column.isnullable())
        self.assertFalse(column.iscomputed())
        self.assertTrue(column.has_default())
        self.assertIsNone(column.get_computedby())
        #
        self.assertEqual(column.get_sql_for('drop'),
                         "ALTER TABLE DEPARTMENT DROP PHONE_NO")
        self.assertEqual(column.get_sql_for('alter', name='NewName'),
            'ALTER TABLE DEPARTMENT ALTER COLUMN PHONE_NO TO "NewName"')
        self.assertEqual(column.get_sql_for('alter', position=2),
            "ALTER TABLE DEPARTMENT ALTER COLUMN PHONE_NO POSITION 2")
        self.assertEqual(column.get_sql_for('alter', datatype='VARCHAR(25)'),
            "ALTER TABLE DEPARTMENT ALTER COLUMN PHONE_NO TYPE VARCHAR(25)")
        with self.assertRaises(idb.ProgrammingError) as cm:
            column.get_sql_for('alter', badparam=10)
        self.assertTupleEqual(cm.exception.args, ("Unsupported parameter(s) 'badparam'",))
        with self.assertRaises(idb.ProgrammingError) as cm:
            column.get_sql_for('alter')
        self.assertTupleEqual(cm.exception.args, ("Parameter required.",))
        with self.assertRaises(idb.ProgrammingError) as cm:
            column.get_sql_for('alter', expression='(1+1)')
        self.assertTupleEqual(cm.exception.args,
                              ("Change from persistent column to computed is not allowed.",))
        # Computed column
        column = self.con.schema.get_table('EMPLOYEE').get_column('FULL_NAME')
        self.assertTrue(column.isnullable())
        self.assertTrue(column.iscomputed())
        self.assertFalse(column.isdomainbased())
        self.assertFalse(column.has_default())
        self.assertEqual(column.get_computedby(), "(LAST_NAME || ', ' || FIRST_NAME)")
        self.assertEqual(column.datatype, 'VARCHAR(0)')
        #
        self.assertEqual(
            column.get_sql_for('alter', datatype='VARCHAR(50)', expression="(first_name || ', ' || last_name)"),
            "ALTER TABLE EMPLOYEE ALTER COLUMN FULL_NAME TYPE VARCHAR(50) COMPUTED BY (first_name || ', ' || last_name)"
        )

        with self.assertRaises(idb.ProgrammingError) as cm:
            column.get_sql_for('alter', datatype='VARCHAR(50)')
        self.assertTupleEqual(cm.exception.args, ("Change from computed column to persistent is not allowed.",))
        # Array column
        # something goes wrong when trying get INTEGER[1:4, 0:3, 1:2] column datatype
        # column = self.con.schema.get_table('AR').get_column('C2')
        # self.assertEqual(column.datatype, 'INTEGER[1:4, 0:3, 1:2]')

    def testIndex(self):
        # System index
        c = self.con.schema.get_index('RDB$INDEX_0')
        # common properties
        self.assertEqual(c.name, 'RDB$INDEX_0')
        self.assertIsNone(c.description)
        self.assertListEqual(c.actions, ['recompute'])
        self.assertTrue(c.issystemobject())
        self.assertEqual(c.get_quoted_name(), 'RDB$INDEX_0')
        self.assertListEqual(c.get_dependents(), [])
        self.assertListEqual(c.get_dependencies(), [])
        #
        self.assertEqual(c.table.name, 'RDB$RELATIONS')
        self.assertListEqual(c.segment_names, ['RDB$RELATION_NAME'])
        # user index
        c = self.con.schema.get_index('MAXSALX')
        # common properties
        self.assertEqual(c.name, 'MAXSALX')
        self.assertIsNone(c.description)
        self.assertListEqual(c.actions,
                             ['create', 'activate', 'deactivate', 'recompute', 'drop'])
        self.assertFalse(c.issystemobject())
        self.assertEqual(c.get_quoted_name(), 'MAXSALX')
        self.assertListEqual(c.get_dependents(), [])
        self.assertListEqual(c.get_dependencies(), [])
        #
        self.assertEqual(c.id,2)
        self.assertEqual(c.table.name,'JOB')
        self.assertEqual(c.index_type,'ASCENDING')
        self.assertIsNone(c.partner_index)
        self.assertIsNone(c.expression)
        # startswith() is necessary, because Python 3 returns more precise value.
        self.assertTrue(str(c.statistics).startswith('0.0384615398943'))
        self.assertListEqual(c.segment_names, ['JOB_COUNTRY', 'MAX_SALARY'])
        self.assertEqual(len(c.segments), 2)
        for segment in c.segments:
            self.assertIsInstance(segment, sm.TableColumn)
        self.assertEqual(c.segments[0].name, 'JOB_COUNTRY')
        self.assertEqual(c.segments[1].name, 'MAX_SALARY')

        self.assertListEqual(
            c.segment_statistics,
            [0.1428571492433548, 0.03846153989434242]
        )
        self.assertIsNone(c.constraint)
        #
        self.assertFalse(c.isexpression())
        self.assertFalse(c.isunique())
        self.assertFalse(c.isinactive())
        self.assertFalse(c.isenforcer())
        #
        self.assertEqual(
            c.get_sql_for('create'),
            """CREATE ASCENDING INDEX MAXSALX\n   ON JOB (JOB_COUNTRY,MAX_SALARY)"""
        )
        self.assertEqual(c.get_sql_for('activate'), "ALTER INDEX MAXSALX ACTIVE")
        self.assertEqual(c.get_sql_for('deactivate'), "ALTER INDEX MAXSALX INACTIVE")
        self.assertEqual(c.get_sql_for('recompute'), "SET STATISTICS INDEX MAXSALX")
        self.assertEqual(c.get_sql_for('drop'), "DROP INDEX MAXSALX")

    def testViewColumn(self):
        c = self.con.schema.get_view('PHONE_LIST').get_column('LAST_NAME')
        # common properties
        self.assertEqual(c.name, 'LAST_NAME')
        self.assertIsNone(c.description)
        self.assertListEqual(c.actions, [])
        self.assertFalse(c.issystemobject())
        self.assertEqual(c.get_quoted_name(),'LAST_NAME')
        self.assertListEqual(c.get_dependents(),[])
        # d = c.get_dependencies()
        # self.assertEqual(len(d), 1)
        # d = d[0]
        # self.assertEqual(d.dependent_name, 'PHONE_LIST')
        # self.assertEqual(d.dependent_type, 1)
        # self.assertIsInstance(d.dependent, sm.View)
        # self.assertEqual(d.field_name, 'LAST_NAME')
        # self.assertEqual(d.depended_on_name, 'EMPLOYEE')
        # self.assertEqual(d.depended_on_type, 0)
        # self.assertIsInstance(d.depended_on, sm.TableColumn)
        # self.assertEqual(d.depended_on.name, 'LAST_NAME')
        # self.assertEqual(d.depended_on.table.name, 'EMPLOYEE')
        # #
        # self.assertEqual(c.view.name, 'PHONE_LIST')
        # self.assertEqual(c.base_field.name, 'LAST_NAME')
        # self.assertEqual(c.base_field.table.name, 'EMPLOYEE')
        # self.assertEqual(c.domain.name, 'LASTNAME')
        # self.assertEqual(c.position, 2)
        #
        self.assertEqual(c.view.name,'PHONE_LIST')
        self.assertEqual(c.base_field.name,'LAST_NAME')
        self.assertEqual(c.base_field.table.name,'EMPLOYEE')
        self.assertEqual(c.domain.name,'LASTNAME')
        self.assertEqual(c.position,2)
        self.assertIsNone(c.security_class)
        self.assertEqual(c.datatype,'VARCHAR(20)')
        #
        self.assertTrue(c.isnullable())

    def testDomain(self):
        # System domain
        c = self.con.schema.get_domain('RDB$6')
        # common properties
        self.assertEqual(c.name, 'RDB$6')
        self.assertIsNone(c.description)
        self.assertListEqual(c.actions, [])
        self.assertTrue(c.issystemobject())
        self.assertEqual(c.get_quoted_name(), 'RDB$6')
        self.assertListEqual(c.get_dependents(), [])
        self.assertListEqual(c.get_dependencies(), [])
        # User domain
        c = self.con.schema.get_domain('PRODTYPE')
        # common properties
        self.assertEqual(c.name, 'PRODTYPE')
        self.assertIsNone(c.description)
        self.assertListEqual(c.actions, ['create', 'alter', 'drop'])
        self.assertFalse(c.issystemobject())
        self.assertEqual(c.get_quoted_name(), 'PRODTYPE')
        self.assertListEqual(c.get_dependents(), [])
        self.assertListEqual(c.get_dependencies(), [])
        #
        self.assertIsNone(c.expression)
        self.assertEqual(
            c.validation,
            "CHECK (VALUE IN ('software', 'hardware', 'other', 'N/A'))"
        )
        self.assertEqual(c.default, "'software'")
        self.assertEqual(c.length, 48)
        self.assertEqual(c.scale, 0)
        # return subtype none
        # self.assertEqual(c.sub_type, 0)
        self.assertEqual(c.field_type, 37)
        self.assertIsNone(c.sub_type)
        self.assertIsNone(c.segment_length)
        self.assertIsNone(c.external_length)
        self.assertIsNone(c.external_scale)
        self.assertIsNone(c.external_type)
        self.assertListEqual(c.dimensions, [])
        self.assertEqual(c.character_length, 12)
        self.assertEqual(c.collation.name, 'UTF8')
        self.assertEqual(c.character_set.name, 'UTF8')
        self.assertIsNone(c.precision)
        self.assertEqual(c.datatype, 'VARCHAR(12)')
        #
        self.assertFalse(c.isnullable())
        self.assertFalse(c.iscomputed())
        self.assertTrue(c.isvalidated())
        self.assertFalse(c.isarray())
        self.assertTrue(c.has_default())
        #
        self.assertEqual(
            c.get_sql_for('create'),
            "CREATE DOMAIN PRODTYPE AS VARCHAR(12) DEFAULT 'software' CHECK (VALUE IN ('software', 'hardware', 'other', 'N/A'))"
        )
        self.assertEqual(c.get_sql_for('drop'), "DROP DOMAIN PRODTYPE")
        self.assertEqual(
            c.get_sql_for('alter',name='New_name'),
            'ALTER DOMAIN PRODTYPE TO "New_name"'
        )
        self.assertEqual(
            c.get_sql_for('alter', default="'New_default'"),
            "ALTER DOMAIN PRODTYPE SET DEFAULT 'New_default'"
        )
        self.assertEqual(
            c.get_sql_for('alter', check="VALUE STARTS WITH 'X'"),
            "ALTER DOMAIN PRODTYPE ADD CHECK (VALUE STARTS WITH 'X')"
        )
        self.assertEqual(
            c.get_sql_for('alter', datatype='VARCHAR(30)'),
            "ALTER DOMAIN PRODTYPE TYPE VARCHAR(30)"
        )
        with self.assertRaises(idb.ProgrammingError) as cm:
            c.get_sql_for('alter', badparam=10)
        self.assertTupleEqual(
            cm.exception.args,
            ("Unsupported parameter(s) 'badparam'",)
        )
        with self.assertRaises(idb.ProgrammingError) as cm:
            c.get_sql_for('alter')
        self.assertTupleEqual(cm.exception.args, ("Parameter required.",))
        # Domain with quoted name
        c = self.con.schema.get_domain('FIRSTNAME')
        self.assertEqual(c.name, 'FIRSTNAME')
        self.assertEqual(c.get_quoted_name(), '"FIRSTNAME"')
        self.assertEqual(
            c.get_sql_for('create'),
            'CREATE DOMAIN "FIRSTNAME" AS VARCHAR(15)'
        )

    def testDependency(self):
        l = self.con.schema.get_table('DEPARTMENT').get_dependents()
        self.assertEqual(len(l), 16)
        c = l[0]
        # common properties
        self.assertIsNone(c.name)
        self.assertIsNone(c.description)
        self.assertListEqual(c.actions, [])
        self.assertTrue(c.issystemobject())
        self.assertIsNone(c.get_quoted_name())
        self.assertListEqual(c.get_dependents(), [])
        self.assertListEqual(c.get_dependencies(), [])
        #
        self.assertEqual(c.dependent_name, 'DELETE_EMPLOYEE')
        self.assertEqual(c.dependent_type, 5)
        self.assertIsInstance(c.dependent, sm.Procedure)
        self.assertEqual(c.dependent.name, 'DELETE_EMPLOYEE')
        self.assertEqual(c.field_name, 'MNGR_NO')
        self.assertEqual(c.depended_on_name, 'DEPARTMENT')
        self.assertEqual(c.depended_on_type, 0)
        self.assertIsInstance(c.depended_on, sm.TableColumn)
        self.assertEqual(c.depended_on.name, 'MNGR_NO')

    def testConstraint(self):
        # Common / PRIMARY KEY
        c = self.con.schema.get_table('CUSTOMER').primary_key
        # common properties
        self.assertEqual('RDB$PRIMARY22',c.name)
        self.assertIsNone(c.description)
        self.assertListEqual(c.actions, ['create', 'drop'])
        self.assertFalse(c.issystemobject())
        self.assertEqual('RDB$PRIMARY22', c.get_quoted_name())
        self.assertListEqual(c.get_dependents(),[])
        self.assertListEqual(c.get_dependencies(),[])
        #
        self.assertEqual(c.constraint_type,'PRIMARY KEY')
        self.assertEqual(c.table.name,'CUSTOMER')
        self.assertEqual('RDB$PRIMARY2', c.index.name)
        self.assertListEqual(c.trigger_names,[])
        self.assertListEqual(c.triggers,[])
        self.assertIsNone(c.column_name)
        self.assertIsNone(c.partner_constraint)
        self.assertIsNone(c.match_option)
        self.assertIsNone(c.update_rule)
        self.assertIsNone(c.delete_rule)
        #
        self.assertFalse(c.isnotnull())
        self.assertTrue(c.ispkey())
        self.assertFalse(c.isfkey())
        self.assertFalse(c.isunique())
        self.assertFalse(c.ischeck())
        self.assertFalse(c.isdeferrable())
        self.assertFalse(c.isdeferred())

        self.assertEqual("ALTER TABLE CUSTOMER ADD CONSTRAINT RDB$PRIMARY22\n  PRIMARY KEY (CUST_NO)",
                         c.get_sql_for('create'))
        self.assertEqual("ALTER TABLE CUSTOMER DROP CONSTRAINT RDB$PRIMARY22",
                         c.get_sql_for('drop'))
        # FOREIGN KEY
        c = self.con.schema.get_table('CUSTOMER').foreign_keys[0]
        #
        self.assertListEqual(c.actions, ['create', 'drop'])
        self.assertEqual(c.constraint_type, 'FOREIGN KEY')
        self.assertEqual(c.table.name, 'CUSTOMER')
        self.assertEqual(c.index.name, 'RDB$FOREIGN11')
        self.assertListEqual(c.trigger_names, [])
        self.assertListEqual(c.triggers, [])
        self.assertIsNone(c.column_name)
        self.assertEqual(c.partner_constraint.name, 'RDB$PRIMARY1')
        self.assertEqual(c.match_option, 'FULL')
        self.assertEqual(c.update_rule, 'RESTRICT')
        self.assertEqual(c.delete_rule, 'RESTRICT')
        #
        self.assertFalse(c.isnotnull())
        self.assertFalse(c.ispkey())
        self.assertTrue(c.isfkey())
        self.assertFalse(c.isunique())
        self.assertFalse(c.ischeck())
        #
        self.assertEqual(c.get_sql_for('create'),
                         """ALTER TABLE CUSTOMER ADD FOREIGN KEY (COUNTRY)
  REFERENCES COUNTRY (COUNTRY)""")
        # CHECK
        c = self.con.schema.get_constraint('INTEG_17')
        #
        self.assertListEqual(c.actions, [])
        self.assertEqual(c.constraint_type, 'NOT NULL')
        self.assertEqual(c.table.name, 'EMPLOYEE_PROJECT')
        self.assertIsNone(c.index)
        self.assertListEqual(c.trigger_names, [])
        self.assertIsNotNone(c.column_name)
        self.assertIsNone(c.partner_constraint)
        self.assertIsNone(c.match_option)
        self.assertIsNone(c.update_rule)
        self.assertIsNone(c.delete_rule)
        #
        self.assertTrue(c.isnotnull())
        self.assertFalse(c.ispkey())
        self.assertFalse(c.isfkey())
        self.assertFalse(c.isunique())
        self.assertFalse(c.ischeck())

        c = self.con.schema.get_constraint('INTEG_15')
        #
        self.assertListEqual(c.actions, [])
        self.assertEqual(c.constraint_type, 'NOT NULL')
        self.assertEqual(c.table.name, 'EMPLOYEE')
        self.assertListEqual(c.trigger_names, [])
        self.assertListEqual(c.triggers, [])
        self.assertIsNotNone(c.column_name)
        self.assertIsNone(c.partner_constraint)
        self.assertIsNone(c.match_option)
        self.assertIsNone(c.update_rule)
        self.assertIsNone(c.delete_rule)
        #
        self.assertTrue(c.isnotnull())
        self.assertFalse(c.ispkey())
        self.assertFalse(c.isfkey())
        self.assertFalse(c.isunique())
        self.assertFalse(c.ischeck())
        # NOT NULL
        c = self.con.schema.get_constraint('INTEG_13')
        #
        self.assertListEqual(c.actions, [])
        self.assertEqual(c.constraint_type, 'NOT NULL')
        self.assertEqual(c.table.name, 'EMPLOYEE')
        self.assertIsNone(c.index)
        self.assertListEqual(c.trigger_names, [])
        self.assertListEqual(c.triggers, [])
        self.assertEqual(c.column_name, 'JOB_GRADE')
        self.assertIsNone(c.partner_constraint)
        self.assertIsNone(c.match_option)
        self.assertIsNone(c.update_rule)
        self.assertIsNone(c.delete_rule)
        #
        self.assertTrue(c.isnotnull())
        self.assertFalse(c.ispkey())
        self.assertFalse(c.isfkey())
        self.assertFalse(c.isunique())
        self.assertFalse(c.ischeck())

    def testTable(self):
        # System table
        c = self.con.schema.get_table('RDB$PAGES')
        # common properties
        self.assertEqual(c.name, 'RDB$PAGES')
        self.assertIsNone(c.description)
        self.assertListEqual(c.actions, [])
        self.assertTrue(c.issystemobject())
        self.assertEqual(c.get_quoted_name(), 'RDB$PAGES')
        self.assertListEqual(c.get_dependents(), [])
        self.assertListEqual(c.get_dependencies(), [])
        # User table
        c = self.con.schema.get_table('EMPLOYEE')
        # common properties
        self.assertEqual(c.name, 'EMPLOYEE')
        self.assertIsNone(c.description)
        self.assertListEqual(c.actions, ['create', 'recreate', 'drop'])
        self.assertFalse(c.issystemobject())
        self.assertEqual(c.get_quoted_name(), 'EMPLOYEE')
        d = c.get_dependents()
        dependencies_list = [(x.dependent_name, x.dependent_type) for x in d]
        self.assertListEqual(
            dependencies_list,
            [
                ('RDB$26', 3),
                ('RDB$26', 3),
                ('SET_EMP_NO', 2),
                ('SAVE_SALARY_CHANGE', 2),
                ('SAVE_SALARY_CHANGE', 2),
                ('DELETE_EMPLOYEE', 5),
                ('DELETE_EMPLOYEE', 5),
                ('ORG_CHART', 5),
                ('ORG_CHART', 5),
                ('ORG_CHART', 5),
                ('ORG_CHART', 5),
                ('ORG_CHART', 5),
                ('PHONE_LIST', 1),
                ('PHONE_LIST', 1)
            ]
        )
        self.assertListEqual(c.get_dependencies(), [])
        #
        self.assertEqual(c.id, 132)
        self.assertEqual(c.dbkey_length,8)
        self.assertEqual(c.format, 1)
        self.assertEqual(c.table_type,'PERSISTENT')
        self.assertEqual(c.security_class, 'SQL$EMPLOYEE')
        self.assertIsNone(c.external_file)
        self.assertEqual(c.owner_name,'SYSDBA')
        self.assertEqual('SQL$DEFAULT54', c.default_class)
        self.assertEqual(c.flags,1)
        self.assertEqual('RDB$PRIMARY7', c.primary_key.name)
        # cant get foreign keys
        # self.assertListEqual([key.name for key in c.foreign_keys], ['INTEG_28', 'INTEG_29'])
        self.assertListEqual(
            [column.name for column in c.columns],
            ['EMP_NO', 'FIRST_NAME', 'LAST_NAME', 'PHONE_EXT', 'HIRE_DATE',
             'DEPT_NO', 'JOB_CODE', 'JOB_GRADE', 'JOB_COUNTRY', 'SALARY', 'FULL_NAME'])
        self.assertListEqual([constraint.name for constraint in c.constraints],
                             ['INTEG_7', 'INTEG_8', 'INTEG_9', 'INTEG_10',
                              'INTEG_11', 'INTEG_12', 'INTEG_13', 'INTEG_14',
                              'INTEG_15', 'RDB$PRIMARY7'])
        self.assertListEqual([x.name for x in c.indices], ['RDB$PRIMARY4', 'NAMEX', 'RDB$FOREIGN8', 'RDB$FOREIGN9'])
        #
        self.assertEqual(c.get_column('EMP_NO').name, 'EMP_NO')
        self.assertFalse(c.isgtt())
        self.assertTrue(c.ispersistent())
        self.assertFalse(c.isexternal())
        self.assertTrue(c.has_pkey())
        self.assertEqual(
            c.get_sql_for('create'),
            """CREATE TABLE EMPLOYEE
(
  EMP_NO EMPNO NOT NULL,
  FIRST_NAME "FIRSTNAME" NOT NULL,
  LAST_NAME "LASTNAME" NOT NULL,
  PHONE_EXT VARCHAR(4),
  HIRE_DATE TIMESTAMP DEFAULT current_timestamp NOT NULL,
  DEPT_NO DEPTNO NOT NULL,
  JOB_CODE JOBCODE NOT NULL,
  JOB_GRADE JOBGRADE NOT NULL,
  JOB_COUNTRY COUNTRYNAME NOT NULL,
  SALARY SALARY NOT NULL,
  FULL_NAME COMPUTED BY (LAST_NAME || ', ' || FIRST_NAME),
  CONSTRAINT RDB$PRIMARY7
  PRIMARY KEY (EMP_NO)
)"""
        )
        self.assertEqual(c.get_sql_for('drop'), "DROP TABLE EMPLOYEE")

    def testView(self):
        # User view
        c = self.con.schema.get_view('PHONE_LIST')
        # common properties
        self.assertEqual(c.name, 'PHONE_LIST')
        self.assertIsNone(c.description)
        self.assertListEqual(c.actions, ['create', 'recreate', 'alter',
                                         'create_or_alter', 'drop'])
        self.assertFalse(c.issystemobject())
        self.assertEqual(c.get_quoted_name(), 'PHONE_LIST')
        self.assertListEqual(c.get_dependents(), [])
        d = c.get_dependencies()
        self.assertListEqual(
            [(x.depended_on_name, x.field_name, x.depended_on_type) for x in d],
            [
                ('DEPARTMENT', 'DEPT_NO', 0),
                ('EMPLOYEE', 'DEPT_NO', 0),
                ('DEPARTMENT', None, 0),
                ('EMPLOYEE', None, 0)
            ]
        )
        #
        self.assertEqual(c.id,143)
        self.assertEqual(c.dbkey_length,16)
        self.assertEqual(c.format,1)
        self.assertEqual(c.security_class,'SQL$PHONE_LIST')
        self.assertEqual(c.owner_name,'SYSDBA')
        self.assertEqual(c.default_class,'SQL$DEFAULT65')
        self.assertEqual(c.flags,1)
        self.assertListEqual([x.name for x in c.columns],['EMP_NO', 'FIRST_NAME',
                            'LAST_NAME', 'PHONE_EXT', 'LOCATION', 'PHONE_NO'])
        self.assertListEqual(c.triggers,[])
        #
        self.assertEqual(c.get_column('LAST_NAME').name, 'LAST_NAME')
        self.assertFalse(c.has_checkoption())
        self.assertEqual(
            c.get_sql_for('create').replace('\r', ''),
            'CREATE VIEW PHONE_LIST (EMP_NO,FIRST_NAME,LAST_NAME,PHONE_EXT,LOCATION,PHONE_NO)\n   '
            'AS\n     '
            'SELECT\n  emp_no, first_name, last_name, phone_ext, location, phone_no\n  '
            'FROM employee, department\n  WHERE employee.dept_no = department.dept_no'
        )
        self.assertEqual(c.get_sql_for('drop'), "DROP VIEW PHONE_LIST")
        self.assertEqual(c.get_sql_for('alter',query='select * from country'),
            "ALTER VIEW PHONE_LIST \n   AS\n     select * from country")
        self.assertEqual(c.get_sql_for('alter',columns='country,currency',
                                       query='select * from country'),
                         "ALTER VIEW PHONE_LIST (country,currency)\n   AS\n     select * from country")
        self.assertEqual(c.get_sql_for('alter', columns='country,currency',
                                       query='select * from country', check=True),
                         "ALTER VIEW PHONE_LIST (country,currency)\n   AS\n     select * from country\n     WITH CHECK OPTION")
        self.assertEqual(c.get_sql_for('alter', columns=('country', 'currency'),
                                       query='select * from country', check=True),
                         "ALTER VIEW PHONE_LIST (country,currency)\n   AS\n     select * from country\n     WITH CHECK OPTION")
        with self.assertRaises(idb.ProgrammingError) as cm:
            c.get_sql_for('alter', badparam='select * from country')
        self.assertTupleEqual(cm.exception.args,
                              ("Unsupported parameter(s) 'badparam'",))
        with self.assertRaises(idb.ProgrammingError) as cm:
            c.get_sql_for('alter')
        self.assertTupleEqual(cm.exception.args, ("Missing required parameter: 'query'.",))
        self.assertEqual(
            c.get_sql_for('create_or_alter').replace('\r', ''),
            'CREATE OR ALTER VIEW PHONE_LIST (EMP_NO,FIRST_NAME,LAST_NAME,PHONE_EXT,LOCATION,PHONE_NO)\n'
            '   AS\n'
            '     SELECT\n'
            '  emp_no, first_name, last_name, phone_ext, location, phone_no\n'
            '  FROM employee, department\n'
            '  WHERE employee.dept_no = department.dept_no'
        )

    def test_connection_with_schema(self):
        with closing(
                idb.connect(
                    host=IBTEST_HOST, database=IBTEST_DB_PATH, user=IBTEST_USER,
                    password=IBTEST_PASSWORD,
                    connection_class=idb.ConnectionWithSchema,
                    sql_dialect=IBTEST_SQL_DIALECT,
                    ssl=IBTEST_SERVER_PUBLIC_FILE is not None,
                    server_public_file=IBTEST_SERVER_PUBLIC_FILE
                )
        ) as connection:
            self.assertEqual(len(connection.tables), 15)
            self.assertEqual(connection.get_table('JOB').name, 'JOB')

    def testTrigger(self):
        # System trigger
        sys_trigger = self.con.schema.get_trigger('RDB$TRIGGER_1')
        # common properties
        self.assertEqual(sys_trigger.name, 'RDB$TRIGGER_1')
        self.assertIsNone(sys_trigger.description)
        self.assertListEqual(sys_trigger.actions, [])
        self.assertTrue(sys_trigger.issystemobject())
        self.assertEqual(sys_trigger.get_quoted_name(), 'RDB$TRIGGER_1')
        self.assertListEqual(sys_trigger.get_dependents(), [])
        self.assertListEqual(sys_trigger.get_dependencies(), [])
        # User trigger
        c = self.con.schema.get_trigger('SET_EMP_NO')
        # common properties
        self.assertEqual(c.name, 'SET_EMP_NO')
        self.assertIsNone(c.description)
        self.assertListEqual(c.actions, ['create', 'recreate', 'alter', 'create_or_alter', 'drop'])
        self.assertFalse(c.issystemobject())
        self.assertEqual(c.get_quoted_name(), 'SET_EMP_NO')
        self.assertListEqual(c.get_dependents(), [])
        d = c.get_dependencies()
        self.assertListEqual(
            [(x.depended_on_name,x.field_name,x.depended_on_type) for x in d],
            [('EMPLOYEE', 'EMP_NO', 0), ('EMP_NO_GEN', None, 11)]
        )
        #
        self.assertEqual(c.relation.name, 'EMPLOYEE')
        self.assertEqual(c.sequence, 0)
        self.assertEqual(c.trigger_type, 1)
        self.assertEqual(
            c.source.replace('\r', ''),
            'AS\nBEGIN\n  if (new.emp_no is null) then\n  new.emp_no = gen_id(emp_no_gen, 1);\nEND'
        )

        self.assertEqual(c.flags, 1)
        #
        self.assertTrue(c.isactive())
        self.assertTrue(c.isbefore())
        self.assertFalse(c.isafter())
        self.assertFalse(c.isdbtrigger())
        self.assertTrue(c.isinsert())
        self.assertFalse(c.isupdate())
        self.assertFalse(c.isdelete())
        self.assertEqual(c.get_type_as_string(), 'BEFORE INSERT')
        #
        self.assertEqual(
            c.get_sql_for('create').replace('\r', ''),
            'CREATE TRIGGER SET_EMP_NO FOR EMPLOYEE ACTIVE\n'
            'BEFORE INSERT POSITION 0\nAS\nBEGIN\n  if (new.emp_no is null) then\n  '
            'new.emp_no = gen_id(emp_no_gen, 1);\nEND'
        )
        with self.assertRaises(idb.ProgrammingError) as cm:
            c.get_sql_for('alter')
        self.assertTupleEqual(cm.exception.args, ("Header or body definition required.",))
        with self.assertRaises(idb.ProgrammingError) as cm:
            c.get_sql_for('alter', declare="DECLARE VARIABLE i integer;")
        self.assertTupleEqual(cm.exception.args, ("Header or body definition required.",))
        self.assertEqual(
            c.get_sql_for(
                'alter',
                fire_on='AFTER INSERT',
                active=False,
                sequence=0,
                declare='  DECLARE VARIABLE i integer;\n  DECLARE VARIABLE x integer;',
                code='  i = 1;\n  x = 2;'
            ),
            'ALTER TRIGGER SET_EMP_NO INACTIVE\n  '
            'AFTER INSERT\n  '
            'POSITION 0'
            '\nAS\n  '
            'DECLARE VARIABLE i integer;\n  '
            'DECLARE VARIABLE x integer;'
            '\nBEGIN\n  '
            'i = 1;\n  '
            'x = 2;'
            '\nEND'
        )
        self.assertEqual(
            c.get_sql_for(
                'alter',
                declare=['DECLARE VARIABLE i integer;', 'DECLARE VARIABLE x integer;'],
                code=['i = 1;', 'x = 2;']
            ),
            'ALTER TRIGGER SET_EMP_NO'
            '\nAS\n  '
            'DECLARE VARIABLE i integer;'
            '\n  DECLARE VARIABLE x integer;'
            '\nBEGIN\n  '
            'i = 1;'
            '\n  x = 2;'
            '\nEND'
        )
        self.assertEqual(c.get_sql_for('alter', active=False), "ALTER TRIGGER SET_EMP_NO INACTIVE")
        self.assertEqual(
            c.get_sql_for('alter', sequence=10, code=('i = 1;', 'x = 2;')),
            'ALTER TRIGGER SET_EMP_NO\n  '
            'POSITION 10'
            '\nAS\n'
            'BEGIN\n  '
            'i = 1;\n  '
            'x = 2;\n'
            'END'
        )
        with self.assertRaises(idb.ProgrammingError) as cm:
            c.get_sql_for('alter', fire_on='ON CONNECT')
        self.assertTupleEqual(cm.exception.args,
                              ("Trigger type change is not allowed.",))
        self.assertEqual(
            c.get_sql_for('create_or_alter').replace('\r', ''),
            'CREATE OR ALTER TRIGGER SET_EMP_NO FOR EMPLOYEE ACTIVE\n'
            'BEFORE INSERT POSITION 0\nAS\nBEGIN\n  '
            'if (new.emp_no is null) then\n  new.emp_no = gen_id(emp_no_gen, 1);\nEND'
        )
        self.assertEqual(c.get_sql_for('drop'), "DROP TRIGGER SET_EMP_NO")
        # Multi-trigger
        c = self.con.schema.get_trigger('TR_MULTI')
        #
        self.assertTrue(c.isinsert())
        self.assertEqual(c.get_type_as_string(), 'AFTER INSERT')

    def testProcedureParameter(self):
        # Input parameter
        c = self.con.schema.get_procedure('GET_EMP_PROJ').input_params[0]
        # common properties
        self.assertEqual(c.name, 'EMP_NO')
        self.assertIsNone(c.description)
        self.assertListEqual(c.actions, [])
        self.assertFalse(c.issystemobject())
        self.assertEqual(c.get_quoted_name(), 'EMP_NO')
        self.assertListEqual(c.get_dependents(), [])
        self.assertListEqual(c.get_dependencies(), [])
        #
        self.assertEqual(c.procedure.name,'GET_EMP_PROJ')
        self.assertEqual(c.sequence,0)
        self.assertEqual(c.domain.name,'RDB$94')
        self.assertEqual(c.datatype,'SMALLINT')
        self.assertEqual(c.type_from,idb.schema.PROCPAR_DATATYPE)
        self.assertIsNone(c.default)
        self.assertIsNone(c.collation)
        self.assertIsNone(c.column)
        #
        self.assertTrue(c.isinput())
        self.assertTrue(c.isnullable())
        self.assertFalse(c.has_default())
        self.assertEqual(c.get_sql_definition(), 'EMP_NO SMALLINT')
        # Output parameter
        c = self.con.schema.get_procedure('GET_EMP_PROJ').output_params[0]
        # common properties
        self.assertEqual(c.name, 'PROJ_ID')
        self.assertIsNone(c.description)
        self.assertListEqual(c.actions, [])
        self.assertFalse(c.issystemobject())
        self.assertEqual(c.get_quoted_name(), 'PROJ_ID')
        self.assertListEqual(c.get_dependents(), [])
        self.assertListEqual(c.get_dependencies(), [])
        #
        self.assertFalse(c.isinput())
        self.assertEqual(c.get_sql_definition(),'PROJ_ID CHAR(5)')

    def testProcedure(self):
        c = self.con.schema.get_procedure('GET_EMP_PROJ')
        # common properties
        self.assertEqual(c.name, 'GET_EMP_PROJ')
        self.assertIsNone(c.description)
        self.assertListEqual(c.actions,
                             ['create', 'recreate', 'alter', 'create_or_alter', 'drop'])
        self.assertFalse(c.issystemobject())
        self.assertEqual(c.get_quoted_name(), 'GET_EMP_PROJ')
        self.assertListEqual(c.get_dependents(), [])
        d = c.get_dependencies()
        self.assertListEqual([(x.depended_on_name, x.field_name, x.depended_on_type) for x in d],
                             [('EMPLOYEE_PROJECT', 'PROJ_ID', 0), ('EMPLOYEE_PROJECT', 'EMP_NO', 0),
                              ('EMPLOYEE_PROJECT', None, 0)])
        #
        self.assertIsNone(c.valid_blr)
        self.assertEqual(c.id, 7)
        self.assertEqual(
            c.source.replace('\r', ''),
            '\nBEGIN\n    '
            'FOR SELECT proj_id\n        '
            'FROM employee_project\n        '
            'WHERE emp_no = :emp_no\n        '
            'INTO :proj_id\n    DO\n        '
            'SUSPEND;\nEND'
        )
        self.assertEqual(c.security_class,'SQL$GET_EMP_PROJ')
        self.assertEqual(c.owner_name,'SYSDBA')
        self.assertListEqual([x.name for x in c.input_params],['EMP_NO'])
        self.assertListEqual([x.name for x in c.output_params],['PROJ_ID'])
        self.assertEqual(c.proc_type,0)
        #
        self.assertEqual(c.get_param('EMP_NO').name, 'EMP_NO')
        self.assertEqual(c.get_param('PROJ_ID').name, 'PROJ_ID')
        #
        query = 'CREATE PROCEDURE GET_EMP_PROJ (EMP_NO SMALLINT)\n' \
                'RETURNS (PROJ_ID CHAR(5))\nAS\n\n' \
                'BEGIN\n    ' \
                'FOR SELECT proj_id\n        ' \
                'FROM employee_project\n        ' \
                'WHERE emp_no = :emp_no\n        ' \
                'INTO :proj_id\n    DO\n        SUSPEND;\n' \
                'END'

        self.assertEqual(c.get_sql_for('create').replace('\r', ''), query)
        self.assertEqual(c.get_sql_for('create',no_code=True),
"""CREATE PROCEDURE GET_EMP_PROJ (EMP_NO SMALLINT)
RETURNS (PROJ_ID CHAR(5))
AS
BEGIN
END""")
        query = 'CREATE OR ALTER PROCEDURE GET_EMP_PROJ (EMP_NO SMALLINT)\n' \
                'RETURNS (PROJ_ID CHAR(5))\n' \
                'AS\n\nBEGIN\n    ' \
                'FOR SELECT proj_id\n        ' \
                'FROM employee_project\n        ' \
                'WHERE emp_no = :emp_no\n        ' \
                'INTO :proj_id\n    DO\n        SUSPEND;\nEND'
        self.assertEqual(c.get_sql_for('create_or_alter').replace('\r', ''), query)
        self.assertEqual(c.get_sql_for('create_or_alter',no_code=True),
"""CREATE OR ALTER PROCEDURE GET_EMP_PROJ (EMP_NO SMALLINT)
RETURNS (PROJ_ID CHAR(5))
AS
BEGIN
END""")
        self.assertEqual(c.get_sql_for('drop'),"DROP PROCEDURE GET_EMP_PROJ")
        self.assertEqual(c.get_sql_for('alter',code="  /* PASS */"),
"""ALTER PROCEDURE GET_EMP_PROJ
AS
BEGIN
  /* PASS */
END""")
        with self.assertRaises(idb.ProgrammingError) as cm:
            c.get_sql_for('alter',declare="DECLARE VARIABLE i integer;")
        self.assertTupleEqual(cm.exception.args, ("Missing required parameter: 'code'.",))
        self.assertEqual(c.get_sql_for('alter', code=''), """ALTER PROCEDURE GET_EMP_PROJ\nAS\nBEGIN\nEND""")
        self.assertEqual(
            c.get_sql_for('alter', input="IN1 integer", code=''),
            """ALTER PROCEDURE GET_EMP_PROJ (IN1 integer)\nAS\nBEGIN\nEND"""
        )
        self.assertEqual(
            c.get_sql_for('alter', output="OUT1 integer", code=''),
            """ALTER PROCEDURE GET_EMP_PROJ\nRETURNS (OUT1 integer)\nAS\nBEGIN\nEND"""
        )
        self.assertEqual(
            c.get_sql_for('alter', input="IN1 integer", output="OUT1 integer", code=''),
            """ALTER PROCEDURE GET_EMP_PROJ (IN1 integer)\nRETURNS (OUT1 integer)\nAS\nBEGIN\nEND"""
        )
        self.assertEqual(
            c.get_sql_for('alter', input=["IN1 integer", "IN2 VARCHAR(10)"], code=''),
            """ALTER PROCEDURE GET_EMP_PROJ (\n  IN1 integer,\n  IN2 VARCHAR(10)\n)\nAS\nBEGIN\nEND"""
        )
        self.assertEqual(
            c.get_sql_for('alter', output=["OUT1 integer", "OUT2 VARCHAR(10)"], code=''),
            """ALTER PROCEDURE GET_EMP_PROJ\nRETURNS (\n  OUT1 integer,\n  OUT2 VARCHAR(10)\n)\nAS\nBEGIN\nEND"""
        )
        self.assertEqual(
            c.get_sql_for(
                'alter',
                input=["IN1 integer", "IN2 VARCHAR(10)"],
                output=["OUT1 integer", "OUT2 VARCHAR(10)"],
                code=''
            ),
            'ALTER PROCEDURE GET_EMP_PROJ (\n  IN1 integer,\n  IN2 VARCHAR(10)\n)\nRETURNS (\n  OUT1 integer,\n  '
            'OUT2 VARCHAR(10)\n)\nAS\nBEGIN\nEND'
        )
        self.assertEqual(
            c.get_sql_for('alter', code="  -- line 1;\n  -- line 2;"),
            """ALTER PROCEDURE GET_EMP_PROJ\nAS\nBEGIN\n  -- line 1;\n  -- line 2;\nEND"""
        )
        self.assertEqual(
            c.get_sql_for('alter', code=["-- line 1;", "-- line 2;"]),
            """ALTER PROCEDURE GET_EMP_PROJ\nAS\nBEGIN\n  -- line 1;\n  -- line 2;\nEND"""
        )
        self.assertEqual(c.get_sql_for('alter', code="  /* PASS */",
                                       declare="  -- line 1;\n  -- line 2;"),
"""ALTER PROCEDURE GET_EMP_PROJ
AS
  -- line 1;
  -- line 2;
BEGIN
  /* PASS */
END""")
        self.assertEqual(c.get_sql_for('alter',code="  /* PASS */",
                                       declare=["-- line 1;","-- line 2;"]),
"""ALTER PROCEDURE GET_EMP_PROJ
AS
  -- line 1;
  -- line 2;
BEGIN
  /* PASS */
END""")

    def testRole(self):
        c = self.con.schema.get_role('TEST_ROLE')
        # common properties
        self.assertEqual(c.name, 'TEST_ROLE')
        self.assertIsNone(c.description)
        self.assertListEqual(c.actions, ['create', 'drop'])
        self.assertFalse(c.issystemobject())
        self.assertEqual(c.get_quoted_name(), 'TEST_ROLE')
        self.assertListEqual(c.get_dependents(), [])
        self.assertListEqual(c.get_dependencies(), [])
        #
        self.assertEqual(c.owner_name, 'SYSDBA')
        #
        self.assertEqual(c.get_sql_for('create'), "CREATE ROLE TEST_ROLE")
        self.assertEqual(c.get_sql_for('drop'), "DROP ROLE TEST_ROLE")

    def _mockFunction(self, name):
        f = None
        if name == 'STRLEN':
            f = sm.Function(self.con.schema,
                            {'RDB$ENTRYPOINT': 'IB_UDF_strlen                  ',
                             'RDB$SYSTEM_FLAG': 0, 'RDB$RETURN_ARGUMENT': 0,
                             'RDB$MODULE_NAME': 'ib_udf', 'RDB$FUNCTION_TYPE': None,
                             'RDB$DESCRIPTION': None,
                             'RDB$FUNCTION_NAME': 'STRLEN                         '})
            f._load_arguments(
                [{'RDB$FIELD_PRECISION': 0, 'RDB$FIELD_LENGTH': 4,
                  'RDB$FIELD_SCALE': 0, 'RDB$FIELD_SUB_TYPE': 0,
                  'RDB$FIELD_TYPE': 8, 'RDB$MECHANISM': 0,
                  'RDB$CHARACTER_SET_ID': None, 'RDB$CHARACTER_LENGTH': None,
                  'RDB$FUNCTION_NAME': 'STRLEN                         ',
                  'RDB$ARGUMENT_POSITION': 0},
                 {'RDB$FIELD_PRECISION': None, 'RDB$FIELD_LENGTH': 32767,
                  'RDB$FIELD_SCALE': 0, 'RDB$FIELD_SUB_TYPE': 0,
                  'RDB$FIELD_TYPE': 40, 'RDB$MECHANISM': 1,
                  'RDB$CHARACTER_SET_ID': 0, 'RDB$CHARACTER_LENGTH': 32767,
                  'RDB$FUNCTION_NAME': 'STRLEN                         ',
                  'RDB$ARGUMENT_POSITION': 1}])
        elif name == 'STRING2BLOB':
            f = sm.Function(self.con.schema,
                            {'RDB$ENTRYPOINT': 'string2blob                    ',
                             'RDB$SYSTEM_FLAG': 0, 'RDB$RETURN_ARGUMENT': 2,
                             'RDB$MODULE_NAME': 'ibudf', 'RDB$FUNCTION_TYPE': None,
                             'RDB$DESCRIPTION': None,
                             'RDB$FUNCTION_NAME': 'STRING2BLOB                    '})
            f._load_arguments(
                [{'RDB$FIELD_PRECISION': None, 'RDB$FIELD_LENGTH': 300,
                  'RDB$FIELD_SCALE': 0, 'RDB$FIELD_SUB_TYPE': 0,
                  'RDB$FIELD_TYPE': 37, 'RDB$MECHANISM': 2,
                  'RDB$CHARACTER_SET_ID': 0, 'RDB$CHARACTER_LENGTH': 300,
                  'RDB$FUNCTION_NAME': 'STRING2BLOB                    ',
                  'RDB$ARGUMENT_POSITION': 1},
                 {'RDB$FIELD_PRECISION': None, 'RDB$FIELD_LENGTH': 8,
                  'RDB$FIELD_SCALE': 0, 'RDB$FIELD_SUB_TYPE': 0,
                  'RDB$FIELD_TYPE': 261, 'RDB$MECHANISM': 3,
                  'RDB$CHARACTER_SET_ID': None, 'RDB$CHARACTER_LENGTH': None,
                  'RDB$FUNCTION_NAME': 'STRING2BLOB                    ',
                  'RDB$ARGUMENT_POSITION': 2}])
        elif name == 'LTRIM':
            f = sm.Function(self.con.schema,
                            {'RDB$ENTRYPOINT': 'IB_UDF_ltrim                   ',
                             'RDB$SYSTEM_FLAG': 0, 'RDB$RETURN_ARGUMENT': 0,
                             'RDB$MODULE_NAME': 'ib_udf', 'RDB$FUNCTION_TYPE': None,
                             'RDB$DESCRIPTION': None,
                             'RDB$FUNCTION_NAME': 'LTRIM                          '})
            f._load_arguments(
                [{'RDB$FIELD_PRECISION': None, 'RDB$FIELD_LENGTH': 255,
                  'RDB$FIELD_SCALE': 0, 'RDB$FIELD_SUB_TYPE': 0,
                  'RDB$FIELD_TYPE': 40, 'RDB$MECHANISM': -1,
                  'RDB$CHARACTER_SET_ID': 0, 'RDB$CHARACTER_LENGTH': 255,
                  'RDB$FUNCTION_NAME': 'LTRIM                          ',
                  'RDB$ARGUMENT_POSITION': 0},
                 {'RDB$FIELD_PRECISION': None, 'RDB$FIELD_LENGTH': 255,
                  'RDB$FIELD_SCALE': 0, 'RDB$FIELD_SUB_TYPE': 0,
                  'RDB$FIELD_TYPE': 40, 'RDB$MECHANISM': 1,
                  'RDB$CHARACTER_SET_ID': 0, 'RDB$CHARACTER_LENGTH': 255,
                  'RDB$FUNCTION_NAME': 'LTRIM                          ',
                  'RDB$ARGUMENT_POSITION': 1}])
        elif name == 'I64NVL':
            f = sm.Function(self.con.schema,
                            {'RDB$ENTRYPOINT': 'idNvl                          ',
                             'RDB$SYSTEM_FLAG': 0, 'RDB$RETURN_ARGUMENT': 0,
                             'RDB$MODULE_NAME': 'ibudf', 'RDB$FUNCTION_TYPE': None,
                             'RDB$DESCRIPTION': None,
                             'RDB$FUNCTION_NAME': 'I64NVL                         '})
            f._load_arguments(
                [{'RDB$FIELD_PRECISION': 18, 'RDB$FIELD_LENGTH': 8,
                  'RDB$FIELD_SCALE': 0, 'RDB$FIELD_SUB_TYPE': 1,
                  'RDB$FIELD_TYPE': 16, 'RDB$MECHANISM': 2,
                  'RDB$CHARACTER_SET_ID': None, 'RDB$CHARACTER_LENGTH': None,
                  'RDB$FUNCTION_NAME': 'I64NVL                         ',
                  'RDB$ARGUMENT_POSITION': 0},
                 {'RDB$FIELD_PRECISION': 18, 'RDB$FIELD_LENGTH': 8,
                  'RDB$FIELD_SCALE': 0, 'RDB$FIELD_SUB_TYPE': 1,
                  'RDB$FIELD_TYPE': 16, 'RDB$MECHANISM': 2,
                  'RDB$CHARACTER_SET_ID': None, 'RDB$CHARACTER_LENGTH': None,
                  'RDB$FUNCTION_NAME': 'I64NVL                         ',
                  'RDB$ARGUMENT_POSITION': 1},
                 {'RDB$FIELD_PRECISION': 18, 'RDB$FIELD_LENGTH': 8,
                  'RDB$FIELD_SCALE': 0, 'RDB$FIELD_SUB_TYPE': 1,
                  'RDB$FIELD_TYPE': 16, 'RDB$MECHANISM': 2,
                  'RDB$CHARACTER_SET_ID': None, 'RDB$CHARACTER_LENGTH': None,
                  'RDB$FUNCTION_NAME': 'I64NVL                         ',
                  'RDB$ARGUMENT_POSITION': 2}])
        if f:
            return f
        else:
            raise Exception("Udefined function for mock.")

    def testFunctionArgument(self):
        f = self._mockFunction('STRLEN')
        c = f.arguments[0]
        self.assertEqual(len(f.arguments), 1)
        # common properties
        self.assertEqual(c.name, 'STRLEN_1')
        self.assertIsNone(c.description)
        self.assertListEqual(c.actions, [])
        self.assertFalse(c.issystemobject())
        self.assertEqual(c.get_quoted_name(), 'STRLEN_1')
        self.assertListEqual(c.get_dependents(), [])
        self.assertListEqual(c.get_dependencies(), [])
        #
        self.assertEqual(c.function.name, 'STRLEN')
        self.assertEqual(c.position, 1)
        self.assertEqual(c.mechanism, 1)
        self.assertEqual(c.field_type, 40)
        self.assertEqual(c.length, 32767)
        self.assertEqual(c.scale, 0)
        self.assertIsNone(c.precision)
        self.assertEqual(c.sub_type,0)
        self.assertEqual(c.character_length,32767)
        self.assertEqual(c.character_set.name,'NONE')
        self.assertEqual(c.datatype,'CSTRING(32767) CHARACTER SET NONE')
        #
        self.assertFalse(c.isbyvalue())
        self.assertTrue(c.isbyreference())
        self.assertFalse(c.isbydescriptor())
        self.assertFalse(c.iswithnull())
        self.assertFalse(c.isfreeit())
        self.assertFalse(c.isreturning())
        self.assertEqual(c.get_sql_definition(), 'CSTRING(32767) CHARACTER SET NONE')
        #
        c = f.returns
        #
        self.assertEqual(c.position, 0)
        self.assertEqual(c.mechanism, 0)
        self.assertEqual(c.field_type, 8)
        self.assertEqual(c.length, 4)
        self.assertEqual(c.scale, 0)
        self.assertEqual(c.precision, 0)
        self.assertEqual(c.sub_type, 0)
        self.assertIsNone(c.character_length)
        self.assertIsNone(c.character_set)
        self.assertEqual(c.datatype, 'INTEGER')
        #
        self.assertTrue(c.isbyvalue())
        self.assertFalse(c.isbyreference())
        self.assertFalse(c.isbydescriptor())
        self.assertFalse(c.iswithnull())
        self.assertFalse(c.isfreeit())
        self.assertTrue(c.isreturning())
        self.assertEqual(c.get_sql_definition(), 'INTEGER BY VALUE')
        #
        f = self._mockFunction('STRING2BLOB')
        self.assertEqual(len(f.arguments), 2)
        c = f.arguments[0]
        self.assertEqual(c.function.name, 'STRING2BLOB')
        self.assertEqual(c.position, 1)
        self.assertEqual(c.mechanism, 2)
        self.assertEqual(c.field_type, 37)
        self.assertEqual(c.length, 300)
        self.assertEqual(c.scale, 0)
        self.assertIsNone(c.precision)
        self.assertEqual(c.sub_type, 0)
        self.assertEqual(c.character_length, 300)
        self.assertEqual(c.character_set.name, 'NONE')
        self.assertEqual(c.datatype, 'VARCHAR(300) CHARACTER SET NONE')
        #
        self.assertFalse(c.isbyvalue())
        self.assertFalse(c.isbyreference())
        self.assertTrue(c.isbydescriptor())
        self.assertFalse(c.iswithnull())
        self.assertFalse(c.isfreeit())
        self.assertFalse(c.isreturning())
        self.assertEqual(c.get_sql_definition(),'VARCHAR(300) CHARACTER SET NONE BY DESCRIPTOR')
        #
        c = f.arguments[1]
        self.assertIs(f.arguments[1], f.returns)
        self.assertEqual(c.function.name, 'STRING2BLOB')
        self.assertEqual(c.position, 2)
        self.assertEqual(c.mechanism, 3)
        self.assertEqual(c.field_type, 261)
        self.assertEqual(c.length, 8)
        self.assertEqual(c.scale, 0)
        self.assertIsNone(c.precision)
        self.assertEqual(c.sub_type, 0)
        self.assertIsNone(c.character_length)
        self.assertIsNone(c.character_set)
        self.assertEqual(c.datatype, 'BLOB')
        #
        self.assertFalse(c.isbyvalue())
        self.assertFalse(c.isbyreference())
        self.assertFalse(c.isbydescriptor())
        self.assertTrue(c.isbydescriptor(any=True))
        self.assertFalse(c.iswithnull())
        self.assertFalse(c.isfreeit())
        self.assertTrue(c.isreturning())
        self.assertEqual(c.get_sql_definition(), 'BLOB')
        #
        f = self._mockFunction('LTRIM')
        self.assertEqual(len(f.arguments), 1)
        c = f.arguments[0]
        self.assertEqual(c.function.name, 'LTRIM')
        self.assertEqual(c.position, 1)
        self.assertEqual(c.mechanism, 1)
        self.assertEqual(c.field_type, 40)
        self.assertEqual(c.length, 255)
        self.assertEqual(c.scale, 0)
        self.assertIsNone(c.precision)
        self.assertEqual(c.sub_type,0)
        self.assertEqual(c.character_length,255)
        self.assertEqual(c.character_set.name,'NONE')
        self.assertEqual(c.datatype,'CSTRING(255) CHARACTER SET NONE')
        #
        self.assertFalse(c.isbyvalue())
        self.assertTrue(c.isbyreference())
        self.assertFalse(c.isbydescriptor())
        self.assertFalse(c.iswithnull())
        self.assertFalse(c.isfreeit())
        self.assertFalse(c.isreturning())
        self.assertEqual(c.get_sql_definition(),'CSTRING(255) CHARACTER SET NONE')
        #
        c = f.returns
        self.assertEqual(c.function.name, 'LTRIM')
        self.assertEqual(c.position, 0)
        self.assertEqual(c.mechanism, 1)
        self.assertEqual(c.field_type, 40)
        self.assertEqual(c.length, 255)
        self.assertEqual(c.scale, 0)
        self.assertIsNone(c.precision)
        self.assertEqual(c.sub_type,0)
        self.assertEqual(c.character_length,255)
        self.assertEqual(c.character_set.name,'NONE')
        self.assertEqual(c.datatype,'CSTRING(255) CHARACTER SET NONE')
        #
        self.assertFalse(c.isbyvalue())
        self.assertTrue(c.isbyreference())
        self.assertFalse(c.isbydescriptor())
        self.assertFalse(c.isbydescriptor(any=True))
        self.assertFalse(c.iswithnull())
        self.assertTrue(c.isfreeit())
        self.assertTrue(c.isreturning())
        self.assertEqual(c.get_sql_definition(),'CSTRING(255) CHARACTER SET NONE')
        #
        f = self._mockFunction('I64NVL')
        self.assertEqual(len(f.arguments), 2)
        for a in f.arguments:
            self.assertEqual(a.datatype, 'NUMERIC(18, 0)')
            self.assertTrue(a.isbydescriptor())
            self.assertEqual(a.get_sql_definition(),
                             'NUMERIC(18, 0) BY DESCRIPTOR')
        self.assertEqual(f.returns.datatype, 'NUMERIC(18, 0)')
        self.assertTrue(f.returns.isbydescriptor())
        self.assertEqual(f.returns.get_sql_definition(),
                         'NUMERIC(18, 0) BY DESCRIPTOR')

    def testFunction(self):
        c = self._mockFunction('STRLEN')
        self.assertEqual(len(c.arguments), 1)
        # common properties
        self.assertEqual(c.name, 'STRLEN')
        self.assertIsNone(c.description)
        self.assertListEqual(c.actions, ['declare', 'drop'])
        self.assertFalse(c.issystemobject())
        self.assertEqual(c.get_quoted_name(), 'STRLEN')
        self.assertListEqual(c.get_dependents(), [])
        self.assertListEqual(c.get_dependencies(), [])
        #
        self.assertEqual(c.module_name, 'ib_udf')
        self.assertEqual(c.entrypoint, 'IB_UDF_strlen')
        self.assertEqual(c.returns.name, 'STRLEN_0')
        self.assertListEqual([a.name for a in c.arguments], ['STRLEN_1'])
        #
        self.assertTrue(c.has_arguments())
        self.assertTrue(c.has_return())
        self.assertFalse(c.has_return_argument())
        #
        self.assertEqual(c.get_sql_for('drop'), "DROP EXTERNAL FUNCTION STRLEN")
        with self.assertRaises(idb.ProgrammingError) as cm:
            c.get_sql_for('drop', badparam='')
        self.assertTupleEqual(cm.exception.args,
                              ("Unsupported parameter(s) 'badparam'",))
        self.assertEqual(c.get_sql_for('declare'),
"""DECLARE EXTERNAL FUNCTION STRLEN
  CSTRING(32767) CHARACTER SET NONE
RETURNS INTEGER BY VALUE
ENTRY_POINT 'IB_UDF_strlen'
MODULE_NAME 'ib_udf'""")
        with self.assertRaises(idb.ProgrammingError) as cm:
            c.get_sql_for('declare',badparam='')
        self.assertTupleEqual(cm.exception.args,
                              ("Unsupported parameter(s) 'badparam'",))
        #
        c = self._mockFunction('STRING2BLOB')
        self.assertEqual(len(c.arguments), 2)
        #
        self.assertTrue(c.has_arguments())
        self.assertTrue(c.has_return())
        self.assertTrue(c.has_return_argument())
        #
        self.assertEqual(c.get_sql_for('declare'),
"""DECLARE EXTERNAL FUNCTION STRING2BLOB
  VARCHAR(300) CHARACTER SET NONE BY DESCRIPTOR,
  BLOB
RETURNS PARAMETER 2
ENTRY_POINT 'string2blob'
MODULE_NAME 'ibudf'""")
        #
        c = self._mockFunction('LTRIM')
        self.assertEqual(len(c.arguments), 1)
        #
        self.assertTrue(c.has_arguments())
        self.assertTrue(c.has_return())
        self.assertFalse(c.has_return_argument())
        #
        self.assertEqual(c.get_sql_for('declare'),
"""DECLARE EXTERNAL FUNCTION LTRIM
  CSTRING(255) CHARACTER SET NONE
RETURNS CSTRING(255) CHARACTER SET NONE FREE_IT
ENTRY_POINT 'IB_UDF_ltrim'
MODULE_NAME 'ib_udf'""")
        #
        c = self._mockFunction('I64NVL')
        self.assertEqual(len(c.arguments), 2)
        #
        self.assertTrue(c.has_arguments())
        self.assertTrue(c.has_return())
        self.assertFalse(c.has_return_argument())
        #
        self.assertEqual(c.get_sql_for('declare'),
                         """DECLARE EXTERNAL FUNCTION I64NVL
  NUMERIC(18, 0) BY DESCRIPTOR,
  NUMERIC(18, 0) BY DESCRIPTOR
RETURNS NUMERIC(18, 0) BY DESCRIPTOR
ENTRY_POINT 'idNvl'
MODULE_NAME 'ibudf'""")

    def testDatabaseFile(self):
        # We have to use mock
        c = sm.DatabaseFile(self.con.schema, {'RDB$FILE_LENGTH': 1000,
                                              'RDB$FILE_NAME': '/path/dbfile.f02',
                                              'RDB$FILE_START': 500,
                                              'RDB$FILE_SEQUENCE': 1})
        # common properties
        self.assertEqual(c.name, 'FILE_1')
        self.assertIsNone(c.description)
        self.assertListEqual(c.actions, [])
        self.assertTrue(c.issystemobject())
        self.assertEqual(c.get_quoted_name(), 'FILE_1')
        self.assertListEqual(c.get_dependents(), [])
        self.assertListEqual(c.get_dependencies(), [])
        #
        self.assertEqual(c.filename, '/path/dbfile.f02')
        self.assertEqual(c.sequence, 1)
        self.assertEqual(c.start, 500)
        self.assertEqual(c.length, 1000)
        #

    def testShadow(self):
        # We have to use mocks
        c = sm.Shadow(self.con.schema, {'RDB$FILE_FLAGS': 1,
                                        'RDB$SHADOW_NUMBER': 3})
        files = []
        files.append(sm.DatabaseFile(self.con.schema, {'RDB$FILE_LENGTH': 500,
                                                       'RDB$FILE_NAME': '/path/shadow.sf1',
                                                       'RDB$FILE_START': 0,
                                                       'RDB$FILE_SEQUENCE': 0}))
        files.append(sm.DatabaseFile(self.con.schema, {'RDB$FILE_LENGTH': 500,
                                                       'RDB$FILE_NAME': '/path/shadow.sf2',
                                                       'RDB$FILE_START': 1000,
                                                       'RDB$FILE_SEQUENCE': 1}))
        files.append(sm.DatabaseFile(self.con.schema, {'RDB$FILE_LENGTH': 0,
                                                       'RDB$FILE_NAME': '/path/shadow.sf3',
                                                       'RDB$FILE_START': 1500,
                                                       'RDB$FILE_SEQUENCE': 2}))
        c.__dict__['_Shadow__files'] = files
        # common properties
        self.assertEqual(c.name, 'SHADOW_3')
        self.assertIsNone(c.description)
        self.assertListEqual(c.actions, ['create', 'drop'])
        self.assertFalse(c.issystemobject())
        self.assertEqual(c.get_quoted_name(), 'SHADOW_3')
        self.assertListEqual(c.get_dependents(), [])
        self.assertListEqual(c.get_dependencies(), [])
        #
        self.assertEqual(c.id, 3)
        self.assertEqual(c.flags, 1)
        self.assertListEqual([(f.name, f.filename, f.start, f.length) for f in c.files],
                             [('FILE_0', '/path/shadow.sf1', 0, 500),
                              ('FILE_1', '/path/shadow.sf2', 1000, 500),
                              ('FILE_2', '/path/shadow.sf3', 1500, 0)])
        #
        self.assertFalse(c.isconditional())
        self.assertFalse(c.isinactive())
        self.assertFalse(c.ismanual())
        #
        self.assertEqual(c.get_sql_for('create'),
"""CREATE SHADOW 3 AUTO '/path/shadow.sf1' LENGTH 500
  FILE '/path/shadow.sf2' STARTING AT 1000 LENGTH 500
  FILE '/path/shadow.sf3' STARTING AT 1500""")
        self.assertEqual(c.get_sql_for('drop'), "DROP SHADOW 3")

    def testPrivilegeBasic(self):
        p = self.con.schema.get_procedure('ALL_LANGS')
        #
        self.assertIsInstance(p.privileges,list)
        self.assertEqual(len(p.privileges),2)
        c = p.privileges[0]
        # common properties
        self.assertIsNone(c.name)
        self.assertIsNone(c.description)
        self.assertListEqual(c.actions, ['grant', 'revoke'])
        self.assertTrue(c.issystemobject())
        self.assertIsNone(c.get_quoted_name())
        self.assertListEqual(c.get_dependents(), [])
        self.assertListEqual(c.get_dependencies(), [])
        #
        self.assertIsInstance(c.user, idb.services.User)
        self.assertIn(c.user.name, ['SYSDBA', 'PUBLIC'])
        self.assertIsInstance(c.grantor, idb.services.User)
        self.assertEqual(c.grantor.name, 'SYSDBA')
        self.assertEqual(c.privilege, 'X')
        self.assertIsInstance(c.subject, sm.Procedure)
        self.assertEqual(c.subject.name, 'ALL_LANGS')
        self.assertIn(c.user_name, ['SYSDBA', 'PUBLIC'])
        self.assertEqual(c.user_type, self.con.schema.enum_object_type_codes['USER'])
        self.assertEqual(c.grantor_name, 'SYSDBA')
        self.assertEqual(c.subject_name, 'ALL_LANGS')
        self.assertEqual(c.subject_type, self.con.schema.enum_object_type_codes['PROCEDURE'])
        self.assertIsNone(c.field_name)
        #
        self.assertFalse(c.has_grant())
        self.assertFalse(c.isselect())
        self.assertFalse(c.isinsert())
        self.assertFalse(c.isupdate())
        self.assertFalse(c.isdelete())
        self.assertTrue(c.isexecute())
        self.assertFalse(c.isreference())
        self.assertFalse(c.ismembership())
        #
        self.assertEqual(c.get_sql_for('grant'),
                         "GRANT EXECUTE ON PROCEDURE ALL_LANGS TO SYSDBA")
        self.assertEqual(c.get_sql_for('grant', grantors=[]),
                         "GRANT EXECUTE ON PROCEDURE ALL_LANGS TO SYSDBA GRANTED BY SYSDBA")
        self.assertEqual(c.get_sql_for('grant', grantors=['SYSDBA', 'TEST_USER']),
                         "GRANT EXECUTE ON PROCEDURE ALL_LANGS TO SYSDBA")
        with self.assertRaises(idb.ProgrammingError) as cm:
            c.get_sql_for('grant', badparam=True)
        self.assertTupleEqual(cm.exception.args,
                              ("Unsupported parameter(s) 'badparam'",))
        self.assertEqual(c.get_sql_for('revoke'),
                         "REVOKE EXECUTE ON PROCEDURE ALL_LANGS FROM SYSDBA")
        self.assertEqual(c.get_sql_for('revoke', grantors=[]),
                         "REVOKE EXECUTE ON PROCEDURE ALL_LANGS FROM SYSDBA GRANTED BY SYSDBA")
        self.assertEqual(c.get_sql_for('revoke', grantors=['SYSDBA', 'TEST_USER']),
                         "REVOKE EXECUTE ON PROCEDURE ALL_LANGS FROM SYSDBA")
        with self.assertRaises(idb.ProgrammingError) as cm:
            c.get_sql_for('revoke', grant_option=True)
        self.assertTupleEqual(cm.exception.args,
                              ("Can't revoke grant option that wasn't granted.",))
        with self.assertRaises(idb.ProgrammingError) as cm:
            c.get_sql_for('revoke', badparam=True)
        self.assertTupleEqual(cm.exception.args,
            ("Unsupported parameter(s) 'badparam'",))
        c = p.privileges[1]
        self.assertEqual(c.get_sql_for('grant'),
            "GRANT EXECUTE ON PROCEDURE ALL_LANGS TO PUBLIC WITH GRANT OPTION")
        self.assertEqual(c.get_sql_for('revoke'),
            "REVOKE EXECUTE ON PROCEDURE ALL_LANGS FROM PUBLIC")
        # get_privileges_of()
        u = idb.services.User('PUBLIC')
        p = self.con.schema.get_privileges_of(u)
        self.assertEqual(len(p), 110)
        with self.assertRaises(idb.ProgrammingError) as cm:
            p = self.con.schema.get_privileges_of('PUBLIC')
        self.assertTupleEqual(cm.exception.args,
                              ("Unknown user_type code.",))
        with self.assertRaises(idb.ProgrammingError) as cm:
            p = self.con.schema.get_privileges_of('PUBLIC', 50)
        self.assertTupleEqual(cm.exception.args,
                              ("Unknown user_type code.",))
        #

    def testPrivilegeExtended(self):
        def get_privilege(obj, privilege):
            x = [x for x in obj.privileges if x.privilege == privilege]
            return x[0]

        p = []
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'SYSDBA',
                                                'RDB$PRIVILEGE': 'X',
                                                'RDB$RELATION_NAME': 'ALL_LANGS',
                                                'RDB$OBJECT_TYPE': 5,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': None}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'PUBLIC',
                                                'RDB$PRIVILEGE': 'X',
                                                'RDB$RELATION_NAME': 'ALL_LANGS',
                                                'RDB$OBJECT_TYPE': 5,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'T_USER',
                                                'RDB$PRIVILEGE': 'X',
                                                'RDB$RELATION_NAME': 'ALL_LANGS',
                                                'RDB$OBJECT_TYPE': 5,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 0}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'TEST_ROLE',
                                                'RDB$PRIVILEGE': 'X',
                                                'RDB$RELATION_NAME': 'ALL_LANGS',
                                                'RDB$OBJECT_TYPE': 5,
                                                'RDB$USER_TYPE': 13,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'PUBLIC',
                                                'RDB$PRIVILEGE': 'X',
                                                'RDB$RELATION_NAME': 'ALL_LANGS',
                                                'RDB$OBJECT_TYPE': 5,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'T_USER',
                                                'RDB$GRANT_OPTION': 0}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'SYSDBA',
                                                'RDB$PRIVILEGE': 'S',
                                                'RDB$RELATION_NAME': 'COUNTRY',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'SYSDBA',
                                                'RDB$PRIVILEGE': 'I',
                                                'RDB$RELATION_NAME': 'COUNTRY',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'SYSDBA',
                                                'RDB$PRIVILEGE': 'U',
                                                'RDB$RELATION_NAME': 'COUNTRY',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'SYSDBA',
                                                'RDB$PRIVILEGE': 'D',
                                                'RDB$RELATION_NAME': 'COUNTRY',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'SYSDBA',
                                                'RDB$PRIVILEGE': 'R',
                                                'RDB$RELATION_NAME': 'COUNTRY',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'PUBLIC',
                                                'RDB$PRIVILEGE': 'S',
                                                'RDB$RELATION_NAME': 'COUNTRY',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'PUBLIC',
                                                'RDB$PRIVILEGE': 'R',
                                                'RDB$RELATION_NAME': 'COUNTRY',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'PUBLIC',
                                                'RDB$PRIVILEGE': 'I',
                                                'RDB$RELATION_NAME': 'COUNTRY',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 0}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'T_USER',
                                                'RDB$PRIVILEGE': 'U',
                                                'RDB$RELATION_NAME': 'COUNTRY',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': 'CURRENCY',
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 0}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'T_USER',
                                                'RDB$PRIVILEGE': 'R',
                                                'RDB$RELATION_NAME': 'COUNTRY',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': 'COUNTRY',
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 0}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'T_USER',
                                                'RDB$PRIVILEGE': 'S',
                                                'RDB$RELATION_NAME': 'COUNTRY',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 0}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'T_USER',
                                                'RDB$PRIVILEGE': 'I',
                                                'RDB$RELATION_NAME': 'COUNTRY',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 0}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'T_USER',
                                                'RDB$PRIVILEGE': 'D',
                                                'RDB$RELATION_NAME': 'COUNTRY',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 0}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'T_USER',
                                                'RDB$PRIVILEGE': 'U',
                                                'RDB$RELATION_NAME': 'COUNTRY',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 0}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'T_USER',
                                                'RDB$PRIVILEGE': 'R',
                                                'RDB$RELATION_NAME': 'COUNTRY',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 0}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'T_USER',
                                                'RDB$PRIVILEGE': 'U',
                                                'RDB$RELATION_NAME': 'COUNTRY',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': 'COUNTRY',
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 0}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'T_USER',
                                                'RDB$PRIVILEGE': 'R',
                                                'RDB$RELATION_NAME': 'COUNTRY',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': 'CURRENCY',
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 0}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'PUBLIC',
                                                'RDB$PRIVILEGE': 'D',
                                                'RDB$RELATION_NAME': 'COUNTRY',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 0}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'PUBLIC',
                                                'RDB$PRIVILEGE': 'U',
                                                'RDB$RELATION_NAME': 'COUNTRY',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 0}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'SYSDBA',
                                                'RDB$PRIVILEGE': 'S',
                                                'RDB$RELATION_NAME': 'DEPARTMENT',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'SYSDBA',
                                                'RDB$PRIVILEGE': 'I',
                                                'RDB$RELATION_NAME': 'DEPARTMENT',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'SYSDBA',
                                                'RDB$PRIVILEGE': 'U',
                                                'RDB$RELATION_NAME': 'DEPARTMENT',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'SYSDBA',
                                                'RDB$PRIVILEGE': 'D',
                                                'RDB$RELATION_NAME': 'DEPARTMENT',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'SYSDBA',
                                                'RDB$PRIVILEGE': 'R',
                                                'RDB$RELATION_NAME': 'DEPARTMENT',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'PUBLIC',
                                                'RDB$PRIVILEGE': 'S',
                                                'RDB$RELATION_NAME': 'DEPARTMENT',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'PUBLIC',
                                                'RDB$PRIVILEGE': 'I',
                                                'RDB$RELATION_NAME': 'DEPARTMENT',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'PUBLIC',
                                                'RDB$PRIVILEGE': 'U',
                                                'RDB$RELATION_NAME': 'DEPARTMENT',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'PUBLIC',
                                                'RDB$PRIVILEGE': 'D',
                                                'RDB$RELATION_NAME': 'DEPARTMENT',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'PUBLIC',
                                                'RDB$PRIVILEGE': 'R',
                                                'RDB$RELATION_NAME': 'DEPARTMENT',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'ORG_CHART',
                                                'RDB$PRIVILEGE': 'S',
                                                'RDB$RELATION_NAME': 'DEPARTMENT',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 5,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 0}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'SYSDBA',
                                                'RDB$PRIVILEGE': 'S',
                                                'RDB$RELATION_NAME': 'EMPLOYEE',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'SYSDBA',
                                                'RDB$PRIVILEGE': 'I',
                                                'RDB$RELATION_NAME': 'EMPLOYEE',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'SYSDBA',
                                                'RDB$PRIVILEGE': 'U',
                                                'RDB$RELATION_NAME': 'EMPLOYEE',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'SYSDBA',
                                                'RDB$PRIVILEGE': 'D',
                                                'RDB$RELATION_NAME': 'EMPLOYEE',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'SYSDBA',
                                                'RDB$PRIVILEGE': 'R',
                                                'RDB$RELATION_NAME': 'EMPLOYEE',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'PUBLIC',
                                                'RDB$PRIVILEGE': 'S',
                                                'RDB$RELATION_NAME': 'EMPLOYEE',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'PUBLIC',
                                                'RDB$PRIVILEGE': 'I',
                                                'RDB$RELATION_NAME': 'EMPLOYEE',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'PUBLIC',
                                                'RDB$PRIVILEGE': 'U',
                                                'RDB$RELATION_NAME': 'EMPLOYEE',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'PUBLIC',
                                                'RDB$PRIVILEGE': 'D',
                                                'RDB$RELATION_NAME': 'EMPLOYEE',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'PUBLIC',
                                                'RDB$PRIVILEGE': 'R',
                                                'RDB$RELATION_NAME': 'EMPLOYEE',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'ORG_CHART',
                                                'RDB$PRIVILEGE': 'S',
                                                'RDB$RELATION_NAME': 'EMPLOYEE',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 5,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 0}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'SYSDBA',
                                                'RDB$PRIVILEGE': 'X',
                                                'RDB$RELATION_NAME': 'ORG_CHART',
                                                'RDB$OBJECT_TYPE': 5,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': None}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'PUBLIC',
                                                'RDB$PRIVILEGE': 'X',
                                                'RDB$RELATION_NAME': 'ORG_CHART',
                                                'RDB$OBJECT_TYPE': 5,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'SYSDBA',
                                                'RDB$PRIVILEGE': 'S',
                                                'RDB$RELATION_NAME': 'PHONE_LIST',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'SYSDBA',
                                                'RDB$PRIVILEGE': 'I',
                                                'RDB$RELATION_NAME': 'PHONE_LIST',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'SYSDBA',
                                                'RDB$PRIVILEGE': 'U',
                                                'RDB$RELATION_NAME': 'PHONE_LIST',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'SYSDBA',
                                                'RDB$PRIVILEGE': 'D',
                                                'RDB$RELATION_NAME': 'PHONE_LIST',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'SYSDBA',
                                                'RDB$PRIVILEGE': 'R',
                                                'RDB$RELATION_NAME': 'PHONE_LIST',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'PUBLIC',
                                                'RDB$PRIVILEGE': 'S',
                                                'RDB$RELATION_NAME': 'PHONE_LIST',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'PUBLIC',
                                                'RDB$PRIVILEGE': 'I',
                                                'RDB$RELATION_NAME': 'PHONE_LIST',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'PUBLIC',
                                                'RDB$PRIVILEGE': 'U',
                                                'RDB$RELATION_NAME': 'PHONE_LIST',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'PUBLIC',
                                                'RDB$PRIVILEGE': 'D',
                                                'RDB$RELATION_NAME': 'PHONE_LIST',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'PUBLIC',
                                                'RDB$PRIVILEGE': 'R',
                                                'RDB$RELATION_NAME': 'PHONE_LIST',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'PUBLIC',
                                                'RDB$PRIVILEGE': 'R',
                                                'RDB$RELATION_NAME': 'PHONE_LIST',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': 'EMP_NO',
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 0}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'SYSDBA',
                                                'RDB$PRIVILEGE': 'S',
                                                'RDB$RELATION_NAME': 'RDB$PAGES',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'SYSDBA',
                                                'RDB$PRIVILEGE': 'I',
                                                'RDB$RELATION_NAME': 'RDB$PAGES',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'SYSDBA',
                                                'RDB$PRIVILEGE': 'U',
                                                'RDB$RELATION_NAME': 'RDB$PAGES',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'SYSDBA',
                                                'RDB$PRIVILEGE': 'D',
                                                'RDB$RELATION_NAME': 'RDB$PAGES',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'SYSDBA',
                                                'RDB$PRIVILEGE': 'R',
                                                'RDB$RELATION_NAME': 'RDB$PAGES',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'PUBLIC',
                                                'RDB$PRIVILEGE': 'S',
                                                'RDB$RELATION_NAME': 'RDB$PAGES',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 0}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'SYSDBA',
                                                'RDB$PRIVILEGE': 'X',
                                                'RDB$RELATION_NAME': 'SHIP_ORDER',
                                                'RDB$OBJECT_TYPE': 5,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': None}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'PUBLIC',
                                                'RDB$PRIVILEGE': 'X',
                                                'RDB$RELATION_NAME': 'SHIP_ORDER',
                                                'RDB$OBJECT_TYPE': 5,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 1}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'T_USER',
                                                'RDB$PRIVILEGE': 'M',
                                                'RDB$RELATION_NAME': 'TEST_ROLE',
                                                'RDB$OBJECT_TYPE': 13,
                                                'RDB$USER_TYPE': 8,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 0}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'SAVE_SALARY_CHANGE',
                                                'RDB$PRIVILEGE': 'I',
                                                'RDB$RELATION_NAME': 'SALARY_HISTORY',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 2,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 0}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'PHONE_LIST',
                                                'RDB$PRIVILEGE': 'S',
                                                'RDB$RELATION_NAME': 'DEPARTMENT',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 1,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 0}))
        p.append(sm.Privilege(self.con.schema, {'RDB$USER': 'PHONE_LIST',
                                                'RDB$PRIVILEGE': 'S',
                                                'RDB$RELATION_NAME': 'EMPLOYEE',
                                                'RDB$OBJECT_TYPE': 0,
                                                'RDB$USER_TYPE': 1,
                                                'RDB$FIELD_NAME': None,
                                                'RDB$GRANTOR': 'SYSDBA',
                                                'RDB$GRANT_OPTION': 0}))
        #
        self.con.schema.__dict__['_Schema__privileges'] = p
        # Table
        p = self.con.schema.get_table('COUNTRY')
        self.assertEqual(len(p.privileges), 19)
        self.assertEqual(len([x for x in p.privileges if x.user_name == 'SYSDBA']), 5)
        self.assertEqual(len([x for x in p.privileges if x.user_name == 'PUBLIC']), 5)
        self.assertEqual(len([x for x in p.privileges if x.user_name == 'T_USER']), 9)
        #
        self.assertTrue(get_privilege(p, 'S').isselect())
        self.assertTrue(get_privilege(p, 'I').isinsert())
        self.assertTrue(get_privilege(p, 'U').isupdate())
        self.assertTrue(get_privilege(p, 'D').isdelete())
        self.assertTrue(get_privilege(p, 'R').isreference())
        #
        x = p.privileges[0]
        self.assertIsInstance(x.subject, sm.Table)
        self.assertEqual(x.subject.name, p.name)
        # TableColumn
        p = p.get_column('CURRENCY')
        self.assertEqual(len(p.privileges), 2)
        x = p.privileges[0]
        self.assertIsInstance(x.subject, sm.Table)
        self.assertEqual(x.field_name, p.name)
        # View
        p = self.con.schema.get_view('PHONE_LIST')
        self.assertEqual(len(p.privileges), 11)
        self.assertEqual(len([x for x in p.privileges if x.user_name == 'SYSDBA']), 5)
        self.assertEqual(len([x for x in p.privileges if x.user_name == 'PUBLIC']), 6)
        #
        x = p.privileges[0]
        self.assertIsInstance(x.subject, sm.View)
        self.assertEqual(x.subject.name, p.name)
        # ViewColumn
        p = p.get_column('EMP_NO')
        self.assertEqual(len(p.privileges), 1)
        x = p.privileges[0]
        self.assertIsInstance(x.subject, sm.View)
        self.assertEqual(x.field_name, p.name)
        # Procedure
        p = self.con.schema.get_procedure('ORG_CHART')
        self.assertEqual(len(p.privileges), 2)
        self.assertEqual(len([x for x in p.privileges if x.user_name == 'SYSDBA']), 1)
        self.assertEqual(len([x for x in p.privileges if x.user_name == 'PUBLIC']), 1)
        #
        x = p.privileges[0]
        self.assertFalse(x.has_grant())
        self.assertIsInstance(x.subject, sm.Procedure)
        self.assertEqual(x.subject.name, p.name)
        #
        x = p.privileges[1]
        self.assertTrue(x.has_grant())
        # Role
        p = self.con.schema.get_role('TEST_ROLE')
        self.assertEqual(len(p.privileges), 1)
        x = p.privileges[0]
        self.assertIsInstance(x.subject, sm.Role)
        self.assertEqual(x.subject.name, p.name)
        self.assertTrue(x.ismembership())
        # Trigger as grantee
        p = self.con.schema.get_table('SALARY_HISTORY')
        x = p.privileges[0]
        self.assertIsInstance(x.user, sm.Trigger)
        self.assertEqual(x.user.name, 'SAVE_SALARY_CHANGE')
        # View as grantee
        p = self.con.schema.get_view('PHONE_LIST')
        x = self.con.schema.get_privileges_of(p)
        self.assertEqual(len(x), 2)
        x = x[0]
        self.assertIsInstance(x.user, sm.View)
        self.assertEqual(x.user.name, 'PHONE_LIST')
        # get_grants()
        self.assertListEqual(sm.get_grants(p.privileges),
                             ['GRANT REFERENCES(EMP_NO) ON PHONE_LIST TO PUBLIC',
                              'GRANT DELETE, INSERT, REFERENCES, SELECT, UPDATE ON PHONE_LIST TO PUBLIC WITH GRANT OPTION',
                              'GRANT DELETE, INSERT, REFERENCES, SELECT, UPDATE ON PHONE_LIST TO SYSDBA WITH GRANT OPTION'])
        p = self.con.schema.get_table('COUNTRY')
        self.assertListEqual(sm.get_grants(p.privileges),
                             ['GRANT DELETE, INSERT, UPDATE ON COUNTRY TO PUBLIC',
                              'GRANT REFERENCES, SELECT ON COUNTRY TO PUBLIC WITH GRANT OPTION',
                              'GRANT DELETE, INSERT, REFERENCES, SELECT, UPDATE ON COUNTRY TO SYSDBA WITH GRANT OPTION',
                              'GRANT DELETE, INSERT, REFERENCES(COUNTRY,CURRENCY), SELECT, UPDATE(COUNTRY,CURRENCY) ON COUNTRY TO T_USER'])
        p = self.con.schema.get_role('TEST_ROLE')
        self.assertListEqual(sm.get_grants(p.privileges), ['GRANT TEST_ROLE TO T_USER'])
        p = self.con.schema.get_table('SALARY_HISTORY')
        self.assertListEqual(sm.get_grants(p.privileges),
            ['GRANT INSERT ON SALARY_HISTORY TO TRIGGER SAVE_SALARY_CHANGE'])
        p = self.con.schema.get_procedure('ORG_CHART')
        self.assertListEqual(sm.get_grants(p.privileges),
            ['GRANT EXECUTE ON PROCEDURE ORG_CHART TO PUBLIC WITH GRANT OPTION',
             'GRANT EXECUTE ON PROCEDURE ORG_CHART TO SYSDBA'])


    def testVisitor(self):
        v = SchemaVisitor(self, 'create', follow='dependencies')
        c = self.con.schema.get_procedure('ALL_LANGS')
        c.accept_visitor(v)
        self.maxDiff = None
        output = "CREATE TABLE JOB\n" \
                 "(\n  JOB_CODE VARCHAR(5) NOT NULL,\n  " \
                 "JOB_GRADE JOBGRADE NOT NULL,\n  " \
                 "JOB_COUNTRY COUNTRYNAME NOT NULL,\n  " \
                 "JOB_TITLE VARCHAR(25) NOT NULL,\n  MIN_SALARY SALARY NOT NULL,\n  " \
                 "MAX_SALARY SALARY NOT NULL,\n  " \
                 "JOB_REQUIREMENT BLOB SUB_TYPE TEXT SEGMENT SIZE 80,\n  " \
                 "LANGUAGE_REQ VARCHAR(255)[5],\n  " \
                 "CONSTRAINT RDB$PRIMARY2\n  PRIMARY KEY (JOB_CODE,JOB_GRADE,JOB_COUNTRY)\n)\n" \
                 "CREATE PROCEDURE SHOW_LANGS (\n  CODE VARCHAR(5),\n  " \
                 "GRADE SMALLINT,\n  CTY VARCHAR(15)\n)\nRETURNS (LANGUAGES VARCHAR(15))\nAS\n\n" \
                 "DECLARE VARIABLE i INTEGER;\nBEGIN\n  i = 1;\n  WHILE (i <= 5) DO\n  " \
                 "BEGIN\n  SELECT language_req[:i] FROM joB\n  WHERE ((job_code = :code) " \
                 "AND (job_grade = :grade) AND (job_country = :cty)\n       " \
                 "AND (language_req IS NOT NULL))\n  INTO :languages;\n  IF (languages = ' ') " \
                 "THEN  /* Prints 'NULL' instead of blanks */\n     " \
                 "languages = 'NULL';\n  i = i +1;\n  SUSPEND;\n  " \
                 "END\nEND\nCREATE PROCEDURE ALL_LANGS\n" \
                 "RETURNS " \
                 "(\n  CODE VARCHAR(5),\n  GRADE VARCHAR(5),\n  COUNTRY VARCHAR(15),\n  " \
                 "LANG VARCHAR(15)\n)\nAS\n\nBEGIN\n    FOR SELECT job_code, job_grade, job_country FROM job\n        " \
                 "INTO :code, :grade, :country\n\n    DO\n    BEGIN\n      " \
                 "FOR SELECT languages FROM SHOW_LANGS\n          (:code, :grade, :country) INTO :lang " \
                 "DO\n        SUSPEND;\n      /* Put nice separators between rows */\n      code = '=====';\n      " \
                 "grade = '=====';\n      country = '===============';\n      lang = '==============';\n      " \
                 "SUSPEND;\n    END\nEND\n"
        self.assertEqual(self.output.getvalue().replace('\r', ''), output)

        v = SchemaVisitor(self, 'drop', follow='dependents')
        c = self.con.schema.get_table('JOB')
        self.clear_output()
        c.accept_visitor(v)
        self.assertEqual(self.output.getvalue(), """DROP PROCEDURE ALL_LANGS
DROP PROCEDURE SHOW_LANGS
DROP TABLE JOB
""")
