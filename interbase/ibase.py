#coding:utf-8
#
#   PROGRAM/MODULE: idb
#   FILE:           ibase.py
#   DESCRIPTION:    Python ctypes interface to InterBase client library
#   CREATED:        6.10.2011
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
import locale
import types
import operator
import platform
import os

from ctypes import *
from ctypes.util import find_library


PYTHON_MAJOR_VER = sys.version_info[0]

#-------------------

if PYTHON_MAJOR_VER == 3:
    from queue import PriorityQueue
    def nativestr(st,charset="latin-1"):
        if st == None:
            return st
        elif isinstance(st, bytes):
            return st.decode(charset)
        else:
            return st
    def b(st,charset="latin-1"):
        if st == None:
            return st
        elif isinstance(st, bytes):
            return st
        else:
            try:
                return st.encode(charset)
            except UnicodeEncodeError:
                return st

    def s(st):
        return st

    ord2 = lambda x: x if type(x) == IntType else ord(x)

    if sys.version_info[1] <= 1:
        def int2byte(i):
            return bytes((i,))
    else:
        # This is about 2x faster than the implementation above on 3.2+
        int2byte = operator.methodcaller("to_bytes", 1, "big")

    def mychr(i):
        return i

    mybytes = bytes
    myunicode = str
    mylong = int
    StringType = str
    IntType = int
    LongType = int
    FloatType = float
    ListType = list
    UnicodeType = str
    TupleType = tuple
    xrange = range

else:
    from Queue import PriorityQueue
    def nativestr(st,charset="latin-1"):
        if st == None:
            return st
        elif isinstance(st, unicode):
            return st.encode(charset)
        else:
            return st
    def b(st,charset="latin-1"):
        if st == None:
            return st
        elif isinstance(st, types.StringType):
            return st
        else:
            try:
                return st.encode(charset)
            except UnicodeEncodeError:
                return st

    int2byte = chr
    s = str
    ord2 = ord

    def mychr(i):
        return chr(i)

    mybytes = str
    myunicode = unicode
    mylong = long
    StringType = types.StringType
    IntType = types.IntType
    LongType = types.LongType
    FloatType = types.FloatType
    ListType = types.ListType
    UnicodeType = types.UnicodeType
    TupleType = types.TupleType
    xrange = xrange

# Support routines from ctypesgen generated file.

# As of ctypes 1.0, ctypes does not support custom error-checking
# functions on callbacks, nor does it support custom datatypes on
# callbacks, so we must ensure that all callbacks return
# primitive datatypes.
#
# Non-primitive return values wrapped with UNCHECKED won't be
# typechecked, and will be converted to c_void_p.
def UNCHECKED(type):
    if (hasattr(type, "_type_") and isinstance(type._type_, str)
        and type._type_ != "P"):
        return type
    else:
        return c_void_p

# ibase.h

IB_API_VER = 25
MAX_BLOB_SEGMENT_SIZE = 65535

# Event queue operation (and priority) codes

OP_DIE      = 1
OP_RECORD_AND_REREGISTER = 2

charset_map = {
    # DB CHAR SET NAME    :   PYTHON CODEC NAME (CANONICAL)
    # -------------------------------------------------------------------------
    None                  :   locale.getpreferredencoding(),
    'NONE'                :   locale.getpreferredencoding(),
    'OCTETS'              :   None,  # Allow to pass through unchanged.
    'UNICODE_FSS'         :   'utf_8',
    'UNICODE_LE'          :   'utf_16_le',
    'UTF8'                :   'utf_8',
    'SJIS_0208'           :   'shift_jis',
    'EUCJ_0208'           :   'euc_jp',
    'DOS437'              :   'cp437',
    'DOS850'              :   'cp850',
    'DOS865'              :   'cp865',
    'DOS860'              :   'cp860',
    'DOS863'              :   'cp863',
    'ISO8859_1'           :   'iso8859_1',
    'ISO8859_2'           :   'iso8859_2',
    'ISO8859_15'          :   'iso8859_15',
    'KSC_5601'            :   'euc_kr',
    'DOS852'              :   'cp852',
    'DOS857'              :   'cp857',
    'DOS861'              :   'cp861',
    'WIN1250'             :   'cp1250',
    'WIN1251'             :   'cp1251',
    'WIN1252'             :   'cp1252',
    'WIN1253'             :   'cp1253',
    'WIN1254'             :   'cp1254',
    'BIG_5'               :   'big5',
    'GB_2312'             :   'gb2312',
    'KOI8R'               :   'koi8_r',
    'UNICODE_BE'          :   'utf_16_be',
    'ASCII'               :   'ascii',
#    'NEXT'                :   '', 
#    'CYRL'                :   '',
    }

DB_CHAR_SET_NAME_TO_PYTHON_ENCODING_MAP = charset_map

# C integer limit constants

SHRT_MIN = -32767
SHRT_MAX = 32767
USHRT_MAX = 65535
INT_MIN = -2147483648
INT_MAX = 2147483647
LONG_MIN = -9223372036854775808
LONG_MAX = 9223372036854775807
SSIZE_T_MIN = INT_MIN
SSIZE_T_MAX = INT_MAX
DSC_VERSION1_TO_CURRENT = 0
DSC_VERSION2 = 2
BLB_DESC_VERSION2 = DSC_VERSION2
BLB_DESC_CURRENT_VERSION = DSC_VERSION2
ARR_DESC_VERSION2 = 2
ARR_DESC_CURRENT_VERSION = ARR_DESC_VERSION2

DSC_system = 8
DSC_nullable = 4
DSC_null = 1
DSC_no_subtype = 2
DSC_CURRENT_TO_VERSION1 = 1

# Constants

DSQL_close = 1
DSQL_drop = 2
DSQL_unprepare = 4
DSQL_cancel = 4
SQLDA_version1 = 1
SQLDA_version2 = 2

# Type codes

SQL_TEXT = 452
SQL_VARYING = 448
SQL_SHORT = 500
SQL_LONG = 496
SQL_FLOAT = 482
SQL_DOUBLE = 480
SQL_D_FLOAT = 530
SQL_TIMESTAMP = 510
SQL_BLOB = 520
SQL_ARRAY = 540
SQL_QUAD = 550
SQL_TYPE_TIME = 560
SQL_TYPE_DATE = 570
SQL_INT64 = 580

SQLIND_NULL = (1 << 15)
SQLIND_INSERT = (1 << 0)
SQLIND_UPDATE = (1 << 1)
SQLIND_DELETE = (1 << 2)
SQLIND_CHANGE = (1 << 3)
SQLIND_TRUNCATE = (1 << 4)
SQLIND_CHANGE_VIEW = (1 << 5)

SUBTYPE_NUMERIC = 1
SUBTYPE_DECIMAL = 2

# These verbs were added in 7.1 for SQL savepoint support
blr_start_savepoint2 = 176
blr_release_savepoint = 177
blr_rollback_savepoint = 178

# START CONVERT TAG
isc_err_factor = 1
isc_arg_end = 0
isc_arg_gds = 1
isc_arg_string = 2
isc_arg_cstring = 3
isc_arg_number = 4
isc_arg_interpreted = 5
isc_arg_vms = 6
isc_arg_unix = 7
isc_arg_domain = 8
isc_arg_dos = 9
isc_arg_mpexl = 10
isc_arg_mpexl_ipc = 11
isc_arg_next_mach = 15
isc_arg_netware = 16
isc_arg_win32 = 17
isc_arg_warning = 18
isc_arg_sql = 19
isc_arg_int64 = 20

# Internal type codes (for example used by ARRAY descriptor)

blr_text = 14
blr_text2 = 15
blr_short = 7
blr_long = 8
blr_quad = 9
blr_float = 10
blr_double = 27
blr_d_float = 11
blr_timestamp = 35
blr_varying = 37
blr_varying2 = 38
blr_blob = 261
blr_cstring = 40
blr_cstring2 = 41
blr_blob_id = 45
blr_sql_date = 12
blr_sql_time = 13
blr_boolean_dtype = 17
blr_int64 = 16
blr_blob2 = 17
# Added in IB 2.1
blr_domain_name = 18
blr_domain_name2 = 19
blr_not_nullable = 20
# Added in IB 2.5
blr_column_name = 21
blr_column_name2 = 22
blr_domain_type_of = 0
blr_domain_full = 1
# Rest of BLR is defined in idb.blr

# Database parameter block stuff

isc_dpb_version1 = 1
isc_dpb_cdd_pathname = 1
isc_dpb_allocation = 2
isc_dpb_journal = 3
isc_dpb_page_size = 4
isc_dpb_num_buffers = 5
isc_dpb_buffer_length = 6
isc_dpb_debug = 7
isc_dpb_garbage_collect = 8
isc_dpb_verify = 9
isc_dpb_sweep = 10
isc_dpb_enable_journal = 11
isc_dpb_disable_journal = 12
isc_dpb_dbkey_scope = 13
isc_dpb_number_of_users = 14
isc_dpb_trace = 15
isc_dpb_no_garbage_collect = 16
isc_dpb_damaged = 17
isc_dpb_license = 18
isc_dpb_sys_user_name = 19
isc_dpb_encrypt_key = 20
isc_dpb_activate_shadow = 21
isc_dpb_sweep_interval = 22
isc_dpb_delete_shadow = 23
isc_dpb_force_write = 24
isc_dpb_begin_log = 25
isc_dpb_quit_log = 26
isc_dpb_no_reserve = 27
isc_dpb_user_name = 28
isc_dpb_password = 29
isc_dpb_password_enc = 30
isc_dpb_sys_user_name_enc = 31
isc_dpb_interp = 32
isc_dpb_online_dump = 33
isc_dpb_old_file_size = 34
isc_dpb_old_num_files = 35
isc_dpb_old_file = 36
isc_dpb_old_file_name = 36
isc_dpb_old_start_page = 37
isc_dpb_old_start_seqno = 38
isc_dpb_old_start_file = 39
isc_dpb_drop_walfile = 40
isc_dpb_old_dump_id = 41
isc_dpb_wal_backup_dir = 42
isc_dpb_wal_chkptlen = 43
isc_dpb_wal_numbufs = 44
isc_dpb_wal_bufsize = 45
isc_dpb_wal_grp_cmt_wait = 46
isc_dpb_lc_messages = 47
isc_dpb_lc_ctype = 48
isc_dpb_cache_manager = 49
isc_dpb_shutdown = 50
isc_dpb_online = 51
isc_dpb_shutdown_delay = 52
isc_dpb_reserved = 53
isc_dpb_overwrite = 54
isc_dpb_sec_attach = 55
isc_dpb_disable_wal = 56
isc_dpb_connect_timeout = 57
isc_dpb_dummy_packet_interval = 58
isc_dpb_gbak_attach = 59
isc_dpb_sql_role_name = 60
isc_dpb_set_page_buffers = 61
isc_dpb_working_directory = 62
isc_dpb_sql_dialect = 63
isc_dpb_set_db_readonly = 64
isc_dpb_set_db_sql_dialect = 65
isc_dpb_gfix_attach = 66
isc_dpb_gstat_attach = 67
isc_dpb_set_db_charset = 68
isc_dpb_gsec_attach = 69
isc_dpb_gbak_ods_version = 68
isc_dpb_gbak_ods_minor_version = 69
isc_dpb_address_path = 70
isc_dpb_set_group_commit = 70
isc_dpb_gbak_validate = 71
isc_dpb_client_interbase_var = 72
isc_dpb_admin_option = 73
isc_dpb_flush_interval = 74
isc_dpb_instance_name = 75
isc_dpb_old_overwrite = 76
isc_dpb_archive_database = 77
isc_dpb_archive_dumps = 80
isc_dpb_archive_journals = 78
isc_dpb_archive_sweep = 79
isc_dpb_archive_recover = 81
isc_dpb_recover_until = 82
isc_dpb_force = 83
isc_dpb_preallocate = 84
isc_dpb_sys_encrypt_password = 85
isc_dpb_eua_user_name = 86
isc_dpb_transaction = 87 # accepts up to int64 type value
isc_dpb_ods_version_major = 88
isc_dpb_old_tablespace_name = 89

# isc_dpb_verify specific flags

isc_dpb_pages = 1
isc_dpb_records = 2
isc_dpb_indices = 4
isc_dpb_transactions = 8
isc_dpb_no_update = 16
isc_dpb_repair = 32
isc_dpb_ignore = 64

# Deprecated definitions maintained for compatibility only

isc_info_db_SQL_dialect = 62
isc_dpb_SQL_dialect = 63
isc_dpb_set_db_SQL_dialect = 65


isc_dpb_archive_recover_dump = 128

# isc_dpb_shutdown specific flags 

isc_dpb_shut_cache = 1
isc_dpb_shut_attachment = 2
isc_dpb_shut_transaction = 4
isc_dpb_shut_force = 8

# Added in IB 2.1
isc_dpb_process_id = 71
isc_dpb_no_db_triggers = 72
isc_dpb_trusted_auth = 73
isc_dpb_process_name = 74
# Added in IB 2.5
isc_dpb_trusted_role = 75
isc_dpb_org_filename = 76
isc_dpb_utf8_filename = 77
isc_dpb_ext_call_depth = 78

# structural codes
isc_info_end = 1
isc_info_truncated = 2
isc_info_error = 3
isc_info_data_not_ready = 4
isc_info_length = 126
isc_info_flag_end = 127

isc_info_req_select_count = 13
isc_info_req_insert_count = 14
isc_info_req_update_count = 15
isc_info_req_delete_count = 16

# These verbs were added in 6.0, primarily to support 64-bit integers

blr_add2 = 163
blr_subtract2 = 164
blr_multiply2 = 165
blr_divide2 = 166
blr_agg_total2 = 167
blr_agg_total_distinct2 = 168
blr_agg_average2 = 169
blr_agg_average_distinct2 = 170
blr_average2 = 171
blr_gen_id2 = 172
blr_set_generator2 = 173

# added for EXECUTE STATEMENT in 10.0
blr_boolean_true = 174
blr_boolean_false = 175
blr_exec_stmt = 179
blr_exec_stmt2 = 180

# Dynamic Data Definition Language operators

# Version number

isc_dyn_version_1 = 1
isc_dyn_eoc = 255

# Operations (may be nested)

isc_dyn_begin = 2
isc_dyn_end = 3
isc_dyn_if = 4
isc_dyn_def_database = 5
isc_dyn_def_global_fld = 6
isc_dyn_def_local_fld = 7
isc_dyn_def_idx = 8
isc_dyn_def_rel = 9
isc_dyn_def_sql_fld = 10
isc_dyn_mod_rel = 11
isc_dyn_def_view = 12
isc_dyn_mod_global_fld = 13
isc_dyn_mod_local_fld = 14
isc_dyn_def_trigger = 15
isc_dyn_mod_view = 16
isc_dyn_def_trigger_msg = 17
isc_dyn_delete_database = 18
isc_dyn_delete_rel = 19
isc_dyn_delete_global_fld = 20
isc_dyn_delete_local_fld = 21
isc_dyn_delete_idx = 22
isc_dyn_delete_trigger = 23
isc_dyn_def_generator = 24
isc_dyn_def_function = 25
isc_dyn_def_filter = 26
isc_dyn_def_function_arg = 27
isc_dyn_mod_trigger_msg = 28
isc_dyn_delete_trigger_msg = 29
isc_dyn_grant = 30
isc_dyn_revoke = 31
isc_dyn_delete_filter = 32
isc_dyn_delete_function = 33
isc_dyn_def_shadow = 34
isc_dyn_delete_shadow = 35
isc_dyn_def_file = 36
isc_dyn_def_primary_key = 37
isc_dyn_def_foreign_key = 38
isc_dyn_mod_database = 39
isc_dyn_def_unique = 40
isc_dyn_mod_filter = 41
isc_dyn_mod_function = 42
isc_dyn_mod_generator = 43
isc_dyn_mod_character_set = 44
isc_dyn_mod_collation = 45
isc_dyn_mod_idx = 102
isc_dyn_mod_trigger = 113
isc_dyn_def_security_class = 120
isc_dyn_mod_security_class = 122
isc_dyn_delete_security_class = 123
isc_dyn_def_parameter = 135
isc_dyn_delete_parameter = 136
isc_dyn_def_dimension = 140
isc_dyn_delete_dimensions = 143
isc_dyn_def_encryption = 150
isc_dyn_mod_encryption = 151
isc_dyn_delete_encryption = 152
isc_dyn_def_subscription = 160
isc_dyn_set_subscription = 161
isc_dyn_def_procedure = 164
isc_dyn_delete_procedure = 165
isc_dyn_delete_subscription = 172
isc_dyn_mod_subscription = 173
isc_dyn_mod_procedure = 175
isc_dyn_def_log_file = 176
isc_dyn_mod_parameter = 177
isc_dyn_def_exception = 181
isc_dyn_mod_exception = 182
isc_dyn_del_exception = 183
isc_dyn_def_filespace = 190
isc_dyn_mod_filespace = 191
isc_dyn_delete_filespace = 192
isc_dyn_sys_encrypt_passwd = 200
isc_dyn_set_password = 201
isc_dyn_def_default_log = 202
isc_dyn_def_journal = 203
isc_dyn_mod_journal = 204
isc_dyn_delete_journal = 205
isc_dyn_def_archive = 206
isc_dyn_mod_archive = 207
isc_dyn_delete_archive = 208
isc_dyn_set_entity_description = 209
isc_dyn_def_sql_role = 211
isc_dyn_mod_sql_role = 212
isc_dyn_del_sql_role = 214
isc_dyn_mod_sql_fld = 216
isc_dyn_delete_generator = 217
isc_dyn_def_user = 225
isc_dyn_mod_user = 226
isc_dyn_delete_user = 227
isc_dyn_mod_constraint = 228

# Last $dyn value assigned

isc_dyn_last_dyn_value = 228

# View specific stuff

isc_dyn_view_blr = 43
isc_dyn_view_source = 44
isc_dyn_view_relation = 45
isc_dyn_view_context = 46
isc_dyn_view_context_name = 47

# Generic attributes

isc_dyn_rel_name = 50
isc_dyn_fld_name  = 51
isc_dyn_new_fld_name = 215
isc_dyn_idx_name = 52
isc_dyn_description = 53
isc_dyn_security_class = 54
isc_dyn_system_flag = 55
isc_dyn_update_flag = 56
isc_dyn_enc_name = 57
isc_dyn_sub_name = 162
isc_dyn_prc_name = 166
isc_dyn_prm_name = 137
isc_dyn_sql_object = 196
isc_dyn_fld_character_set_name = 174
isc_dyn_reserve_space = 195
isc_dyn_restrict_or_cascade = 220

# sub parameters for blr_rows

blr_ties = 0
blr_percent = 1

blr_agg_count = 83
blr_agg_max = 84
blr_agg_min = 85
blr_agg_total = 86
blr_agg_average = 87
blr_parameter3 = 88
blr_run_count = 118
blr_run_max = 89
blr_run_min = 90
blr_run_total = 91
blr_run_average = 92
blr_agg_count2 = 93
blr_agg_count_distinct = 94
blr_agg_total_distinct = 95
blr_agg_average_distinct = 96

blr_function = 100
blr_gen_id = 101
blr_prot_mask = 102
blr_upcase = 103
blr_lock_state = 104
blr_value_if = 105
blr_matching2 = 106
blr_index = 107
blr_ansi_like = 108
blr_bookmark = 109
blr_crack = 110
blr_force_crack = 111
blr_seek = 112
blr_find = 113

blr_continue = 0
blr_forward = 1
blr_backward = 2
blr_bof_forward = 3
blr_eof_backward = 4

blr_lock_relation = 114
blr_lock_record = 115
blr_set_bookmark = 116
blr_get_bookmark = 117
blr_rs_stream = 119
blr_exec_proc = 120
blr_begin_range = 121
blr_end_range = 122
blr_delete_range = 123
blr_procedure = 124
blr_pid = 125
blr_exec_pid = 126
blr_singular = 127
blr_abort = 128
blr_block = 129
blr_error_handler = 130
blr_cast = 131
blr_release_lock = 132
blr_release_locks = 133
blr_start_savepoint = 134
blr_end_savepoint = 135
blr_find_dbkey = 136
blr_range_relation = 137
blr_delete_ranges = 138

blr_plan = 139
blr_merge = 140
blr_join = 141
blr_sequential = 142
blr_navigational = 143
blr_indices = 144
blr_retrieve = 145

blr_relation2 = 146
blr_rid2 = 147
blr_reset_stream = 148
blr_release_bookmark = 149
blr_set_generator = 150
blr_ansi_any = 151
blr_exists = 152
blr_cardinality = 153

blr_record_version = 154 # get tid of record
blr_stall = 155 # fake server stall
blr_seek_no_warn = 156
blr_find_dbkey_version = 157
blr_ansi_all = 158

blr_extract = 159

# added for CHANGE VIEW support in 12.0.1
blr_changed = 181
blr_stored = 182
blr_modified = 183
blr_erased = 184

# Relation specific attributes

isc_dyn_rel_dbkey_length = 61
isc_dyn_rel_store_trig = 62
isc_dyn_rel_modify_trig = 63
isc_dyn_rel_erase_trig = 64
isc_dyn_rel_store_trig_source = 65
isc_dyn_rel_modify_trig_source = 66
isc_dyn_rel_erase_trig_source = 67
isc_dyn_rel_ext_file = 68
isc_dyn_rel_sql_protection = 69
isc_dyn_rel_constraint = 162
isc_dyn_delete_rel_constraint = 163
isc_dyn_rel_sql_scope = 218
isc_dyn_rel_sql_on_commit = 219

# Global field specific attributes

isc_dyn_fld_type = 70
isc_dyn_fld_length = 71
isc_dyn_fld_scale = 72
isc_dyn_fld_sub_type = 73
isc_dyn_fld_segment_length = 74
isc_dyn_fld_query_header = 75
isc_dyn_fld_edit_string = 76
isc_dyn_fld_validation_blr = 77
isc_dyn_fld_validation_source = 78
isc_dyn_fld_computed_blr = 79
isc_dyn_fld_computed_source = 80
isc_dyn_fld_missing_value = 81
isc_dyn_fld_default_value = 82
isc_dyn_fld_query_name = 83
isc_dyn_fld_dimensions = 84
isc_dyn_fld_not_null = 85
isc_dyn_fld_precision = 86
isc_dyn_fld_char_length = 172
isc_dyn_fld_collation = 173
isc_dyn_fld_default_source = 193
isc_dyn_del_default = 197
isc_dyn_del_validation = 198
isc_dyn_single_validation = 199
isc_dyn_fld_encrypt = 200
isc_dyn_fld_decrypt_dflt_value = 201
isc_dyn_fld_decrypt_dflt_source = 202
isc_dyn_fld_character_set = 203

# Local field specific attributes

isc_dyn_fld_derived = 89
isc_dyn_fld_source = 90
isc_dyn_fld_base_fld = 91
isc_dyn_fld_position = 92
isc_dyn_fld_update_flag = 93
isc_dyn_fld_all = 94

# Index specific attributes

isc_dyn_idx_unique = 100
isc_dyn_idx_inactive = 101
isc_dyn_idx_type = 103
isc_dyn_idx_foreign_key = 104
isc_dyn_idx_ref_column = 105
isc_dyn_idx_statistic = 204

# Trigger specific attributes

isc_dyn_trg_type = 110
isc_dyn_trg_blr = 111
isc_dyn_trg_source = 112
isc_dyn_trg_name = 114
isc_dyn_trg_sequence = 115
isc_dyn_trg_inactive = 116
isc_dyn_trg_msg_number = 117
isc_dyn_trg_msg = 118

# Security Class specific attributes

isc_dyn_scl_acl = 121
isc_dyn_grant_user = 130
isc_dyn_grant_proc = 186
isc_dyn_grant_trig = 187
isc_dyn_grant_view = 188
isc_dyn_grant_options = 132
isc_dyn_grant_user_group = 205

# Historical alias for pre V6 applications
blr_inner = 0
blr_left = 1
blr_right = 2
blr_full = 3

blr_gds_code = 0
blr_sql_code = 1
blr_exception = 2
blr_trigger_code = 3
blr_default_code = 4

blr_immediate = 0
blr_deferred = 1

blr_restrict = 0
blr_cascade = 1

blr_version4 = 4
blr_version5 = 5
blr_eoc = 76
blr_end = 255

blr_assignment = 1
blr_begin = 2
blr_dcl_variable = 3
blr_message = 4
blr_erase = 5
blr_fetch = 6
blr_for = 7
blr_if = 8
blr_loop = 9
blr_modify = 10
blr_handler = 11
blr_receive = 12
blr_select = 13
blr_send = 14
blr_store = 15
blr_truncate = 16
blr_label = 17
blr_leave = 18
blr_store2 = 19
blr_post = 20

blr_literal = 21
blr_dbkey = 22
blr_field = 23
blr_fid = 24
blr_parameter = 25
blr_variable = 26
blr_average = 27
blr_count = 28
blr_maximum = 29
blr_minimum = 30
blr_total = 31
blr_add = 34
blr_subtract = 35
blr_multiply = 36
blr_divide = 37
blr_negate = 38
blr_concatenate = 39
blr_substring = 40
blr_parameter2 = 41
blr_from = 42
blr_via = 43
blr_user_name = 44
blr_null = 45

blr_eql = 47
blr_neq = 48
blr_gtr = 49
blr_geq = 50
blr_lss = 51
blr_leq = 52
blr_containing = 53
blr_matching = 54
blr_starting = 55
blr_between = 56
blr_or = 57
blr_and = 58
blr_not = 59
blr_any = 60
blr_missing = 61
blr_unique = 62
blr_like = 63
blr_with = 64

blr_stream = 65
blr_set_index = 66
blr_rse = 67
blr_first = 68
blr_project = 69
blr_sort = 70
blr_boolean = 71
blr_ascending = 72
blr_descending = 73
blr_relation = 74
blr_rid = 75
blr_union = 76
blr_map = 77
blr_group_by = 78
blr_aggregate = 79
blr_join_type = 80
blr_rows = 81
blr_derived_relation = 82

# sub parameters for blr_extract

blr_extract_year = 0
blr_extract_month = 1
blr_extract_day = 2
blr_extract_hour = 3
blr_extract_minute = 4
blr_extract_second = 5
blr_extract_weekday = 6
blr_extract_yearday = 7

blr_current_date = 160
blr_current_timestamp = 161
blr_current_time = 162

# Dimension specific information

isc_dyn_dim_lower = 141
isc_dyn_dim_upper = 142

# File specific attributes

isc_dyn_file_name = 125
isc_dyn_file_start = 126
isc_dyn_file_length = 127
isc_dyn_shadow_number = 128
isc_dyn_shadow_man_auto = 129
isc_dyn_shadow_conditional = 130
isc_dyn_file_prealloc = 131

# Log file specific attributes

isc_dyn_log_file_sequence = 177
isc_dyn_log_file_partitions = 178
isc_dyn_log_file_serial = 179
isc_dyn_log_file_directory = 200
isc_dyn_log_file_raw = 201

# Log specific attributes

isc_dyn_log_check_point_interval = 189
isc_dyn_log_buffer_size = 190
isc_dyn_log_check_point_length = 191
isc_dyn_log_num_of_buffers = 192
isc_dyn_log_timestamp_name = 193

# Function specific attributes

isc_dyn_function_name = 145
isc_dyn_function_type = 146
isc_dyn_func_module_name = 147
isc_dyn_func_entry_point = 148
isc_dyn_func_return_argument = 149
isc_dyn_func_arg_position = 150
isc_dyn_func_mechanism = 151
isc_dyn_filter_in_subtype = 152
isc_dyn_filter_out_subtype = 153


isc_dyn_description2 = 154
isc_dyn_fld_computed_source2 = 155
isc_dyn_fld_edit_string2 = 156
isc_dyn_fld_query_header2 = 157
isc_dyn_fld_validation_source2 = 158
isc_dyn_trg_msg2 = 159
isc_dyn_trg_source2 = 160
isc_dyn_view_source2 = 161
isc_dyn_xcp_msg2 = 184

# Generator specific attributes

isc_dyn_generator_name = 95
isc_dyn_generator_id = 96

# Procedure specific attributes

isc_dyn_prc_inputs = 167
isc_dyn_prc_outputs = 168
isc_dyn_prc_source = 169
isc_dyn_prc_blr = 170
isc_dyn_prc_source2 = 171

# Parameter specific attributes

isc_dyn_prm_number = 138
isc_dyn_prm_type = 139

# Relation specific attributes

isc_dyn_xcp_msg = 185

# Subscription specific attributes

isc_dyn_change_type = 163
isc_dyn_insert = 165
isc_dyn_update = 166
isc_dyn_delete = 167
isc_dyn_change = 168
isc_dyn_sub_active = 169
isc_dyn_sub_inactive = 170
isc_dyn_sub_dest = 171
isc_dyn_sub_rel_counter = 172

# Cascading referential integrity values

isc_dyn_foreign_key_update = 205
isc_dyn_foreign_key_delete = 206
isc_dyn_foreign_key_cascade = 207
isc_dyn_foreign_key_default = 208
isc_dyn_foreign_key_null = 209
isc_dyn_foreign_key_none = 210

# SQL role values

isc_dyn_sql_role_name = 212
isc_dyn_grant_admin_options = 213

# ADMIN OPTION values

isc_dyn_add_admin = 221
isc_dyn_drop_admin = 222
isc_dyn_admin_active = 223
isc_dyn_admin_inactive = 224

# User specific attributes

isc_dyn_user_sys_name = 11
isc_dyn_user_grp_name = 12
isc_dyn_user_uid = 13
isc_dyn_user_gid = 14
isc_dyn_user_password = 15
isc_dyn_user_active = 16
isc_dyn_user_inactive = 17
isc_dyn_user_description = 18
isc_dyn_user_first_name = 19
isc_dyn_user_middle_name = 20
isc_dyn_user_last_name = 21
isc_dyn_user_default_role = 22

# Database specific attributes

isc_dyn_db_page_size = 35
isc_dyn_db_passwd_digest = 37
isc_dyn_db_page_all_checksum = 38
isc_dyn_db_page_enc_checksum = 39
isc_dyn_db_page_off_checksum = 40
isc_dyn_db_page_cache = 41
isc_dyn_db_proc_cache = 42
isc_dyn_db_rel_cache = 43
isc_dyn_db_trig_cache = 44
isc_dyn_db_flush_int = 45
isc_dyn_db_linger_int = 46
isc_dyn_db_reclaim_int = 47
isc_dyn_db_sweep_int = 48
isc_dyn_db_group_commit = 49

# Encryption specific attributes

isc_dyn_enc_default = 50
isc_dyn_enc_cipher = 51
isc_dyn_enc_length = 52
isc_dyn_enc_password = 54
isc_dyn_enc_init_vector = 55
isc_dyn_enc_pad = 56
isc_dyn_encrypt = 57
isc_dyn_decrypt = 58

# Filespace specific attributes

isc_dyn_fsp_active = 70
isc_dyn_fsp_inactive = 71
isc_dyn_fsp_page_size = 72
isc_dyn_fsp_name = 73

# types less than zero are reserved for customer use

isc_blob_untyped = 0

# internal subtypes

isc_blob_text = 1
isc_blob_blr = 2
isc_blob_acl = 3
isc_blob_ranges = 4
isc_blob_summary = 5
isc_blob_format = 6
isc_blob_tra = 7
isc_blob_extfile = 8

# the range 20-30 is reserved for dBASE and Paradox types

isc_blob_formatted_memo = 20
isc_blob_paradox_ole = 21
isc_blob_graphic = 22
isc_blob_dbase_ole = 23
isc_blob_typed_binary = 24

# Actions to pass to the blob filter (ctl_source)

isc_blob_filter_open = 0
isc_blob_filter_get_segment = 1
isc_blob_filter_close = 2
isc_blob_filter_create = 3
isc_blob_filter_put_segment = 4
isc_blob_filter_alloc = 5
isc_blob_filter_free = 6
isc_blob_filter_seek = 7

# DB Info item codes

isc_info_db_id = 4
isc_info_reads = 5
isc_info_writes = 6
isc_info_fetches = 7
isc_info_marks = 8
isc_info_implementation = 11
isc_info_isc_version = 12
isc_info_base_level = 13
isc_info_page_size = 14
isc_info_num_buffers = 15
isc_info_limbo = 16
isc_info_current_memory = 17
isc_info_max_memory = 18
isc_info_window_turns = 19
isc_info_license = 20
isc_info_allocation = 21
isc_info_attachment_id = 22
isc_info_read_seq_count = 23
isc_info_read_idx_count = 24
isc_info_insert_count = 25
isc_info_update_count = 26
isc_info_delete_count = 27
isc_info_backout_count = 28
isc_info_purge_count = 29
isc_info_expunge_count = 30
isc_info_sweep_interval = 31
isc_info_ods_version = 32
isc_info_ods_minor_version = 33
isc_info_no_reserve = 34
isc_info_logfile = 35
isc_info_cur_logfile_name = 36
isc_info_cur_log_part_offset = 37
isc_info_num_wal_buffers = 38
isc_info_wal_buffer_size = 39
isc_info_wal_ckpt_length = 40
isc_info_wal_cur_ckpt_interval = 41
isc_info_wal_prv_ckpt_fname = 42
isc_info_wal_prv_ckpt_poffset = 43
isc_info_wal_recv_ckpt_fname = 44
isc_info_wal_recv_ckpt_poffset = 45
isc_info_wal_grpc_wait_usecs = 47
isc_info_wal_num_io = 48
isc_info_wal_avg_io_size = 49
isc_info_wal_num_commits = 50
isc_info_wal_avg_grpc_size = 51
isc_info_forced_writes = 52
isc_info_user_names = 53
isc_info_page_errors = 54
isc_info_record_errors = 55
isc_info_bpage_errors = 56
isc_info_dpage_errors = 57
isc_info_ipage_errors = 58
isc_info_ppage_errors = 59
isc_info_tpage_errors = 60
isc_info_set_page_buffers = 61
isc_info_db_sql_dialect = 62
isc_info_db_read_only = 63
isc_info_db_size_in_pages = 64
isc_info_svc_get_db_alias = 69

isc_info_version = isc_info_isc_version

# Blob information items
isc_info_blob_num_segments = 4
isc_info_blob_max_segment = 5
isc_info_blob_total_length = 6
isc_info_blob_type = 7

# Transaction information items

isc_info_tra_id = 4
isc_info_tra_oldest_interesting = 5
isc_info_tra_oldest_snapshot = 6
isc_info_tra_oldest_active = 7
isc_info_tra_isolation = 8
isc_info_tra_access = 9
isc_info_tra_lock_timeout = 10

# isc_info_tra_isolation responses
isc_info_tra_consistency = 1
isc_info_tra_concurrency = 2
isc_info_tra_read_committed = 3

# isc_info_tra_read_committed options
isc_info_tra_no_rec_version = 0
isc_info_tra_rec_version = 1

# isc_info_tra_access responses
isc_info_tra_readonly = 0
isc_info_tra_readwrite = 1

# SQL information items
isc_info_sql_select = 4
isc_info_sql_bind = 5
isc_info_sql_num_variables = 6
isc_info_sql_describe_vars = 7
isc_info_sql_describe_end = 8
isc_info_sql_sqlda_seq = 9
isc_info_sql_message_seq = 10
isc_info_sql_type = 11
isc_info_sql_sub_type = 12
isc_info_sql_scale = 13
isc_info_sql_length = 14
isc_info_sql_null_ind = 15
isc_info_sql_field = 16
isc_info_sql_relation = 17
isc_info_sql_owner = 18
isc_info_sql_alias = 19
isc_info_sql_sqlda_start = 20
isc_info_sql_stmt_type = 21
isc_info_sql_get_plan = 22
isc_info_sql_records = 23
isc_info_sql_batch_fetch = 24
isc_info_sql_relation_alias = 25

# SQL information return values
isc_info_sql_stmt_select = 1
isc_info_sql_stmt_insert = 2
isc_info_sql_stmt_update = 3
isc_info_sql_stmt_delete = 4
isc_info_sql_stmt_ddl = 5
isc_info_sql_stmt_get_segment = 6
isc_info_sql_stmt_put_segment = 7
isc_info_sql_stmt_exec_procedure = 8
isc_info_sql_stmt_start_trans = 9
isc_info_sql_stmt_commit = 10
isc_info_sql_stmt_rollback = 11
isc_info_sql_stmt_select_for_upd = 12
isc_info_sql_stmt_set_generator = 13
isc_info_sql_stmt_savepoint = 14

# Transaction parameter block stuff
isc_tpb_version1 = 1
isc_tpb_version3 = 3
isc_tpb_consistency = 1
isc_tpb_concurrency = 2
isc_tpb_shared = 3
isc_tpb_protected = 4
isc_tpb_exclusive = 5
isc_tpb_wait = 6
isc_tpb_nowait = 7
isc_tpb_read = 8
isc_tpb_write = 9
isc_tpb_lock_read = 10
isc_tpb_lock_write = 11
isc_tpb_verb_time = 12
isc_tpb_commit_time = 13
isc_tpb_ignore_limbo = 14
isc_tpb_read_committed = 15
isc_tpb_autocommit = 16
isc_tpb_rec_version = 17
isc_tpb_no_rec_version = 18
isc_tpb_restart_requests = 19
isc_tpb_no_auto_undo = 20
isc_tpb_lock_timeout = 21

# BLOB parameter buffer

isc_bpb_version1          = 1
isc_bpb_source_type       = 1
isc_bpb_target_type       = 2
isc_bpb_type              = 3
isc_bpb_source_interp     = 4
isc_bpb_target_interp     = 5
isc_bpb_filter_parameter  = 6
isc_bpb_target_relation_name = 7
isc_bpb_target_field_name = 8
isc_bpb_target_tablespace_id = 9
# Added in IB 2.1
isc_bpb_storage           = 7

isc_bpb_type_segmented    = 0
isc_bpb_type_stream       = 1

# BLOB codes

isc_segment    = 335544366
isc_segstr_eof = 335544367

# Services API
# Service parameter block stuff
isc_spb_current_version = 2
isc_spb_version = isc_spb_current_version
isc_spb_user_name = isc_dpb_user_name
isc_spb_sys_user_name = isc_dpb_sys_user_name
isc_spb_sys_user_name_enc = isc_dpb_sys_user_name_enc
isc_spb_password = isc_dpb_password
isc_spb_sys_encrypt_password = isc_dpb_sys_encrypt_password
isc_spb_password_enc = isc_dpb_password_enc
isc_spb_command_line = 105
isc_spb_dbname = 106
isc_spb_verbose = 107
isc_spb_options = 108
isc_spb_address_path = 109
# Added in IB 2.1
isc_spb_process_id = 110
isc_spb_trusted_auth = 111
isc_spb_process_name = 112
# Added in IB 2.5
isc_spb_trusted_role = 113

# Service action items
isc_action_svc_backup = 1           # Starts database backup process on the server
isc_action_svc_restore = 2          # Starts database restore process on the server
isc_action_svc_repair = 3           # Starts database repair process on the server
isc_action_svc_add_user = 4         # Adds a new user to the security database
isc_action_svc_delete_user = 5      # Deletes a user record from the security database
isc_action_svc_modify_user = 6      # Modifies a user record in the security database
isc_action_svc_display_user = 7     # Displays a user record from the security database
isc_action_svc_properties = 8       # Sets database properties
isc_action_svc_add_license = 9      # Adds a license to the license file
isc_action_svc_remove_license = 10  # Removes a license from the license file
isc_action_svc_db_stats = 11        # Retrieves database statistics
isc_action_svc_get_ib_log = 12      # Retrieves the InterBase log file from the server

# Actions for working with alias
isc_action_svc_add_db_alias = 13    # Adds a new database alias
isc_action_svc_delete_db_alias = 14 # Deletes an existing database alias
isc_action_svc_display_db_alias = 15 # Displays an existing database alias
isc_action_svc_dump = 16            # Starts database dump process on the server


# Service information items
isc_info_svc_svr_db_info = 50    # Retrieves the number of attachments and databases */
isc_info_svc_get_config = 53     # Retrieves the parameters and values for IB_CONFIG */
isc_info_svc_version = 54        # Retrieves the version of the services manager */
isc_info_svc_server_version = 55 # Retrieves the version of the InterBase server */
isc_info_svc_implementation = 56 # Retrieves the implementation of the InterBase server */
isc_info_svc_capabilities = 57   # Retrieves a bitmask representing the server's capabilities */
isc_info_svc_user_dbpath = 58    # Retrieves the path to the security database in use by the server */
isc_info_svc_get_env = 59        # Retrieves the setting of $InterBase */
isc_info_svc_get_env_lock = 60   # Retrieves the setting of $InterBase_LCK */
isc_info_svc_get_env_msg = 61    # Retrieves the setting of $InterBase_MSG */
isc_info_svc_line = 62           # Retrieves 1 line of service output per call */
isc_info_svc_to_eof = 63         # Retrieves as much of the server output as will fit in the supplied buffer */
isc_info_svc_timeout = 64        # Sets / signifies a timeout value for reading service information */
isc_info_svc_limbo_trans = 66    # Retrieve the limbo transactions */
isc_info_svc_running = 67        # Checks to see if a service is running on an attachment */
isc_info_svc_get_users = 68      # Returns the user information from isc_action_svc_display_users */

# Parameters for isc_action_{add|del|mod|disp)_user
isc_spb_sec_userid = 5
isc_spb_sec_groupid = 6
isc_spb_sec_username = 7
isc_spb_sec_password = 8
isc_spb_sec_groupname = 9
isc_spb_sec_firstname = 10
isc_spb_sec_middlename = 11
isc_spb_sec_lastname = 12
isc_spb_sec_admin = 13

# Parameters for isc_action_svc_backup
isc_spb_bkp_file = 5
isc_spb_bkp_factor = 6
isc_spb_bkp_length = 7
isc_spb_bkp_encrypt_name = 14
isc_spb_bkp_ignore_checksums = 0x01
isc_spb_bkp_ignore_limbo = 0x02
isc_spb_bkp_metadata_only = 0x04
isc_spb_bkp_no_garbage_collect = 0x08
isc_spb_bkp_old_descriptions = 0x10
isc_spb_bkp_non_transportable = 0x20
isc_spb_bkp_convert = 0x40
isc_spb_bkp_expand = 0x80
isc_spb_bkp_no_triggers = 0x8000
isc_spb_bkp_archive_database = 0x010000
isc_spb_bkp_archive_journals = 0x020000

# Parameters for isc_action_svc_dump
isc_spb_dmp_file = 5
isc_spb_dmp_length = 7
isc_spb_dmp_overwrite = 20 # special case; does not require any values
# standalone options for dump operation...
isc_spb_dmp_create = 0x080000

# Parameters for isc_action_{add|delete|display)_db_alias
isc_spb_sec_db_alias_name = 20
isc_spb_sec_db_alias_dbpath = 21

# Parameters for isc_action_svc_properties
isc_spb_prp_page_buffers = 5
isc_spb_prp_sweep_interval = 6
isc_spb_prp_shutdown_db = 7
isc_spb_prp_deny_new_attachments = 9
isc_spb_prp_deny_new_transactions = 10
isc_spb_prp_reserve_space = 11
isc_spb_prp_write_mode = 12
isc_spb_prp_access_mode = 13
isc_spb_prp_set_sql_dialect = 14
isc_spb_prp_activate = 0x0100
isc_spb_prp_db_online = 0x0200
isc_spb_prp_force_shutdown = 41
isc_spb_prp_attachments_shutdown = 42
isc_spb_prp_transactions_shutdown = 43
isc_spb_prp_shutdown_mode = 44
isc_spb_prp_online_mode = 45

# Parameters for isc_spb_prp_shutdown_mode and isc_spb_prp_online_mode
isc_spb_prp_sm_normal = 0
isc_spb_prp_sm_multi = 1
isc_spb_prp_sm_single = 2
isc_spb_prp_sm_full = 3

# Parameters for isc_spb_prp_reserve_space
isc_spb_prp_res_use_full = 35
isc_spb_prp_res = 36

# Parameters for isc_spb_prp_write_mode
isc_spb_prp_wm_async = 37
isc_spb_prp_wm_sync = 38

# Parameters for isc_spb_prp_access_mode
isc_spb_prp_am_readonly = 39
isc_spb_prp_am_readwrite = 40

# Parameters for isc_action_svc_repair
isc_spb_rpr_commit_trans = 15
isc_spb_rpr_rollback_trans = 34
isc_spb_rpr_recover_two_phase = 17
isc_spb_tra_id = 18
isc_spb_single_tra_id = 19
isc_spb_multi_tra_id = 20
isc_spb_tra_state = 21
isc_spb_tra_state_limbo = 22
isc_spb_tra_state_commit = 23
isc_spb_tra_state_rollback = 24
isc_spb_tra_state_unknown = 25
isc_spb_tra_host_site = 26
isc_spb_tra_remote_site = 27
isc_spb_tra_db_path = 28
isc_spb_tra_advise = 29
isc_spb_tra_advise_commit = 30
isc_spb_tra_advise_rollback = 31
isc_spb_tra_advise_unknown = 33

isc_spb_rpr_validate_db = 0x01
isc_spb_rpr_sweep_db = 0x02
isc_spb_rpr_mend_db = 0x04
isc_spb_rpr_list_limbo_trans = 0x08
isc_spb_rpr_check_db = 0x10
isc_spb_rpr_ignore_checksum = 0x20
isc_spb_rpr_kill_shadows = 0x40
isc_spb_rpr_full = 0x80

# Parameters for isc_action_svc_restore
isc_spb_res_buffers = 9
isc_spb_res_page_size = 10
isc_spb_res_length = 11
isc_spb_res_access_mode = 12
isc_spb_res_fix_fss_data = 13
isc_spb_res_fix_fss_metadata = 14
isc_spb_res_decrypt_password = 16
isc_spb_res_archive_recover_until = 23
isc_spb_res_metadata_only = 0x04
isc_spb_res_deactivate_idx = 0x0100
isc_spb_res_no_shadow = 0x0200
isc_spb_res_no_validity = 0x0400
isc_spb_res_one_at_a_time = 0x0800
isc_spb_res_replace = 0x1000
isc_spb_res_create = 0x2000
isc_spb_res_use_all_space = 0x4000
# Archive recover operation
isc_spb_res_archive_recover = 0x040000
# standalone options for tablespace restore
isc_spb_res_create_tablespace = 0x0100000
isc_spb_res_replace_tablespace = 0x0200000

# Parameters for isc_action_svc_backup and
# isc_action_svc_restore

# options needing string values
isc_spb_tablespace_include = 24
isc_spb_tablespace_exclude = 25
isc_spb_tablespace_file = isc_spb_bkp_file

# Parameters for isc_spb_res_access_mode
isc_spb_res_am_readonly = isc_spb_prp_am_readonly
isc_spb_res_am_readwrite = isc_spb_prp_am_readwrite

# Parameters for isc_info_svc_svr_db_info
isc_spb_num_att = 5
isc_spb_num_db = 6

# Parameters for isc_info_svc_db_stats
isc_spb_sts_data_pages = 0x01
isc_spb_sts_db_log = 0x02
isc_spb_sts_hdr_pages = 0x04
isc_spb_sts_idx_pages = 0x08
isc_spb_sts_sys_relations = 0x10
isc_spb_sts_record_versions = 0x20
isc_spb_sts_table = 0x40
isc_spb_sts_nocreation = 0x80

#-------------------

STRING = c_char_p
WSTRING = c_wchar_p

blb_got_eof = 0
blb_got_fragment = -1
blb_got_full_segment = 1
blb_seek_relative = 1
blb_seek_from_tail = 2

# Implementation codes
isc_info_db_impl_rdb_vms = 1
isc_info_db_impl_rdb_eln = 2
isc_info_db_impl_rdb_eln_dev = 3
isc_info_db_impl_rdb_vms_y = 4
isc_info_db_impl_rdb_eln_y = 5
isc_info_db_impl_jri = 6
isc_info_db_impl_jsv = 7
isc_info_db_impl_isc_apl_68K = 25
isc_info_db_impl_isc_vax_ultr = 26
isc_info_db_impl_isc_vms = 27
isc_info_db_impl_isc_sun_68k = 28
isc_info_db_impl_isc_os2 = 29
isc_info_db_impl_isc_sun4 = 30
isc_info_db_impl_isc_hp_ux = 31
isc_info_db_impl_isc_sun_386i = 32
isc_info_db_impl_isc_vms_orcl = 33
isc_info_db_impl_isc_mac_aux = 34
isc_info_db_impl_isc_rt_aix = 35
isc_info_db_impl_isc_mips_ult = 36
isc_info_db_impl_isc_xenix = 37
isc_info_db_impl_isc_dg = 38
isc_info_db_impl_isc_hp_mpexl = 39
isc_info_db_impl_isc_hp_ux68K = 40
isc_info_db_impl_isc_sgi = 41
isc_info_db_impl_isc_sco_unix = 42
isc_info_db_impl_isc_cray = 43
isc_info_db_impl_isc_imp = 44
isc_info_db_impl_isc_delta = 45
isc_info_db_impl_isc_next = 46
isc_info_db_impl_isc_dos = 47

# Info db class
isc_info_db_class_access = 1
isc_info_db_class_y_valve = 2
isc_info_db_class_rem_int = 3
isc_info_db_class_rem_srvr = 4
isc_info_db_class_pipe_int = 7
isc_info_db_class_pipe_srvr = 8
isc_info_db_class_sam_int = 9
isc_info_db_class_sam_srvr = 10
isc_info_db_class_gateway = 11
isc_info_db_class_cache = 12
isc_info_db_class_classic_access = 13
isc_info_db_class_server_access = 14
isc_info_db_class_last_value = (isc_info_db_class_server_access+1)

# Character sets
# 1 byte
CHARSET_NONE = 0
CHARSET_OCTETS = 1
CHARSET_ASCII = 2
CHARSET_DOS437 = 10
CHARSET_DOS850 = 11
CHARSET_DOS865 = 12
CHARSET_DOS860 = 13
CHARSET_DOS863 = 14
CHARSET_NEXT = 19
CHARSET_ISO8859_1 = 21
CHARSET_ISO8859_2 = 22
CHARSET_ISO8859_15 = 39
CHARSET_DOS852 = 45
CHARSET_DOS857 = 46
CHARSET_DOS861 = 47
CHARSET_CYRL = 50
CHARSET_WIN1250 = 51
CHARSET_WIN1251 = 52
CHARSET_WIN1252 = 53
CHARSET_WIN1253 = 54
CHARSET_WIN1254 = 55
CHARSET_KOI8R = 58
# 2 bytes
CHARSET_SJIS_0208 = 5
CHARSET_EUCJ_0208 = 6
CHARSET_UNICODE_BE = 8
CHARSET_KSC_5601 = 44
CHARSET_BIG_5 = 56
CHARSET_GB_2312 = 57
CHARSET_UNICODE_LE = 64
# 3 bytes
CHARSET_UNICODE_FSS = 3
# 4 bytes
CHARSET_UTF_8 = 59

# status codes
isc_segment = 335544366

IB_API_HANDLE = c_uint
if platform.architecture() == ('64bit', 'WindowsPE'):
    intptr_t = c_longlong
    uintptr_t = c_ulonglong
else:
    intptr_t = c_long
    uintptr_t = c_ulong

ISC_STATUS = intptr_t
ISC_STATUS_PTR = POINTER(ISC_STATUS)
ISC_STATUS_ARRAY = ISC_STATUS * 20
IB_SQLSTATE_STRING = c_char * (5 + 1)
ISC_LONG = c_int
ISC_ULONG = c_uint
ISC_SHORT = c_short
ISC_USHORT = c_ushort
ISC_UCHAR = c_ubyte
ISC_SCHAR = c_char
ISC_INT64 = c_longlong
ISC_UINT64 = c_ulonglong
ISC_DATE = c_int
ISC_TIME = c_uint
ISC_BOOLEAN = c_ushort

METADATALENGTH = 68


class ISC_TIMESTAMP(Structure):
    pass
ISC_TIMESTAMP._fields_ = [
    ('timestamp_date', ISC_DATE),
    ('timestamp_time', ISC_TIME),
]


class GDS_QUAD_t(Structure):
    pass
GDS_QUAD_t._fields_ = [
    ('gds_quad_high', ISC_LONG),
    ('gds_quad_low', ISC_ULONG),
]
GDS_QUAD = GDS_QUAD_t
ISC_QUAD = GDS_QUAD_t

isc_att_handle = IB_API_HANDLE
isc_blob_handle = IB_API_HANDLE
isc_db_handle = IB_API_HANDLE
isc_req_handle = IB_API_HANDLE
isc_stmt_handle = IB_API_HANDLE
isc_svc_handle = IB_API_HANDLE
isc_tr_handle = IB_API_HANDLE
isc_resv_handle = ISC_LONG

IB_SHUTDOWN_CALLBACK = CFUNCTYPE(UNCHECKED(c_int), c_int, c_int, POINTER(None))
ISC_CALLBACK = CFUNCTYPE(None)
ISC_PRINT_CALLBACK = CFUNCTYPE(None, c_void_p, c_short, STRING)
ISC_VERSION_CALLBACK = CFUNCTYPE(None, c_void_p, STRING)
ISC_EVENT_CALLBACK = CFUNCTYPE(None, POINTER(ISC_UCHAR), c_ushort, POINTER(ISC_UCHAR))


class ISC_ARRAY_BOUND(Structure):
    pass
ISC_ARRAY_BOUND._fields_ = [
    ('array_bound_lower', c_short),
    ('array_bound_upper', c_short),
]


class ISC_ARRAY_DESC(Structure):
    pass
ISC_ARRAY_DESC._fields_ = [
    ('array_desc_dtype', ISC_UCHAR),
    ('array_desc_scale', ISC_SCHAR),
    ('array_desc_length', c_ushort),
    ('array_desc_field_name', ISC_SCHAR * 32),
    ('array_desc_relation_name', ISC_SCHAR * 32),
    ('array_desc_dimensions', c_short),
    ('array_desc_flags', c_short),
    ('array_desc_bounds', ISC_ARRAY_BOUND * 16),
]

class ISC_ARRAY_DESC_V2(Structure):
    pass
ISC_ARRAY_DESC_V2._fields_ = [
    ('array_desc_version', c_short),
    ('array_desc_dtype', ISC_UCHAR),
    ('array_desc_subtype', ISC_UCHAR),
    ('array_desc_scale', ISC_SCHAR),
    ('array_desc_length', c_ushort),
    ('array_desc_field_name', ISC_SCHAR * METADATALENGTH),
    ('array_desc_relation_name', ISC_SCHAR * METADATALENGTH),
    ('array_desc_dimensions', c_short),
    ('array_desc_flags', c_short),
    ('array_desc_bounds', ISC_ARRAY_BOUND * 16),
]

class ISC_BLOB_DESC(Structure):
    pass
ISC_BLOB_DESC._fields_ = [
    ('blob_desc_subtype', c_short),
    ('blob_desc_charset', c_short),
    ('blob_desc_segment_size', c_short),
    ('blob_desc_field_name', ISC_UCHAR * 32),
    ('blob_desc_relation_name', ISC_UCHAR * 32),
]

class ISC_BLOB_DESC_V2(Structure):
    pass
ISC_BLOB_DESC_V2._fields_ = [
    ('blob_desc_version', c_short),
    ('blob_desc_subtype', c_short),
    ('blob_desc_charset', c_short),
    ('blob_desc_segment_size', c_short),
    ('blob_desc_field_name', ISC_UCHAR * METADATALENGTH),
    ('blob_desc_relation_name', ISC_UCHAR * METADATALENGTH),
]

class isc_blob_ctl(Structure):
    pass
isc_blob_ctl._fields_ = [
    ('ctl_source', CFUNCTYPE(ISC_STATUS)),
    ('ctl_source_handle', POINTER(isc_blob_ctl)),
    ('ctl_to_sub_type', c_short),
    ('ctl_from_sub_type', c_short),
    ('ctl_buffer_length', c_ushort),
    ('ctl_segment_length', c_ushort),
    ('ctl_bpb_length', c_ushort),
    ('ctl_bpb', STRING),
    ('ctl_buffer', POINTER(ISC_UCHAR)),
    ('ctl_max_segment', ISC_LONG),
    ('ctl_number_segments', ISC_LONG),
    ('ctl_total_length', ISC_LONG),
    ('ctl_status', POINTER(ISC_STATUS)),
    ('ctl_data', c_long * 8),
]
ISC_BLOB_CTL = POINTER(isc_blob_ctl)


class bstream(Structure):
    pass
bstream._fields_ = [
    ('bstr_blob', isc_blob_handle),
    ('bstr_buffer', POINTER(c_char)), # STRING
    ('bstr_ptr', POINTER(c_char)), # STRING
    ('bstr_length', c_short),
    ('bstr_cnt', c_short),
    ('bstr_mode', c_char),
]
BSTREAM = bstream
IB_BLOB_STREAM = POINTER(bstream)
# values for enumeration 'blob_lseek_mode'
blob_lseek_mode = c_int  # enum

# values for enumeration 'blob_get_result'
blob_get_result = c_int  # enum


class blobcallback(Structure):
    pass
blobcallback._fields_ = [
    ('blob_get_segment', CFUNCTYPE(c_short, c_void_p, POINTER(ISC_UCHAR),
                                   c_ushort, POINTER(ISC_USHORT))),
    ('blob_handle', c_void_p),
    ('blob_number_segments', ISC_LONG),
    ('blob_max_segment', ISC_LONG),
    ('blob_total_length', ISC_LONG),
    ('blob_put_segment', CFUNCTYPE(None, c_void_p, POINTER(ISC_UCHAR),
                                   c_ushort)),
    ('blob_lseek', CFUNCTYPE(ISC_LONG, c_void_p, c_ushort, c_int)),
]
BLOBCALLBACK = POINTER(blobcallback)


class paramdsc(Structure):
    pass
paramdsc._fields_ = [
    ('dsc_dtype', ISC_UCHAR),
    ('dsc_scale', c_byte),
    ('dsc_length', ISC_USHORT),
    ('dsc_sub_type', c_short),
    ('dsc_flags', ISC_USHORT),
    ('dsc_address', POINTER(ISC_UCHAR)),
]
PARAMDSC = paramdsc


class paramvary(Structure):
    pass
paramvary._fields_ = [
    ('vary_length', ISC_USHORT),
    ('vary_string', ISC_UCHAR * 1),
]
PARAMVARY = paramvary

class ISC_TEB(Structure):
    pass
ISC_TEB._fields_ = [
    ('db_ptr', POINTER(isc_db_handle)),
    ('tpb_len', ISC_SHORT),
    ('tpb_ptr', STRING)
]

class XSQLVAR(Structure):
    pass
XSQLVAR._fields_ = [
    ('sqltype', ISC_SHORT),
    ('sqlscale', ISC_SHORT),
    ('sqlprecision', ISC_SHORT),
    ('sqlsubtype', ISC_SHORT),
    ('sqllen', ISC_SHORT),
    ('sqldata', POINTER(c_char)),  # STRING),
    ('sqlind', POINTER(ISC_SHORT)),
    ('sqlname_length', ISC_SHORT),
    ('sqlname', ISC_SCHAR * 68),
    ('relname_length', ISC_SHORT),
    ('relname', ISC_SCHAR * 68),
    ('ownname_length', ISC_SHORT),
    ('ownname', ISC_SCHAR * 68),
    ('aliasname_length', ISC_SHORT),
    ('aliasname', ISC_SCHAR * 68),
]

class XSQLVAR_V1(Structure):
    pass
XSQLVAR_V1._fields_ = [
    ('sqltype', ISC_SHORT),
    ('sqlscale', ISC_SHORT),
    ('sqlsubtype', ISC_SHORT),
    ('sqllen', ISC_SHORT),
    ('sqldata', POINTER(c_char)),  # STRING),
    ('sqlind', POINTER(ISC_SHORT)),
    ('sqlname_length', ISC_SHORT),
    ('sqlname', ISC_SCHAR * 68),
    ('relname_length', ISC_SHORT),
    ('relname', ISC_SCHAR * 68),
    ('ownname_length', ISC_SHORT),
    ('ownname', ISC_SCHAR * 68),
    ('aliasname_length', ISC_SHORT),
    ('aliasname', ISC_SCHAR * 68),
]

class XSQLDA(Structure):
    pass
XSQLDA._fields_ = [
    ('version', ISC_SHORT),
    ('sqldaid', ISC_SCHAR * 8),
    ('sqldabc', ISC_LONG),
    ('sqln', ISC_SHORT),
    ('sqld', ISC_SHORT),
    ('sqlvar', XSQLVAR * 1),
]

class XSQLDA_VERSION1(Structure):
    pass
XSQLDA_VERSION1._fields_ = [
    ('version', ISC_SHORT),
    ('sqldaid', ISC_SCHAR * 8),
    ('sqldabc', ISC_LONG),
    ('sqln', ISC_SHORT),
    ('sqld', ISC_SHORT),
    ('sqlvar', XSQLVAR_V1 * 1),
]

XSQLDA_PTR = POINTER(XSQLDA)

def portable_int (buf):
    pass

class USER_SEC_DATA(Structure):
    pass
USER_SEC_DATA._fields_ = [
    ('sec_flags', c_short),
    ('uid', c_int),
    ('gid', c_int),
    ('protocol', c_int),
    ('server', STRING),
    ('user_name', STRING),
    ('password', STRING),
    ('group_name', STRING),
    ('first_name', STRING),
    ('middle_name', STRING),
    ('last_name', STRING),
    ('dba_user_name', STRING),
    ('dba_password', STRING),
]

RESULT_VECTOR = ISC_ULONG * 15

# values for enumeration 'db_info_types'
db_info_types = c_int  # enum

# values for enumeration 'info_db_implementations'
info_db_implementations = c_int  # enum

# values for enumeration 'info_db_class'
info_db_class = c_int  # enum

# values for enumeration 'info_db_provider'
info_db_provider = c_int  # enum


class imaxdiv_t(Structure):
    pass
imaxdiv_t._fields_ = [
    ('quot', c_long),
    ('rem', c_long),
]
intmax_t = c_long

int8_t = c_int8
int16_t = c_int16
int32_t = c_int32
int64_t = c_int64
uint8_t = c_uint8
uint16_t = c_uint16
uint32_t = c_uint32
uint64_t = c_uint64
int_least8_t = c_byte
int_least16_t = c_short
int_least32_t = c_int
int_least64_t = c_long
uint_least8_t = c_ubyte
uint_least16_t = c_ushort
uint_least32_t = c_uint
uint_least64_t = c_ulong
int_fast8_t = c_byte
int_fast16_t = c_long
int_fast32_t = c_long
int_fast64_t = c_long
uint_fast8_t = c_ubyte
uint_fast16_t = c_ulong
uint_fast32_t = c_ulong
uint_fast64_t = c_ulong
ptrdiff_t = c_long
size_t = c_ulong
uintmax_t = c_ulong


def get_library_name(embedded) -> str:
    windows_32_lib = "gds32.dll"
    windows_32_elib = "ibtogo.dll"
    windows_64_lib = "ibclient64.dll"
    windows_64_elib = "ibtogo64.dll"
    linux_lib = "gds"
    linux_elib = "ibtogo"
    macos_lib = "libgds"
    macos_elib = "libibtogo"

    is_64_bit = sys.maxsize > 2**32
    if sys.platform == "darwin":
        result = macos_elib if embedded else macos_lib
    elif sys.platform == 'win32' and is_64_bit:
        result = windows_64_elib if embedded else windows_64_lib
    elif sys.platform == 'win32' and not is_64_bit:
        result = windows_32_elib if embedded else windows_32_lib
    elif sys.platform == "linux":
        result = linux_elib if embedded else linux_lib
    else:
        raise Exception("Platform is not supported.")
    return result


class ibclient_API(object):
    """InterBase Client API interface object. Loads InterBase Client Library and exposes
    API functions as member methods. Uses :ref:`ctypes <python:module-ctypes>` for bindings.
    """

    def __find_windows_library_in_registry(self, lib_name):
        """Should return library path found on windows or None"""
        import winreg
        # try find via installed InterBase server

        key_path = r'SOFTWARE\Embarcadero\InterBase\Servers'
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)

        installed_dir = winreg.QueryValueEx(key, 'RootDirectory')
        bin_dir = os.path.join(installed_dir[0], 'bin')

        if lib_name in os.listdir(bin_dir):
            return os.path.join(bin_dir, lib_name)
        else:
            return None

    def __init__(self, ib_library_name=None, embedded=False):
        if ib_library_name is None:
            name = get_library_name(embedded)
            ib_library_name = find_library(name)
            if not ib_library_name and sys.platform == 'win32':
                ib_library_name = self.__find_windows_library_in_registry(name)

            if not ib_library_name:
                raise Exception("Failed to locate the InterBase client library.")

        elif not os.path.exists(ib_library_name):
            raise Exception("InterBase Client Library '%s' not found" % ib_library_name)

        if sys.platform in ('win32', 'cygwin', 'os2', 'os2emx'):
            ib_library = WinDLL(ib_library_name)
        else:
            ib_library = CDLL(ib_library_name)

        self.isc_attach_database = ib_library.isc_attach_database
        self.isc_attach_database.restype = ISC_STATUS
        self.isc_attach_database.argtypes = [POINTER(ISC_STATUS), c_short, STRING,
                                             POINTER(isc_db_handle), c_short, STRING]

        self.isc_array_gen_sdl = ib_library.isc_array_gen_sdl
        self.isc_array_gen_sdl.restype = ISC_STATUS
        self.isc_array_gen_sdl.argtypes = [POINTER(ISC_STATUS), POINTER(ISC_ARRAY_DESC),
                                           POINTER(ISC_SHORT), POINTER(ISC_UCHAR),
                                           POINTER(ISC_SHORT)]

        self.isc_array_gen_sdl2 = ib_library.isc_array_gen_sdl2
        self.isc_array_gen_sdl2.restype = ISC_STATUS
        self.isc_array_gen_sdl2.argtypes = [POINTER(ISC_STATUS), POINTER(ISC_ARRAY_DESC_V2),
                                           POINTER(ISC_SHORT), POINTER(ISC_UCHAR),
                                           POINTER(ISC_SHORT)]

        self.isc_array_get_slice = ib_library.isc_array_get_slice
        self.isc_array_get_slice.restype = ISC_STATUS
        self.isc_array_get_slice.argtypes = [POINTER(ISC_STATUS), POINTER(isc_db_handle),
                                             POINTER(isc_tr_handle), POINTER(ISC_QUAD),
                                             POINTER(ISC_ARRAY_DESC), c_void_p,
                                             POINTER(ISC_LONG)]
        
        self.isc_array_get_slice2 = ib_library.isc_array_get_slice2
        self.isc_array_get_slice2.restype = ISC_STATUS
        self.isc_array_get_slice2.argtypes = [POINTER(ISC_STATUS), POINTER(isc_db_handle),
                                             POINTER(isc_tr_handle), POINTER(ISC_QUAD),
                                             POINTER(ISC_ARRAY_DESC_V2), c_void_p,
                                             POINTER(ISC_LONG)]

        self.isc_array_lookup_bounds = ib_library.isc_array_lookup_bounds
        self.isc_array_lookup_bounds.restype = ISC_STATUS
        self.isc_array_lookup_bounds.argtypes = [POINTER(ISC_STATUS),
                                                 POINTER(isc_db_handle),
                                                 POINTER(isc_tr_handle), STRING, STRING,
                                                 POINTER(ISC_ARRAY_DESC)]

        self.isc_array_lookup_bounds2 = ib_library.isc_array_lookup_bounds2
        self.isc_array_lookup_bounds2.restype = ISC_STATUS
        self.isc_array_lookup_bounds2.argtypes = [POINTER(ISC_STATUS),
                                                 POINTER(isc_db_handle),
                                                 POINTER(isc_tr_handle), STRING, STRING,
                                                 POINTER(ISC_ARRAY_DESC_V2)]

        self.isc_array_lookup_desc = ib_library.isc_array_lookup_desc
        self.isc_array_lookup_desc.restype = ISC_STATUS
        self.isc_array_lookup_desc.argtypes = [POINTER(ISC_STATUS),
                                               POINTER(isc_db_handle),
                                               POINTER(isc_tr_handle), STRING, STRING,
                                               POINTER(ISC_ARRAY_DESC)]

        self.isc_array_lookup_desc2 = ib_library.isc_array_lookup_desc2
        self.isc_array_lookup_desc2.restype = ISC_STATUS
        self.isc_array_lookup_desc2.argtypes = [POINTER(ISC_STATUS),
                                               POINTER(isc_db_handle),
                                               POINTER(isc_tr_handle), STRING, STRING,
                                               POINTER(ISC_ARRAY_DESC_V2)]

        self.isc_array_set_desc = ib_library.isc_array_set_desc
        self.isc_array_set_desc.restype = ISC_STATUS
        self.isc_array_set_desc.argtypes = [POINTER(ISC_STATUS), STRING, STRING,
                                            POINTER(c_short), POINTER(c_short),
                                            POINTER(c_short), POINTER(ISC_ARRAY_DESC)]

        self.isc_array_set_desc2 = ib_library.isc_array_set_desc2
        self.isc_array_set_desc2.restype = ISC_STATUS
        self.isc_array_set_desc2.argtypes = [POINTER(ISC_STATUS), STRING, STRING,
                                            POINTER(c_short), POINTER(c_short),
                                            POINTER(c_short), POINTER(ISC_ARRAY_DESC_V2)]

        self.isc_array_put_slice = ib_library.isc_array_put_slice
        self.isc_array_put_slice.restype = ISC_STATUS
        self.isc_array_put_slice.argtypes = [POINTER(ISC_STATUS), POINTER(isc_db_handle),
                                             POINTER(isc_tr_handle), POINTER(ISC_QUAD),
                                             POINTER(ISC_ARRAY_DESC), c_void_p,
                                             POINTER(ISC_LONG)]

        self.isc_array_put_slice2 = ib_library.isc_array_put_slice2
        self.isc_array_put_slice2.restype = ISC_STATUS
        self.isc_array_put_slice2.argtypes = [POINTER(ISC_STATUS), POINTER(isc_db_handle),
                                             POINTER(isc_tr_handle), POINTER(ISC_QUAD),
                                             POINTER(ISC_ARRAY_DESC_V2), c_void_p,
                                             POINTER(ISC_LONG)]

        self.isc_blob_default_desc = ib_library.isc_blob_default_desc
        self.isc_blob_default_desc.restype = None
        self.isc_blob_default_desc.argtypes = [POINTER(ISC_BLOB_DESC), POINTER(ISC_UCHAR),
                                               POINTER(ISC_UCHAR)]

        self.isc_blob_default_desc2 = ib_library.isc_blob_default_desc2
        self.isc_blob_default_desc2.restype = None
        self.isc_blob_default_desc2.argtypes = [POINTER(ISC_BLOB_DESC_V2), POINTER(ISC_UCHAR),
                                               POINTER(ISC_UCHAR)]

        self.isc_blob_gen_bpb = ib_library.isc_blob_gen_bpb
        self.isc_blob_gen_bpb.restype = ISC_STATUS
        self.isc_blob_gen_bpb.argtypes = [POINTER(ISC_STATUS), POINTER(ISC_BLOB_DESC),
                                          POINTER(ISC_BLOB_DESC), c_ushort,
                                          POINTER(ISC_UCHAR), POINTER(c_ushort)]

        self.isc_blob_gen_bpb2 = ib_library.isc_blob_gen_bpb2
        self.isc_blob_gen_bpb2.restype = ISC_STATUS
        self.isc_blob_gen_bpb2.argtypes = [POINTER(ISC_STATUS), POINTER(ISC_BLOB_DESC_V2),
                                          POINTER(ISC_BLOB_DESC_V2), c_ushort,
                                          POINTER(ISC_UCHAR), POINTER(c_ushort)]

        self.isc_blob_info = ib_library.isc_blob_info
        self.isc_blob_info.restype = ISC_STATUS
        self.isc_blob_info.argtypes = [POINTER(ISC_STATUS), POINTER(isc_blob_handle),
                                       c_short, STRING, c_short, POINTER(c_char)]

        self.isc_blob_lookup_desc = ib_library.isc_blob_lookup_desc
        self.isc_blob_lookup_desc.restype = ISC_STATUS
        self.isc_blob_lookup_desc.argtypes = [POINTER(ISC_STATUS), POINTER(isc_db_handle),
                                              POINTER(isc_tr_handle), POINTER(ISC_UCHAR),
                                              POINTER(ISC_UCHAR), POINTER(ISC_BLOB_DESC),
                                              POINTER(ISC_UCHAR)]

        self.isc_blob_lookup_desc2 = ib_library.isc_blob_lookup_desc2
        self.isc_blob_lookup_desc2.restype = ISC_STATUS
        self.isc_blob_lookup_desc2.argtypes = [POINTER(ISC_STATUS), POINTER(isc_db_handle),
                                              POINTER(isc_tr_handle), POINTER(ISC_UCHAR),
                                              POINTER(ISC_UCHAR), POINTER(ISC_BLOB_DESC_V2),
                                              POINTER(ISC_UCHAR)]

        self.isc_blob_set_desc = ib_library.isc_blob_set_desc
        self.isc_blob_set_desc.restype = ISC_STATUS
        self.isc_blob_set_desc.argtypes = [POINTER(ISC_STATUS), POINTER(ISC_UCHAR),
                                           POINTER(ISC_UCHAR), c_short, c_short, c_short,
                                           POINTER(ISC_BLOB_DESC)]

        self.isc_blob_set_desc2 = ib_library.isc_blob_set_desc2
        self.isc_blob_set_desc2.restype = ISC_STATUS
        self.isc_blob_set_desc2.argtypes = [POINTER(ISC_STATUS), POINTER(ISC_UCHAR),
                                           POINTER(ISC_UCHAR), c_short, c_short, c_short,
                                           POINTER(ISC_BLOB_DESC_V2)]

        self.isc_cancel_blob = ib_library.isc_cancel_blob
        self.isc_cancel_blob.restype = ISC_STATUS
        self.isc_cancel_blob.argtypes = [POINTER(ISC_STATUS), POINTER(isc_blob_handle)]

        self.isc_cancel_events = ib_library.isc_cancel_events
        self.isc_cancel_events.restype = ISC_STATUS
        self.isc_cancel_events.argtypes = [POINTER(ISC_STATUS), POINTER(isc_db_handle),
                                           POINTER(ISC_LONG)]

        self.isc_close_blob = ib_library.isc_close_blob
        self.isc_close_blob.restype = ISC_STATUS
        self.isc_close_blob.argtypes = [POINTER(ISC_STATUS), POINTER(isc_blob_handle)]

        self.isc_commit_retaining = ib_library.isc_commit_retaining
        self.isc_commit_retaining.restype = ISC_STATUS
        self.isc_commit_retaining.argtypes = [POINTER(ISC_STATUS), POINTER(isc_tr_handle)]

        self.isc_commit_transaction = ib_library.isc_commit_transaction
        self.isc_commit_transaction.restype = ISC_STATUS
        self.isc_commit_transaction.argtypes = [POINTER(ISC_STATUS), POINTER(isc_tr_handle)]

        self.isc_create_blob = ib_library.isc_create_blob
        self.isc_create_blob.restype = ISC_STATUS
        self.isc_create_blob.argtypes = [POINTER(ISC_STATUS), POINTER(isc_db_handle),
                                         POINTER(isc_tr_handle), POINTER(isc_blob_handle),
                                         POINTER(ISC_QUAD)]

        self.isc_create_blob2 = ib_library.isc_create_blob2
        self.isc_create_blob2.restype = ISC_STATUS
        self.isc_create_blob2.argtypes = [POINTER(ISC_STATUS), POINTER(isc_db_handle),
                                          POINTER(isc_tr_handle), POINTER(isc_blob_handle),
                                          POINTER(ISC_QUAD), c_short, STRING]

        self.isc_create_database = ib_library.isc_create_database
        self.isc_create_database.restype = ISC_STATUS
        self.isc_create_database.argtypes = [POINTER(ISC_STATUS), c_short, STRING,
                                             POINTER(isc_db_handle), c_short, STRING,
                                             c_short]

        self.isc_database_info = ib_library.isc_database_info
        self.isc_database_info.restype = ISC_STATUS
        self.isc_database_info.argtypes = [POINTER(ISC_STATUS), POINTER(isc_db_handle),
                                           c_short, STRING, c_short, STRING]

        self.isc_decode_date = ib_library.isc_decode_date
        self.isc_decode_date.restype = None
        self.isc_decode_date.argtypes = [POINTER(ISC_QUAD), c_void_p]

        self.isc_decode_sql_date = ib_library.isc_decode_sql_date
        self.isc_decode_sql_date.restype = None
        self.isc_decode_sql_date.argtypes = [POINTER(ISC_DATE), c_void_p]

        self.isc_decode_sql_time = ib_library.isc_decode_sql_time
        self.isc_decode_sql_time.restype = None
        self.isc_decode_sql_time.argtypes = [POINTER(ISC_TIME), c_void_p]

        self.isc_decode_timestamp = ib_library.isc_decode_timestamp
        self.isc_decode_timestamp.restype = None
        self.isc_decode_timestamp.argtypes = [POINTER(ISC_TIMESTAMP), c_void_p]

        self.isc_detach_database = ib_library.isc_detach_database
        self.isc_detach_database.restype = ISC_STATUS
        self.isc_detach_database.argtypes = [POINTER(ISC_STATUS), POINTER(isc_db_handle)]

        self.isc_drop_database = ib_library.isc_drop_database
        self.isc_drop_database.restype = ISC_STATUS
        self.isc_drop_database.argtypes = [POINTER(ISC_STATUS), POINTER(isc_db_handle)]

        self.isc_dsql_allocate_statement = ib_library.isc_dsql_allocate_statement
        self.isc_dsql_allocate_statement.restype = ISC_STATUS
        self.isc_dsql_allocate_statement.argtypes = [POINTER(ISC_STATUS),
                                                     POINTER(isc_db_handle),
                                                     POINTER(isc_stmt_handle)]

        self.isc_dsql_alloc_statement2 = ib_library.isc_dsql_alloc_statement2
        self.isc_dsql_alloc_statement2.restype = ISC_STATUS
        self.isc_dsql_alloc_statement2.argtypes = [POINTER(ISC_STATUS),
                                                   POINTER(isc_db_handle),
                                                   POINTER(isc_stmt_handle)]

        self.isc_dsql_describe = ib_library.isc_dsql_describe
        self.isc_dsql_describe.restype = ISC_STATUS
        self.isc_dsql_describe.argtypes = [POINTER(ISC_STATUS),
                                           POINTER(isc_stmt_handle),
                                           c_ushort, POINTER(XSQLDA)]

        self.isc_dsql_describe_bind = ib_library.isc_dsql_describe_bind
        self.isc_dsql_describe_bind.restype = ISC_STATUS
        self.isc_dsql_describe_bind.argtypes = [POINTER(ISC_STATUS),
                                                POINTER(isc_stmt_handle),
                                                c_ushort, POINTER(XSQLDA)]

        self.isc_dsql_exec_immed2 = ib_library.isc_dsql_exec_immed2
        self.isc_dsql_exec_immed2.restype = ISC_STATUS
        self.isc_dsql_exec_immed2.argtypes = [POINTER(ISC_STATUS), POINTER(isc_db_handle),
                                              POINTER(isc_tr_handle), c_ushort, STRING,
                                              c_ushort, POINTER(XSQLDA), POINTER(XSQLDA)]

        self.isc_dsql_execute = ib_library.isc_dsql_execute
        self.isc_dsql_execute.restype = ISC_STATUS
        self.isc_dsql_execute.argtypes = [POINTER(ISC_STATUS), POINTER(isc_tr_handle),
                                          POINTER(isc_stmt_handle), c_ushort,
                                          POINTER(XSQLDA)]

        self.isc_dsql_execute2 = ib_library.isc_dsql_execute2
        self.isc_dsql_execute2.restype = ISC_STATUS
        self.isc_dsql_execute2.argtypes = [POINTER(ISC_STATUS), POINTER(isc_tr_handle),
                                           POINTER(isc_stmt_handle), c_ushort,
                                           POINTER(XSQLDA), POINTER(XSQLDA)]

        self.isc_dsql_execute_immediate = ib_library.isc_dsql_execute_immediate
        self.isc_dsql_execute_immediate.restype = ISC_STATUS
        self.isc_dsql_execute_immediate.argtypes = [POINTER(ISC_STATUS),
                                                    POINTER(isc_db_handle),
                                                    POINTER(isc_tr_handle),
                                                    c_ushort, STRING, c_ushort,
                                                    POINTER(XSQLDA)]

        self.isc_dsql_fetch = ib_library.isc_dsql_fetch
        self.isc_dsql_fetch.restype = ISC_STATUS
        self.isc_dsql_fetch.argtypes = [POINTER(ISC_STATUS), POINTER(isc_stmt_handle),
                                        c_ushort, POINTER(XSQLDA)]

        self.isc_dsql_finish = ib_library.isc_dsql_finish
        self.isc_dsql_finish.restype = ISC_STATUS
        self.isc_dsql_finish.argtypes = [POINTER(isc_db_handle)]

        self.isc_dsql_free_statement = ib_library.isc_dsql_free_statement
        self.isc_dsql_free_statement.restype = ISC_STATUS
        self.isc_dsql_free_statement.argtypes = [POINTER(ISC_STATUS),
                                                 POINTER(isc_stmt_handle), c_ushort]

        self.isc_dsql_insert = ib_library.isc_dsql_insert
        self.isc_dsql_insert.restype = ISC_STATUS
        self.isc_dsql_insert.argtypes = [POINTER(ISC_STATUS), POINTER(isc_stmt_handle),
                                         c_ushort, POINTER(XSQLDA)]

        self.isc_dsql_prepare = ib_library.isc_dsql_prepare
        self.isc_dsql_prepare.restype = ISC_STATUS
        self.isc_dsql_prepare.argtypes = [POINTER(ISC_STATUS), POINTER(isc_tr_handle),
                                          POINTER(isc_stmt_handle), c_ushort, STRING,
                                          c_ushort, POINTER(XSQLDA)]

        self.isc_dsql_set_cursor_name = ib_library.isc_dsql_set_cursor_name
        self.isc_dsql_set_cursor_name.restype = ISC_STATUS
        self.isc_dsql_set_cursor_name.argtypes = [POINTER(ISC_STATUS),
                                                  POINTER(isc_stmt_handle), STRING,
                                                  c_ushort]

        self.isc_dsql_sql_info = ib_library.isc_dsql_sql_info
        self.isc_dsql_sql_info.restype = ISC_STATUS
        self.isc_dsql_sql_info.argtypes = [POINTER(ISC_STATUS),
                                           POINTER(isc_stmt_handle),
                                           c_short, STRING, c_short, STRING]

        self.isc_encode_date = ib_library.isc_encode_date
        self.isc_encode_date.restype = None
        self.isc_encode_date.argtypes = [c_void_p, POINTER(ISC_QUAD)]

        self.isc_encode_sql_date = ib_library.isc_encode_sql_date
        self.isc_encode_sql_date.restype = None
        self.isc_encode_sql_date.argtypes = [c_void_p, POINTER(ISC_DATE)]

        self.isc_encode_sql_time = ib_library.isc_encode_sql_time
        self.isc_encode_sql_time.restype = None
        self.isc_encode_sql_time.argtypes = [c_void_p, POINTER(ISC_TIME)]

        self.isc_encode_timestamp = ib_library.isc_encode_timestamp
        self.isc_encode_timestamp.restype = None
        self.isc_encode_timestamp.argtypes = [c_void_p, POINTER(ISC_TIMESTAMP)]

        self.isc_event_counts = ib_library.isc_event_counts
        self.isc_event_counts.restype = None
        self.isc_event_counts.argtypes = [POINTER(RESULT_VECTOR), c_short, POINTER(ISC_UCHAR),
                                     POINTER(ISC_UCHAR)]

        self.isc_expand_dpb = ib_library.isc_expand_dpb
        self.isc_expand_dpb.restype = None
        self.isc_expand_dpb.argtypes = [POINTER(STRING), POINTER(c_short)]

        self.isc_modify_dpb = ib_library.isc_modify_dpb
        self.isc_modify_dpb.restype = c_int
        self.isc_modify_dpb.argtypes = [POINTER(STRING), POINTER(c_short), c_ushort,
                                        STRING, c_short]

        self.isc_free = ib_library.isc_free
        self.isc_free.restype = ISC_LONG
        self.isc_free.argtypes = [STRING]

        self.isc_get_segment = ib_library.isc_get_segment
        self.isc_get_segment.restype = ISC_STATUS
        self.isc_get_segment.argtypes = [POINTER(ISC_STATUS), POINTER(isc_blob_handle),
                                         POINTER(c_ushort), c_ushort, c_void_p]
        #self.isc_get_segment.argtypes = [POINTER(ISC_STATUS), POINTER(isc_blob_handle),
        #                            POINTER(c_ushort), c_ushort, POINTER(c_char)]

        self.isc_get_slice = ib_library.isc_get_slice
        self.isc_get_slice.restype = ISC_STATUS
        self.isc_get_slice.argtypes = [POINTER(ISC_STATUS), POINTER(isc_db_handle),
                                       POINTER(isc_tr_handle), POINTER(ISC_QUAD),
                                       c_short,
                                       STRING, c_short, POINTER(ISC_LONG), ISC_LONG,
                                       c_void_p, POINTER(ISC_LONG)]

        self.isc_interprete = ib_library.isc_interprete
        self.isc_interprete.restype = ISC_LONG
        self.isc_interprete.argtypes = [STRING, POINTER(POINTER(ISC_STATUS))]

       #self.ib_interpret = ib_library.ib_interpret
       #self.ib_interpret.restype = ISC_LONG
       #self.ib_interpret.argtypes = [STRING, c_uint, POINTER(POINTER(ISC_STATUS))]

        self.isc_open_blob = ib_library.isc_open_blob
        self.isc_open_blob.restype = ISC_STATUS
        self.isc_open_blob.argtypes = [POINTER(ISC_STATUS), POINTER(isc_db_handle),
                                       POINTER(isc_tr_handle), POINTER(isc_blob_handle),
                                       POINTER(ISC_QUAD)]

        self.isc_open_blob2 = ib_library.isc_open_blob2
        self.isc_open_blob2.restype = ISC_STATUS
        self.isc_open_blob2.argtypes = [POINTER(ISC_STATUS), POINTER(isc_db_handle),
                                        POINTER(isc_tr_handle), POINTER(isc_blob_handle),
                                        POINTER(ISC_QUAD), ISC_USHORT, STRING] # POINTER(ISC_UCHAR)

        self.isc_prepare_transaction2 = ib_library.isc_prepare_transaction2
        self.isc_prepare_transaction2.restype = ISC_STATUS
        self.isc_prepare_transaction2.argtypes = [POINTER(ISC_STATUS),
                                                  POINTER(isc_tr_handle), ISC_USHORT,
                                                  POINTER(ISC_UCHAR)]

        self.isc_print_sqlerror = ib_library.isc_print_sqlerror
        self.isc_print_sqlerror.restype = None
        self.isc_print_sqlerror.argtypes = [ISC_SHORT, POINTER(ISC_STATUS)]

        self.isc_print_status = ib_library.isc_print_status
        self.isc_print_status.restype = ISC_STATUS
        self.isc_print_status.argtypes = [POINTER(ISC_STATUS)]

        self.isc_put_segment = ib_library.isc_put_segment
        self.isc_put_segment.restype = ISC_STATUS
        self.isc_put_segment.argtypes = [POINTER(ISC_STATUS), POINTER(isc_blob_handle),
                                         c_ushort, c_void_p]
        #self.isc_put_segment.argtypes = [POINTER(ISC_STATUS), POINTER(isc_blob_handle),
        #                            c_ushort, STRING]

        self.isc_put_slice = ib_library.isc_put_slice
        self.isc_put_slice.restype = ISC_STATUS
        self.isc_put_slice.argtypes = [POINTER(ISC_STATUS), POINTER(isc_db_handle),
                                       POINTER(isc_tr_handle), POINTER(ISC_QUAD),
                                       c_short,
                                       STRING, c_short, POINTER(ISC_LONG), ISC_LONG,
                                       c_void_p]

        self.isc_que_events = ib_library.isc_que_events
        self.isc_que_events.restype = ISC_STATUS
        self.isc_que_events.argtypes = [POINTER(ISC_STATUS), POINTER(isc_db_handle),
                                        POINTER(ISC_LONG), c_short, POINTER(ISC_UCHAR),
                                        ISC_EVENT_CALLBACK, POINTER(ISC_UCHAR)]

        self.isc_rollback_retaining = ib_library.isc_rollback_retaining
        self.isc_rollback_retaining.restype = ISC_STATUS
        self.isc_rollback_retaining.argtypes = [POINTER(ISC_STATUS), POINTER(isc_tr_handle)]

        self.isc_rollback_savepoint = ib_library.isc_rollback_savepoint
        self.isc_rollback_savepoint.restype = ISC_STATUS
        self.isc_rollback_savepoint.argtypes = [
            POINTER(ISC_STATUS),
            POINTER(isc_db_handle),
            STRING,
            c_short,
        ]

        self.isc_start_savepoint = ib_library.isc_start_savepoint
        self.isc_start_savepoint.restype = ISC_STATUS
        self.isc_start_savepoint.argtypes = [
            POINTER(ISC_STATUS),
            POINTER(isc_db_handle),
            STRING,
        ]

        self.isc_release_savepoint = ib_library.isc_release_savepoint
        self.isc_release_savepoint.restype = ISC_STATUS
        self.isc_release_savepoint.argtypes = [
            POINTER(ISC_STATUS),
            POINTER(isc_db_handle),
            STRING,
        ]

        self.isc_rollback_transaction = ib_library.isc_rollback_transaction
        self.isc_rollback_transaction.restype = ISC_STATUS
        self.isc_rollback_transaction.argtypes = [POINTER(ISC_STATUS),
                                                  POINTER(isc_tr_handle)]

        self.isc_start_multiple = ib_library.isc_start_multiple
        self.isc_start_multiple.restype = ISC_STATUS
        self.isc_start_multiple.argtypes = [POINTER(ISC_STATUS), POINTER(isc_tr_handle),
                                            c_short, c_void_p]

        if sys.platform in ['win32', 'cygwin', 'os2', 'os2emx']:
            P_isc_start_transaction = CFUNCTYPE(ISC_STATUS, POINTER(ISC_STATUS),
                                                POINTER(isc_tr_handle), c_short,
                                                POINTER(isc_db_handle), c_short,
                                                STRING)
            self.isc_start_transaction = P_isc_start_transaction(('isc_start_transaction',
                                                             ib_library))
        else:
            self.isc_start_transaction = ib_library.isc_start_transaction
            self.isc_start_transaction.restype = ISC_STATUS
            self.isc_start_transaction.argtypes = [POINTER(ISC_STATUS),
                                                   POINTER(isc_tr_handle), c_short,
                                                   POINTER(isc_db_handle), c_short, STRING]

        self.isc_sqlcode = ib_library.isc_sqlcode
        self.isc_sqlcode.restype = ISC_LONG
        self.isc_sqlcode.argtypes = [POINTER(ISC_STATUS)]

        self.isc_sql_interprete = ib_library.isc_sql_interprete
        self.isc_sql_interprete.restype = None
        self.isc_sql_interprete.argtypes = [c_short, STRING, c_short]

        self.isc_transaction_info = ib_library.isc_transaction_info
        self.isc_transaction_info.restype = ISC_STATUS
        self.isc_transaction_info.argtypes = [POINTER(ISC_STATUS), POINTER(isc_tr_handle),
                                              c_short, STRING, c_short, STRING]

        self.isc_transact_request = ib_library.isc_transact_request
        self.isc_transact_request.restype = ISC_STATUS
        self.isc_transact_request.argtypes = [POINTER(ISC_STATUS), POINTER(isc_db_handle),
                                              POINTER(isc_tr_handle), c_ushort, STRING,
                                              c_ushort, STRING, c_ushort, STRING]

        self.isc_vax_integer = ib_library.isc_vax_integer
        self.isc_vax_integer.restype = ISC_LONG
        self.isc_vax_integer.argtypes = [STRING, c_short]

        self.isc_portable_integer = ib_library.isc_portable_integer
        self.isc_portable_integer.restype = ISC_INT64
        self.isc_portable_integer.argtypes = [POINTER(ISC_UCHAR), c_short]

        self.isc_add_user = ib_library.isc_add_user
        self.isc_add_user.restype = ISC_STATUS
        self.isc_add_user.argtypes = [POINTER(ISC_STATUS), POINTER(USER_SEC_DATA)]

        self.isc_delete_user = ib_library.isc_delete_user
        self.isc_delete_user.restype = ISC_STATUS
        self.isc_delete_user.argtypes = [POINTER(ISC_STATUS), POINTER(USER_SEC_DATA)]

        self.isc_modify_user = ib_library.isc_modify_user
        self.isc_modify_user.restype = ISC_STATUS
        self.isc_modify_user.argtypes = [POINTER(ISC_STATUS), POINTER(USER_SEC_DATA)]

        self.isc_compile_request = ib_library.isc_compile_request
        self.isc_compile_request.restype = ISC_STATUS
        self.isc_compile_request.argtypes = [POINTER(ISC_STATUS), POINTER(isc_db_handle),
                                             POINTER(isc_req_handle), c_short, STRING]

        self.isc_compile_request2 = ib_library.isc_compile_request2
        self.isc_compile_request2.restype = ISC_STATUS
        self.isc_compile_request2.argtypes = [POINTER(ISC_STATUS), POINTER(isc_db_handle),
                                              POINTER(isc_req_handle), c_short, STRING]

        self.isc_ddl = ib_library.isc_ddl
        self.isc_ddl.restype = ISC_STATUS
        self.isc_ddl.argtypes = [POINTER(ISC_STATUS), POINTER(isc_db_handle),
                                 POINTER(isc_tr_handle), c_short, STRING]

        self.isc_prepare_transaction = ib_library.isc_prepare_transaction
        self.isc_prepare_transaction.restype = ISC_STATUS
        self.isc_prepare_transaction.argtypes = [POINTER(ISC_STATUS),
                                                 POINTER(isc_tr_handle)]

        self.isc_receive = ib_library.isc_receive
        self.isc_receive.restype = ISC_STATUS
        self.isc_receive.argtypes = [POINTER(ISC_STATUS), POINTER(isc_req_handle),
                                     c_short, c_short, c_void_p, c_short]

        self.isc_reconnect_transaction = ib_library.isc_reconnect_transaction
        self.isc_reconnect_transaction.restype = ISC_STATUS
        self.isc_reconnect_transaction.argtypes = [POINTER(ISC_STATUS),
                                                   POINTER(isc_db_handle),
                                                   POINTER(isc_tr_handle), c_short, STRING]

        self.isc_release_request = ib_library.isc_release_request
        self.isc_release_request.restype = ISC_STATUS
        self.isc_release_request.argtypes = [POINTER(ISC_STATUS), POINTER(isc_req_handle)]

        self.isc_request_info = ib_library.isc_request_info
        self.isc_request_info.restype = ISC_STATUS
        self.isc_request_info.argtypes = [POINTER(ISC_STATUS), POINTER(isc_req_handle),
                                          c_short, c_short, STRING, c_short, STRING]

        self.isc_seek_blob = ib_library.isc_seek_blob
        self.isc_seek_blob.restype = ISC_STATUS
        self.isc_seek_blob.argtypes = [POINTER(ISC_STATUS), POINTER(isc_blob_handle),
                                       c_short, ISC_LONG, POINTER(ISC_LONG)]

        self.isc_send = ib_library.isc_send
        self.isc_send.restype = ISC_STATUS
        self.isc_send.argtypes = [POINTER(ISC_STATUS), POINTER(isc_req_handle),
                                  c_short, c_short, c_void_p, c_short]

        self.isc_start_and_send = ib_library.isc_start_and_send
        self.isc_start_and_send.restype = ISC_STATUS
        self.isc_start_and_send.argtypes = [POINTER(ISC_STATUS), POINTER(isc_req_handle),
                                            POINTER(isc_tr_handle), c_short, c_short,
                                            c_void_p, c_short]

        self.isc_start_request = ib_library.isc_start_request
        self.isc_start_request.restype = ISC_STATUS
        self.isc_start_request.argtypes = [POINTER(ISC_STATUS), POINTER(isc_req_handle),
                                           POINTER(isc_tr_handle), c_short]

        self.isc_unwind_request = ib_library.isc_unwind_request
        self.isc_unwind_request.restype = ISC_STATUS
        self.isc_unwind_request.argtypes = [POINTER(ISC_STATUS), POINTER(isc_tr_handle),
                                            c_short]

        self.isc_wait_for_event = ib_library.isc_wait_for_event
        self.isc_wait_for_event.restype = ISC_STATUS
        self.isc_wait_for_event.argtypes = [POINTER(ISC_STATUS), POINTER(isc_db_handle),
                                            c_short, POINTER(ISC_UCHAR), POINTER(ISC_UCHAR)]

        self.isc_close = ib_library.isc_close
        self.isc_close.restype = ISC_STATUS
        self.isc_close.argtypes = [POINTER(ISC_STATUS), STRING]

        self.isc_declare = ib_library.isc_declare
        self.isc_declare.restype = ISC_STATUS
        self.isc_declare.argtypes = [POINTER(ISC_STATUS), STRING, STRING]

        self.isc_describe = ib_library.isc_describe
        self.isc_describe.restype = ISC_STATUS
        self.isc_describe.argtypes = [POINTER(ISC_STATUS), STRING, POINTER(XSQLDA)]

        self.isc_describe_bind = ib_library.isc_describe_bind
        self.isc_describe_bind.restype = ISC_STATUS
        self.isc_describe_bind.argtypes = [POINTER(ISC_STATUS), STRING, POINTER(XSQLDA)]

        self.isc_execute = ib_library.isc_execute
        self.isc_execute.restype = ISC_STATUS
        self.isc_execute.argtypes = [POINTER(ISC_STATUS), POINTER(isc_tr_handle),
                                     STRING, POINTER(XSQLDA)]

        self.isc_execute_immediate = ib_library.isc_execute_immediate
        self.isc_execute_immediate.restype = ISC_STATUS
        self.isc_execute_immediate.argtypes = [POINTER(ISC_STATUS),
                                               POINTER(isc_db_handle),
                                               POINTER(isc_tr_handle),
                                               POINTER(c_short), STRING]

        self.isc_fetch = ib_library.isc_fetch
        self.isc_fetch.restype = ISC_STATUS
        self.isc_fetch.argtypes = [POINTER(ISC_STATUS), STRING, POINTER(XSQLDA)]

        self.isc_open = ib_library.isc_open
        self.isc_open.restype = ISC_STATUS
        self.isc_open.argtypes = [POINTER(ISC_STATUS), POINTER(isc_tr_handle),
                                  STRING, POINTER(XSQLDA)]

        self.isc_prepare = ib_library.isc_prepare
        self.isc_prepare.restype = ISC_STATUS
        self.isc_prepare.argtypes = [POINTER(ISC_STATUS), POINTER(isc_db_handle),
                                     POINTER(isc_tr_handle), STRING, POINTER(c_short),
                                     STRING, POINTER(XSQLDA)]

        self.isc_dsql_execute_m = ib_library.isc_dsql_execute_m
        self.isc_dsql_execute_m.restype = ISC_STATUS
        self.isc_dsql_execute_m.argtypes = [POINTER(ISC_STATUS),
                                            POINTER(isc_tr_handle),
                                            POINTER(isc_stmt_handle), c_ushort,
                                            STRING, c_ushort, c_ushort, STRING]

        self.isc_dsql_execute2_m = ib_library.isc_dsql_execute2_m
        self.isc_dsql_execute2_m.restype = ISC_STATUS
        self.isc_dsql_execute2_m.argtypes = [POINTER(ISC_STATUS),
                                             POINTER(isc_tr_handle),
                                             POINTER(isc_stmt_handle), c_ushort,
                                             STRING, c_ushort, c_ushort, STRING,
                                             c_ushort, STRING, c_ushort, c_ushort,
                                             STRING]

        self.isc_dsql_execute_immediate_m = ib_library.isc_dsql_execute_immediate_m
        self.isc_dsql_execute_immediate_m.restype = ISC_STATUS
        self.isc_dsql_execute_immediate_m.argtypes = [POINTER(ISC_STATUS),
                                                      POINTER(isc_db_handle),
                                                      POINTER(isc_tr_handle),
                                                      c_ushort, STRING, c_ushort,
                                                      c_ushort, STRING, c_ushort,
                                                      c_ushort, STRING]

        self.isc_dsql_exec_immed3_m = ib_library.isc_dsql_exec_immed3_m
        self.isc_dsql_exec_immed3_m.restype = ISC_STATUS
        self.isc_dsql_exec_immed3_m.argtypes = [POINTER(ISC_STATUS),
                                                POINTER(isc_db_handle),
                                                POINTER(isc_tr_handle), c_ushort,
                                                STRING, c_ushort, c_ushort,
                                                STRING, c_ushort, c_ushort,
                                                STRING, c_ushort, STRING,
                                                c_ushort, c_ushort, STRING]

        self.isc_dsql_fetch_m = ib_library.isc_dsql_fetch_m
        self.isc_dsql_fetch_m.restype = ISC_STATUS
        self.isc_dsql_fetch_m.argtypes = [POINTER(ISC_STATUS),
                                          POINTER(isc_stmt_handle), c_ushort,
                                          STRING, c_ushort, c_ushort, STRING]

        self.isc_dsql_insert_m = ib_library.isc_dsql_insert_m
        self.isc_dsql_insert_m.restype = ISC_STATUS
        self.isc_dsql_insert_m.argtypes = [POINTER(ISC_STATUS),
                                           POINTER(isc_stmt_handle), c_ushort,
                                           STRING, c_ushort, c_ushort, STRING]

        self.isc_dsql_prepare_m = ib_library.isc_dsql_prepare_m
        self.isc_dsql_prepare_m.restype = ISC_STATUS
        self.isc_dsql_prepare_m.argtypes = [POINTER(ISC_STATUS),
                                            POINTER(isc_tr_handle),
                                            POINTER(isc_stmt_handle), c_ushort,
                                            STRING, c_ushort, c_ushort, STRING,
                                            c_ushort, STRING]

        self.isc_dsql_release = ib_library.isc_dsql_release
        self.isc_dsql_release.restype = ISC_STATUS
        self.isc_dsql_release.argtypes = [POINTER(ISC_STATUS), STRING]

        self.isc_embed_dsql_close = ib_library.isc_embed_dsql_close
        self.isc_embed_dsql_close.restype = ISC_STATUS
        self.isc_embed_dsql_close.argtypes = [POINTER(ISC_STATUS), STRING]

        self.isc_embed_dsql_declare = ib_library.isc_embed_dsql_declare
        self.isc_embed_dsql_declare.restype = ISC_STATUS
        self.isc_embed_dsql_declare.argtypes = [POINTER(ISC_STATUS), STRING, STRING]

        self.isc_embed_dsql_describe = ib_library.isc_embed_dsql_describe
        self.isc_embed_dsql_describe.restype = ISC_STATUS
        self.isc_embed_dsql_describe.argtypes = [POINTER(ISC_STATUS), STRING,
                                                 c_ushort, POINTER(XSQLDA)]

        self.isc_embed_dsql_describe_bind = ib_library.isc_embed_dsql_describe_bind
        self.isc_embed_dsql_describe_bind.restype = ISC_STATUS
        self.isc_embed_dsql_describe_bind.argtypes = [POINTER(ISC_STATUS), STRING,
                                                      c_ushort, POINTER(XSQLDA)]

        self.isc_embed_dsql_execute = ib_library.isc_embed_dsql_execute
        self.isc_embed_dsql_execute.restype = ISC_STATUS
        self.isc_embed_dsql_execute.argtypes = [POINTER(ISC_STATUS),
                                                POINTER(isc_tr_handle),
                                                STRING, c_ushort, POINTER(XSQLDA)]

        self.isc_embed_dsql_execute2 = ib_library.isc_embed_dsql_execute2
        self.isc_embed_dsql_execute2.restype = ISC_STATUS
        self.isc_embed_dsql_execute2.argtypes = [POINTER(ISC_STATUS),
                                                 POINTER(isc_tr_handle),
                                                 STRING, c_ushort, POINTER(XSQLDA),
                                                 POINTER(XSQLDA)]

        self.isc_embed_dsql_execute_immed = ib_library.isc_embed_dsql_execute_immed
        self.isc_embed_dsql_execute_immed.restype = ISC_STATUS
        self.isc_embed_dsql_execute_immed.argtypes = [POINTER(ISC_STATUS),
                                                      POINTER(isc_db_handle),
                                                      POINTER(isc_tr_handle),
                                                      c_ushort, STRING, c_ushort,
                                                      POINTER(XSQLDA)]

        self.isc_embed_dsql_fetch = ib_library.isc_embed_dsql_fetch
        self.isc_embed_dsql_fetch.restype = ISC_STATUS
        self.isc_embed_dsql_fetch.argtypes = [POINTER(ISC_STATUS), STRING,
                                              c_ushort, POINTER(XSQLDA)]

        self.isc_embed_dsql_fetch_a = ib_library.isc_embed_dsql_fetch_a
        self.isc_embed_dsql_fetch_a.restype = ISC_STATUS
        self.isc_embed_dsql_fetch_a.argtypes = [POINTER(ISC_STATUS), POINTER(c_int),
                                                STRING, ISC_USHORT, POINTER(XSQLDA)]

        self.isc_embed_dsql_open = ib_library.isc_embed_dsql_open
        self.isc_embed_dsql_open.restype = ISC_STATUS
        self.isc_embed_dsql_open.argtypes = [POINTER(ISC_STATUS),
                                             POINTER(isc_tr_handle),
                                             STRING, c_ushort, POINTER(XSQLDA)]

        self.isc_embed_dsql_open2 = ib_library.isc_embed_dsql_open2
        self.isc_embed_dsql_open2.restype = ISC_STATUS
        self.isc_embed_dsql_open2.argtypes = [POINTER(ISC_STATUS),
                                              POINTER(isc_tr_handle),
                                              STRING, c_ushort, POINTER(XSQLDA),
                                              POINTER(XSQLDA)]

        self.isc_embed_dsql_insert = ib_library.isc_embed_dsql_insert
        self.isc_embed_dsql_insert.restype = ISC_STATUS
        self.isc_embed_dsql_insert.argtypes = [POINTER(ISC_STATUS), STRING,
                                               c_ushort, POINTER(XSQLDA)]

        self.isc_embed_dsql_prepare = ib_library.isc_embed_dsql_prepare
        self.isc_embed_dsql_prepare.restype = ISC_STATUS
        self.isc_embed_dsql_prepare.argtypes = [POINTER(ISC_STATUS),
                                                POINTER(isc_db_handle),
                                                POINTER(isc_tr_handle), STRING,
                                                c_ushort, STRING, c_ushort,
                                                POINTER(XSQLDA)]

        self.isc_embed_dsql_release = ib_library.isc_embed_dsql_release
        self.isc_embed_dsql_release.restype = ISC_STATUS
        self.isc_embed_dsql_release.argtypes = [POINTER(ISC_STATUS), STRING]

        self.BLOB_open = ib_library.BLOB_open
        self.BLOB_open.restype = POINTER(BSTREAM)
        self.BLOB_open.argtypes = [isc_blob_handle, STRING, c_int]

        self.BLOB_put = ib_library.BLOB_put
        self.BLOB_put.restype = c_int
        self.BLOB_put.argtypes = [ISC_SCHAR, POINTER(BSTREAM)]

        self.BLOB_close = ib_library.BLOB_close
        self.BLOB_close.restype = c_int
        self.BLOB_close.argtypes = [POINTER(BSTREAM)]

        self.BLOB_get = ib_library.BLOB_get
        self.BLOB_get.restype = c_int
        self.BLOB_get.argtypes = [POINTER(BSTREAM)]

        self.BLOB_display = ib_library.BLOB_display
        self.BLOB_display.restype = c_int
        self.BLOB_display.argtypes = [POINTER(ISC_QUAD), isc_db_handle,
                                      isc_tr_handle, STRING]

        self.BLOB_dump = ib_library.BLOB_dump
        self.BLOB_dump.restype = c_int
        self.BLOB_dump.argtypes = [POINTER(ISC_QUAD), isc_db_handle, isc_tr_handle,
                                   STRING]

        self.BLOB_edit = ib_library.BLOB_edit
        self.BLOB_edit.restype = c_int
        self.BLOB_edit.argtypes = [POINTER(ISC_QUAD), isc_db_handle,
                                   isc_tr_handle, STRING]

        self.BLOB_load = ib_library.BLOB_load
        self.BLOB_load.restype = c_int
        self.BLOB_load.argtypes = [POINTER(ISC_QUAD), isc_db_handle,
                                   isc_tr_handle, STRING]

        self.BLOB_text_dump = ib_library.BLOB_text_dump
        self.BLOB_text_dump.restype = c_int
        self.BLOB_text_dump.argtypes = [POINTER(ISC_QUAD), isc_db_handle,
                                        isc_tr_handle, STRING]

        self.BLOB_text_load = ib_library.BLOB_text_load
        self.BLOB_text_load.restype = c_int
        self.BLOB_text_load.argtypes = [POINTER(ISC_QUAD), isc_db_handle,
                                        isc_tr_handle, STRING]

        self.Bopen = ib_library.Bopen
        self.Bopen.restype = POINTER(BSTREAM)
        self.Bopen.argtypes = [POINTER(ISC_QUAD), isc_db_handle, isc_tr_handle,
                               STRING]

        self.isc_ftof = ib_library.isc_ftof
        self.isc_ftof.restype = ISC_LONG
        self.isc_ftof.argtypes = [STRING, c_ushort, STRING, c_ushort]

        self.isc_print_blr = ib_library.isc_print_blr
        self.isc_print_blr.restype = ISC_STATUS
        self.isc_print_blr.argtypes = [STRING, ISC_PRINT_CALLBACK, c_void_p, c_short]

        self.isc_set_debug = ib_library.isc_set_debug
        self.isc_set_debug.restype = None
        self.isc_set_debug.argtypes = [c_int]

        self.isc_qtoq = ib_library.isc_qtoq
        self.isc_qtoq.restype = None
        self.isc_qtoq.argtypes = [POINTER(ISC_QUAD), POINTER(ISC_QUAD)]

        self.isc_vtof = ib_library.isc_vtof
        self.isc_vtof.restype = None
        self.isc_vtof.argtypes = [STRING, STRING, c_ushort]

        self.isc_vtov = ib_library.isc_vtov
        self.isc_vtov.restype = None
        self.isc_vtov.argtypes = [STRING, STRING, c_short]

        self.isc_version = ib_library.isc_version
        self.isc_version.restype = c_int
        self.isc_version.argtypes = [POINTER(isc_db_handle),
                                     ISC_VERSION_CALLBACK, c_void_p]

        # deprecated
        #self.isc_reset_fpe = ib_library.isc_reset_fpe
        #self.isc_reset_fpe.restype = ISC_LONG
        #self.isc_reset_fpe.argtypes = [ISC_USHORT]

        self.isc_service_attach = ib_library.isc_service_attach
        self.isc_service_attach.restype = ISC_STATUS
        self.isc_service_attach.argtypes = [POINTER(ISC_STATUS), c_ushort, STRING,
                                            POINTER(isc_svc_handle), c_ushort, STRING]

        self.isc_service_detach = ib_library.isc_service_detach
        self.isc_service_detach.restype = ISC_STATUS
        self.isc_service_detach.argtypes = [POINTER(ISC_STATUS),
                                            POINTER(isc_svc_handle)]

        self.isc_service_query = ib_library.isc_service_query
        self.isc_service_query.restype = ISC_STATUS
        self.isc_service_query.argtypes = [POINTER(ISC_STATUS),
                                           POINTER(isc_svc_handle),
                                           POINTER(isc_resv_handle), c_ushort,
                                           STRING, c_ushort, STRING, c_ushort,
                                           STRING]

        self.isc_service_start = ib_library.isc_service_start
        self.isc_service_start.restype = ISC_STATUS
        self.isc_service_start.argtypes = [POINTER(ISC_STATUS),
                                           POINTER(isc_svc_handle),
                                           POINTER(isc_resv_handle),
                                           c_ushort, STRING]

        self.isc_get_client_version = ib_library.isc_get_client_version
        self.isc_get_client_version.restype = None
        self.isc_get_client_version.argtypes = [STRING]

        self.isc_get_client_major_version = ib_library.isc_get_client_major_version
        self.isc_get_client_major_version.restype = c_int
        self.isc_get_client_major_version.argtypes = []

        self.isc_get_client_minor_version = ib_library.isc_get_client_minor_version
        self.isc_get_client_minor_version.restype = c_int
        self.isc_get_client_minor_version.argtypes = []

        #self.imaxabs = ib_library.imaxabs
        #self.imaxabs.restype = intmax_t
        #self.imaxabs.argtypes = [intmax_t]

        #self.imaxdiv = ib_library.imaxdiv
        #self.imaxdiv.restype = imaxdiv_t
        #self.imaxdiv.argtypes = [intmax_t, intmax_t]

        #self.strtoimax = ib_library.strtoimax
        #self.strtoimax.restype = intmax_t
        #self.strtoimax.argtypes = [STRING, POINTER(STRING), c_int]

        #self.strtoumax = ib_library.strtoumax
        #self.strtoumax.restype = uintmax_t
        #self.strtoumax.argtypes = [STRING, POINTER(STRING), c_int]

        #self.wcstoimax = ib_library.wcstoimax
        #self.wcstoimax.restype = intmax_t
        #self.wcstoimax.argtypes = [WSTRING, POINTER(WSTRING), c_int]

        #self.wcstoumax = ib_library.wcstoumax
        #self.wcstoumax.restype = uintmax_t
        #self.wcstoumax.argtypes = [WSTRING, POINTER(WSTRING), c_int]

        self.P_isc_event_block = CFUNCTYPE(ISC_LONG,POINTER(POINTER(ISC_UCHAR)),
                                    POINTER(POINTER(ISC_UCHAR)), ISC_USHORT)
        self.C_isc_event_block = self.P_isc_event_block(('isc_event_block',ib_library))
        self.P_isc_event_block_args = self.C_isc_event_block.argtypes

    def isc_event_block(self,event_buffer,result_buffer,*args):
        if len(args) > 15:
            raise Exception("isc_event_block takes no more than 15 event names")
        newargs = list(self.P_isc_event_block_args)
        for x in args:
            newargs.append(STRING)
        self.C_isc_event_block.argtypes = newargs
        result = self.C_isc_event_block(event_buffer,result_buffer,len(args),*args)
        return result


