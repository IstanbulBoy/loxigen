# Copyright 2013, Big Switch Networks, Inc.
#
# LoxiGen is licensed under the Eclipse Public License, version 1.0 (EPL), with
# the following special exception:
#
# LOXI Exception
#
# As a special exception to the terms of the EPL, you may distribute libraries
# generated by LoxiGen (LoxiGen Libraries) under the terms of your choice, provided
# that copyright and licensing notices generated by LoxiGen are not altered or removed
# from the LoxiGen Libraries and the notice provided below is (i) included in
# the LoxiGen Libraries, if distributed in source code form and (ii) included in any
# documentation for the LoxiGen Libraries, if distributed in binary form.
#
# Notice: "Copyright 2013, Big Switch Networks, Inc. This library was generated by the LoxiGen Compiler."
#
# You may not use this file except in compliance with the EPL or LOXI Exception. You may obtain
# a copy of the EPL at:
#
# http://www.eclipse.org/legal/epl-v10.html
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# EPL for the specific language governing permissions and limitations
# under the EPL.

# @brief Generate wire to generic match conversion functions
#
# @fixme This has lots of C specific code that should be moved into c_gen

# of_match_to_wire_match(match, wire_match)
# of_wire_match_to_match(wire_match, match)
#    Version is taken from the source in each case
#
# name
# type
# conditions
# v3 ident
# takes mask

import sys
import c_gen.of_g_legacy as of_g
import c_gen.match as match
import c_code_gen

def match_c_top_matter(out, name):
    """
    Generate top matter for match C file

    @param name The name of the output file
    @param out The output file object
    """
    c_code_gen.common_top_matter(out, name)
    out.write("#include \"loci_log.h\"\n")
    out.write("#include <loci/loci.h>\n")

def match_h_top_matter(out, name):
    """
    Generate top matter for the C file

    @param name The name of the output file
    @param ih_name The name of the internal header file
    @param out The output file object
    """
    c_code_gen.common_top_matter(out, name)
    out.write("""
#include <loci/loci_base.h>
""")

def gen_declarations(out):
    out.write("""
/*
 * Match serialize/deserialize declarations
 * Wire match conversion function declarations
 */
extern int of_match_serialize(of_version_t version, of_match_t *match,
                              of_octets_t *octets);
extern int of_match_deserialize(of_version_t version, of_match_t *match,
                                of_octets_t *octets);
extern int of_match_v1_to_match(of_match_v1_t *src, of_match_t *dst);
extern int of_match_v2_to_match(of_match_v2_t *src, of_match_t *dst);
extern int of_match_v3_to_match(of_match_v3_t *src, of_match_t *dst);
extern int of_match_to_wire_match_v1(of_match_t *src, of_match_v1_t *dst);
extern int of_match_to_wire_match_v2(of_match_t *src, of_match_v2_t *dst);
extern int of_match_to_wire_match_v3(of_match_t *src, of_match_v3_t *dst);
""")

def gen_v4_match_compat(out):
    """
    Code for coercing version 1.3 matches to 1.2 matches

    @FIXME This is a stopgap and needs to get cleaned up.
    """
    out.write("""
/**
 * Definitions to coerce v4 match (version 1.3) to v3 matches
 * (version 1.2).
 * @FIXME This is a stopgap and needs to get cleaned up.
 */
#define of_match_v4_t of_match_v3_t
#define of_match_v4_init of_match_v3_init
#define of_match_v4_new of_match_v3_new
#define of_match_v4_to_match of_match_v3_to_match
#define of_match_to_wire_match_v4 of_match_to_wire_match_v3
#define of_match_v4_delete of_match_v3_delete
""")

def gen_match_macros(out):
    out.write("""

/**
 * Definitions for wildcard macros for OF_VERSION_1_0
 */

""")
    for key in match.of_v1_keys:
        entry = match.of_match_members[key]
        if "v1_wc_shift" in entry:
            if key in ["ipv4_src", "ipv4_dst"]:
                out.write("""
#define OF_MATCH_V1_WC_%(ku)s_SHIFT %(val)d
#define OF_MATCH_V1_WC_%(ku)s_MASK (0x3f << %(val)d)
#define OF_MATCH_V1_WC_%(ku)s_CLEAR(wc) ((wc) &= ~(0x3f << %(val)d))
#define OF_MATCH_V1_WC_%(ku)s_SET(wc, value) do {   \\
        OF_MATCH_V1_WC_%(ku)s_CLEAR(wc); \\
        ((wc) |= (((value) & 0x3f) << %(val)d)); \\
    } while (0)
#define OF_MATCH_V1_WC_%(ku)s_TEST(wc) ((wc) & (0x3f << %(val)d))
#define OF_MATCH_V1_WC_%(ku)s_GET(wc) (((wc) >> %(val)d) & 0x3f)
""" % dict(ku=key.upper(), val=entry["v1_wc_shift"]))
            else:
                out.write("""
#define OF_MATCH_V1_WC_%(ku)s_SHIFT %(val)d
#define OF_MATCH_V1_WC_%(ku)s_MASK (1 << %(val)d)
#define OF_MATCH_V1_WC_%(ku)s_SET(wc) ((wc) |= (1 << %(val)d))
#define OF_MATCH_V1_WC_%(ku)s_CLEAR(wc) ((wc) &= ~(1 << %(val)d))
#define OF_MATCH_V1_WC_%(ku)s_TEST(wc) ((wc) & (1 << %(val)d))
""" % dict(ku=key.upper(), val=entry["v1_wc_shift"]))

    out.write("""

/**
 * Definitions for wildcard macros for OF_VERSION_1_1
 */
""")

    for key in sorted(match.of_v2_keys):
        entry = match.of_match_members[key]
        if "v2_wc_shift" in entry:
            out.write("""
#define OF_MATCH_V2_WC_%(ku)s_SHIFT %(val)d
#define OF_MATCH_V2_WC_%(ku)s_MASK (1 << %(val)d)
#define OF_MATCH_V2_WC_%(ku)s_SET(wc) ((wc) |= (1 << %(val)d))
#define OF_MATCH_V2_WC_%(ku)s_CLEAR(wc) ((wc) &= ~(1 << %(val)d))
#define OF_MATCH_V2_WC_%(ku)s_TEST(wc) ((wc) & (1 << %(val)d))
""" % dict(ku=key.upper(), val=entry["v2_wc_shift"]))


def gen_match_struct(out=sys.stdout):
    out.write("/* Unified, flat OpenFlow match structure based on OF 1.2 */\n")
    out.write("typedef struct of_match_fields_s {\n")
    out.write("    /* Version 1.2 is used for field names */\n")
    for name in match.match_keys_sorted:
        entry = match.of_match_members[name]
        out.write("    %-20s %s;\n" % (entry["m_type"], entry["name"]))
    out.write("""
} of_match_fields_t;

/**
 * @brief The LOCI match structure.
 */

typedef struct of_match_s {
    of_version_t version;
    of_match_fields_t fields;
    of_match_fields_t masks;
} of_match_t;

/**
 * Mask the values in the match structure according to its fields
 */
static inline void of_match_values_mask(of_match_t *match)
{
    int idx;

    for (idx = 0; idx < sizeof(of_match_fields_t); idx++) {
        ((uint8_t *)&match->fields)[idx] &= ((uint8_t *)&match->masks)[idx];
    }
}

static inline void
of_memmask(void *_fields, void *_masks, size_t len)
{
    int idx;
    uint8_t *fields = _fields;
    uint8_t *masks = _masks;

    for (idx = 0; idx < len; idx++) {
        fields[idx] &= masks[idx];
    }
}

/**
 * IP Mask map.  IP maks wildcards from OF 1.0 are interpretted as
 * indices into the map below.
 *
 * of_ip_mask_map: Array mapping index to mask
 * of_ip_mask_use_map: Boolean indication set when map is initialized
 * of_ip_mask_map_init: Initialize to default values; set "use map".
 */
#define OF_IP_MASK_MAP_COUNT 64
extern uint32_t of_ip_mask_map[OF_IP_MASK_MAP_COUNT];
extern int of_ip_mask_map_init_done;

#define OF_IP_MASK_INIT_CHECK \
    if (!of_ip_mask_map_init_done) of_ip_mask_map_init()

/**
 * Initialize map
 */
extern void of_ip_mask_map_init(void);

extern int of_ip_mask_map_set(int index, uint32_t mask);
extern int of_ip_mask_map_get(int index, uint32_t *mask);

/**
 * @brief Map from mask to index
 */

extern int of_ip_mask_to_index(uint32_t mask);

/**
 * @brief Map from index to mask
 */

extern uint32_t of_ip_index_to_mask(int index);

/**
 * The signalling of an untagged packet varies by OF version.
 * Use this macro to set the field value.
 */
#define OF_MATCH_UNTAGGED_VLAN_ID(version) \\
    ((version) == OF_VERSION_1_0 ? 0xffff : \\
     ((version) == OF_VERSION_1_1 ? 0xffff : 0))

/**
 * Version 1.1 had the notion of "any" vlan but must be set
 */
#define OF_MATCH_VLAN_TAG_PRESENT_ANY_ID(version) \\
    ((version) == OF_VERSION_1_0 ? 0 /* @fixme */  : \\
     ((version) == OF_VERSION_1_1 ? 0xfffe : 0x1000))
""")

def gen_oxm_defines(out):
    """
    Generate verbatim definitions for OXM
    """
    out.write("""

/* These are from the OpenFlow 1.2 header file */

/* OXM index values for bitmaps and parsing */
enum of_oxm_index_e {
    OF_OXM_INDEX_IN_PORT        = 0,  /* Switch input port. */
    OF_OXM_INDEX_IN_PHY_PORT    = 1,  /* Switch physical input port. */
    OF_OXM_INDEX_METADATA       = 2,  /* Metadata passed between tables. */
    OF_OXM_INDEX_ETH_DST        = 3,  /* Ethernet destination address. */
    OF_OXM_INDEX_ETH_SRC        = 4,  /* Ethernet source address. */
    OF_OXM_INDEX_ETH_TYPE       = 5,  /* Ethernet frame type. */
    OF_OXM_INDEX_VLAN_VID       = 6,  /* VLAN id. */
    OF_OXM_INDEX_VLAN_PCP       = 7,  /* VLAN priority. */
    OF_OXM_INDEX_IP_DSCP        = 8,  /* IP DSCP (6 bits in ToS field). */
    OF_OXM_INDEX_IP_ECN         = 9,  /* IP ECN (2 bits in ToS field). */
    OF_OXM_INDEX_IP_PROTO       = 10, /* IP protocol. */
    OF_OXM_INDEX_IPV4_SRC       = 11, /* IPv4 source address. */
    OF_OXM_INDEX_IPV4_DST       = 12, /* IPv4 destination address. */
    OF_OXM_INDEX_TCP_SRC        = 13, /* TCP source port. */
    OF_OXM_INDEX_TCP_DST        = 14, /* TCP destination port. */
    OF_OXM_INDEX_UDP_SRC        = 15, /* UDP source port. */
    OF_OXM_INDEX_UDP_DST        = 16, /* UDP destination port. */
    OF_OXM_INDEX_SCTP_SRC       = 17, /* SCTP source port. */
    OF_OXM_INDEX_SCTP_DST       = 18, /* SCTP destination port. */
    OF_OXM_INDEX_ICMPV4_TYPE    = 19, /* ICMP type. */
    OF_OXM_INDEX_ICMPV4_CODE    = 20, /* ICMP code. */
    OF_OXM_INDEX_ARP_OP         = 21, /* ARP opcode. */
    OF_OXM_INDEX_ARP_SPA        = 22, /* ARP source IPv4 address. */
    OF_OXM_INDEX_ARP_TPA        = 23, /* ARP target IPv4 address. */
    OF_OXM_INDEX_ARP_SHA        = 24, /* ARP source hardware address. */
    OF_OXM_INDEX_ARP_THA        = 25, /* ARP target hardware address. */
    OF_OXM_INDEX_IPV6_SRC       = 26, /* IPv6 source address. */
    OF_OXM_INDEX_IPV6_DST       = 27, /* IPv6 destination address. */
    OF_OXM_INDEX_IPV6_FLABEL    = 28, /* IPv6 Flow Label */
    OF_OXM_INDEX_ICMPV6_TYPE    = 29, /* ICMPv6 type. */
    OF_OXM_INDEX_ICMPV6_CODE    = 30, /* ICMPv6 code. */
    OF_OXM_INDEX_IPV6_ND_TARGET = 31, /* Target address for ND. */
    OF_OXM_INDEX_IPV6_ND_SLL    = 32, /* Source link-layer for ND. */
    OF_OXM_INDEX_IPV6_ND_TLL    = 33, /* Target link-layer for ND. */
    OF_OXM_INDEX_MPLS_LABEL     = 34, /* MPLS label. */
    OF_OXM_INDEX_MPLS_TC        = 35, /* MPLS TC. */

    OF_OXM_INDEX_BSN_IN_PORTS_128 = 36,
    OF_OXM_INDEX_BSN_LAG_ID = 37,
    OF_OXM_INDEX_BSN_VRF = 38,
    OF_OXM_INDEX_BSN_GLOBAL_VRF_ALLOWED = 39,
    OF_OXM_INDEX_BSN_L3_INTERFACE_CLASS_ID = 40,
    OF_OXM_INDEX_BSN_L3_SRC_CLASS_ID = 41,
    OF_OXM_INDEX_BSN_L3_DST_CLASS_ID = 42,
    OF_OXM_INDEX_BSN_EGR_PORT_GROUP_ID = 43,
    OF_OXM_INDEX_BSN_UDF0 = 44,
    OF_OXM_INDEX_BSN_UDF1 = 45,
    OF_OXM_INDEX_BSN_UDF2 = 46,
    OF_OXM_INDEX_BSN_UDF3 = 47,
    OF_OXM_INDEX_BSN_UDF4 = 48,
    OF_OXM_INDEX_BSN_UDF5 = 49,
    OF_OXM_INDEX_BSN_UDF6 = 50,
    OF_OXM_INDEX_BSN_UDF7 = 51,
};

#define OF_OXM_BIT(index) (((uint64_t) 1) << (index))

/*
 * The generic match structure uses the OXM bit indices for it's
 * bitmasks for active and masked values
 */
""")
    for key, entry in match.of_match_members.items():
        out.write("""
/* Mask/value check/set macros for %(key)s */

/**
 * Set the mask for an exact match of %(key)s
 */
#define OF_MATCH_MASK_%(ku)s_EXACT_SET(_match)   \\
    MEMSET(&(_match)->masks.%(key)s, 0xff, \\
        sizeof(((_match)->masks).%(key)s))

/**
 * Clear the mask for %(key)s making that field inactive for the match
 */
#define OF_MATCH_MASK_%(ku)s_CLEAR(_match) \\
    MEMSET(&(_match)->masks.%(key)s, 0, \\
        sizeof(((_match)->masks).%(key)s))

/**
 * Test whether the match is exact for %(key)s
 */
#define OF_MATCH_MASK_%(ku)s_EXACT_TEST(_match) \\
    OF_VARIABLE_IS_ALL_ONES(&(((_match)->masks).%(key)s))

/**
 * Test whether key %(key)s is being checked in the match
 */
#define OF_MATCH_MASK_%(ku)s_ACTIVE_TEST(_match) \\
    OF_VARIABLE_IS_NON_ZERO(&(((_match)->masks).%(key)s))

""" % dict(key=key, bit=match.oxm_index(key), ku=key.upper()))

def gen_incompat_members(out=sys.stdout):
    """
    Generate a macro that lists all the unified fields which are
    incompatible with v1 matches
    """
    out.write("""
/* Identify bits in unified match that are incompatible with V1, V2 matches */
#define OF_MATCH_V1_INCOMPAT ( (uint64_t)0 """)
    for key in match.of_match_members:
        if key in match.of_v1_keys:
            continue
        out.write("\\\n    | ((uint64_t)1 << %s)" % match.oxm_index(key))
    out.write(")\n\n")

    out.write("#define OF_MATCH_V2_INCOMPAT ( (uint64_t)0 ")
    for key in match.of_match_members:
        if key in match.of_v2_keys:
            continue
        out.write("\\\n    | ((uint64_t)1 << %s)" % match.oxm_index(key))
    out.write(""")

/* Indexed by version number */
extern const uint64_t of_match_incompat[4];
""")


# # FIXME:  Make these version specific
# def name_to_index(a, name, key="name"):
#     """
#     Given an array, a, with each entry a dict, and a name,
#     find the entry with key matching name and return the index
#     """
#     count = 0
#     for e in a:
#         if e[key] == name:
#             return count
#         count += 1
#     return -1

def gen_wc_convert_literal(out):
    """
    A bunch of literal C code that's associated with match conversions
    @param out The output file handle
    """
    out.write("""

/* Some internal macros and utility functions */

/* For counting bits in a uint32 */
#define _VAL_AND_5s(v)  ((v) & 0x55555555)
#define _VAL_EVERY_OTHER(v)  (_VAL_AND_5s(v) + _VAL_AND_5s(v >> 1))
#define _VAL_AND_3s(v)  ((v) & 0x33333333)
#define _VAL_PAIRS(v)  (_VAL_AND_3s(v) + _VAL_AND_3s(v >> 2))
#define _VAL_QUADS(v)  (((val) + ((val) >> 4)) & 0x0F0F0F0F)
#define _VAL_BYTES(v)  ((val) + ((val) >> 8))

/**
 * Counts the number of bits set in an integer
 */
static inline int
_COUNT_BITS(unsigned int val)
{
    val = _VAL_EVERY_OTHER(val);
    val = _VAL_PAIRS(val);
    val = _VAL_QUADS(val);
    val = _VAL_BYTES(val);

    return (val & 0XFF) + ((val >> 16) & 0xFF);
}

/* Indexed by version number */
const uint64_t of_match_incompat[4] = {
    -1,
    OF_MATCH_V1_INCOMPAT,
    OF_MATCH_V2_INCOMPAT,
    0
};

""")


def gen_unified_match_to_v1(out):
    """
    Generate C code to convert a unified match structure to a V1 match struct
    @param out The output file handle
    """

    out.write("""
/**
 * Check if match is compatible with OF 1.0
 * @param match The match being checked
 */
static inline int
of_match_v1_compat_check(of_match_t *match)
{
""")
    for key in match.of_match_members:
        if key in match.of_v1_keys:
            continue
        out.write("""
    if (OF_MATCH_MASK_%(ku)s_ACTIVE_TEST(match)) {
        return 0;
    }
""" % dict(ku=key.upper()))

    out.write("""
    return 1;
}
""")

    out.write("""
/**
 * Convert a generic match object to an OF_VERSION_1_0 object
 * @param src Pointer to the generic match object source
 * @param dst Pointer to the OF 1.0 wire structure
 *
 * The wire structure is initialized by this function if it doesn't
 * not have the proper object ID.
 */

int
of_match_to_wire_match_v1(of_match_t *src, of_match_v1_t *dst)
{
    of_wc_bmap_t wildcards = 0;
    int ip_mask_index;

    if ((src == NULL) || (dst == NULL)) {
        return OF_ERROR_PARAM;
    }
    if (!of_match_v1_compat_check(src)) {
        return OF_ERROR_COMPAT;
    }
    if (dst->object_id != OF_MATCH_V1) {
        of_match_v1_init(dst, OF_VERSION_1_0, 0, 0);
    }
""")
    for key in sorted(match.of_v1_keys):
        if key in ["ipv4_src", "ipv4_dst"]: # Special cases for masks here
            out.write("""
    if (OF_MATCH_MASK_%(ku)s_ACTIVE_TEST(src)) {
        ip_mask_index = of_ip_mask_to_index(src->masks.%(key)s);
        of_match_v1_%(key)s_set(dst, src->fields.%(key)s);
    } else { /* Wildcarded, look for 0 mask */
        ip_mask_index = of_ip_mask_to_index(0);
    }
    OF_MATCH_V1_WC_%(ku)s_SET(wildcards, ip_mask_index);
""" % dict(key=key, ku=key.upper()))
        else:
            out.write("""
    if (OF_MATCH_MASK_%(ku)s_ACTIVE_TEST(src)) {
        of_match_v1_%(key)s_set(dst, src->fields.%(key)s);
    } else {
        OF_MATCH_V1_WC_%(ku)s_SET(wildcards);
    }
""" % dict(key=key, ku=key.upper()))

    out.write("""
    of_match_v1_wildcards_set(dst, wildcards);

    return OF_ERROR_NONE;
}
""")

def all_ones_mask(d_type):
    if d_type == "of_mac_addr_t":
        return "of_mac_addr_all_ones"
    else:
        return "((%s) -1)" % d_type

def gen_unified_match_to_v2(out):
    """
    Generate C code to convert a unified match structure to a V2 match struct
    @param out The output file handle
    """

    out.write("""
/**
 * Check if match is compatible with OF 1.0
 * @param match The match being checked
 */
static inline int
of_match_v2_compat_check(of_match_t *match)
{
""")
    for key in match.of_match_members:
        if key in match.of_v2_keys:
            continue
        out.write("""
    if (OF_MATCH_MASK_%(ku)s_ACTIVE_TEST(match)) {
        return 0;
    }
""" % dict(ku=key.upper()))

    out.write("""
    return 1;
}
""")

    out.write("""
/**
 * Convert a generic match object to an OF_VERSION_1_1 object
 * @param src Pointer to the generic match object source
 * @param dst Pointer to the OF 1.1 wire structure
 *
 * The wire structure is initialized by this function.
 */

int
of_match_to_wire_match_v2(of_match_t *src, of_match_v2_t *dst)
{
    of_wc_bmap_t wildcards = 0;

    if ((src == NULL) || (dst == NULL)) {
        return OF_ERROR_PARAM;
    }
    if (!of_match_v2_compat_check(src)) {
        return OF_ERROR_COMPAT;
    }
    if (dst->object_id != OF_MATCH_V2) {
        of_match_v2_init(dst, OF_VERSION_1_1, 0, 0);
    }
""")
    for key in match.of_v2_keys:
        if key in match.of_v2_full_mask:
            ones_mask = all_ones_mask(match.of_match_members[key]["m_type"])
            out.write("""
    if (OF_MATCH_MASK_%(ku)s_ACTIVE_TEST(src)) {
        if (!OF_MATCH_MASK_%(ku)s_EXACT_TEST(src)) {
            of_match_v2_%(key)s_mask_set(dst,
                src->masks.%(key)s);
        } else { /* Exact match; use all ones mask */
            of_match_v2_%(key)s_mask_set(dst,
                %(ones_mask)s);
        }
        of_match_v2_%(key)s_set(dst, src->fields.%(key)s);
    }

""" % dict(key=key, ku=key.upper(), ones_mask=ones_mask))
        else:
            out.write("""
    if (!OF_MATCH_MASK_%(ku)s_EXACT_TEST(src)) {
        return OF_ERROR_COMPAT;
    }
    if (OF_MATCH_MASK_%(ku)s_ACTIVE_TEST(src)) {
        of_match_v2_%(key)s_set(dst, src->fields.%(key)s);
    } else {
        OF_MATCH_V2_WC_%(ku)s_SET(wildcards);
    }
""" % dict(key=key, ku=key.upper(),
           wc_bit="OF_MATCH_WC_V2_%s" % key.upper()))

    out.write("""
    of_match_v2_wildcards_set(dst, wildcards);

    return OF_ERROR_NONE;
}
""")

def gen_unified_match_to_v3(out):
    """
    Generate C code to convert a unified match structure to a V3 match

    This is much easier as the unified struct is based on V3
    @param out The output file handle
    """
    out.write("""
static int
populate_oxm_list(of_match_t *src, of_list_oxm_t *oxm_list)
{
    of_oxm_t oxm_entry;

    /* For each active member, add an OXM entry to the list */
""")
    for key in match.match_keys_sorted:
        entry = match.of_match_members[key]
        out.write("""\
    if (OF_MATCH_MASK_%(ku)s_ACTIVE_TEST(src)) {
        if (!OF_MATCH_MASK_%(ku)s_EXACT_TEST(src)) {
            of_oxm_%(key)s_masked_t *elt;
            elt = &oxm_entry.%(key)s_masked;

            of_oxm_%(key)s_masked_init(elt,
                oxm_list->version, -1, 1);
            of_list_oxm_append_bind(oxm_list, &oxm_entry);
            of_oxm_%(key)s_masked_value_set(elt,
                   src->fields.%(key)s);
            of_oxm_%(key)s_masked_value_mask_set(elt,
                   src->masks.%(key)s);
        } else {  /* Active, but not masked */
            of_oxm_%(key)s_t *elt;
            elt = &oxm_entry.%(key)s;
            of_oxm_%(key)s_init(elt,
                oxm_list->version, -1, 1);
            of_list_oxm_append_bind(oxm_list, &oxm_entry);
            of_oxm_%(key)s_value_set(elt, src->fields.%(key)s);
        }
    }
""" % dict(key=key, ku=key.upper()))
    out.write("""
    return OF_ERROR_NONE;
}

/**
 * Convert a generic match object to an OF_VERSION_1_2 object
 * @param src Pointer to the generic match object source
 * @param dst Pointer to the OF 1.2 wire structure
 *
 * The wire structure is initialized by this function if the object
 * id is not correct in the object
 */

int
of_match_to_wire_match_v3(of_match_t *src, of_match_v3_t *dst)
{
    int rv = OF_ERROR_NONE;
    of_list_oxm_t *oxm_list;

    if ((src == NULL) || (dst == NULL)) {
        return OF_ERROR_PARAM;
    }
    if (dst->object_id != OF_MATCH_V3) {
        of_match_v3_init(dst, OF_VERSION_1_2, 0, 0);
    }
    if ((oxm_list = of_list_oxm_new(dst->version)) == NULL) {
        return OF_ERROR_RESOURCE;
    }

    rv = populate_oxm_list(src, oxm_list);

    if (rv == OF_ERROR_NONE) {
        rv = of_match_v3_oxm_list_set(dst, oxm_list);
    }

    of_list_oxm_delete(oxm_list);

    return rv;
}
""")

def gen_v1_to_unified_match(out):
    """
    Generate the code that maps a v1 wire format match object
    to a unified match object
    """
    # for each v1 member, if not in wildcards
    # translate to unified.  Treat nw_src/dst specially
    out.write("""

/**
 * Convert an OF_VERSION_1_0 object to a generic match object
 * @param src Pointer to the OF 1.0 wire structure source
 * @param dst Pointer to the generic match object destination
 *
 * The wire structure is initialized by this function.
 */

int
of_match_v1_to_match(of_match_v1_t *src, of_match_t *dst)
{
    of_wc_bmap_t wc;
    int count;

    MEMSET(dst, 0, sizeof(*dst));
    dst->version = src->version;

    of_match_v1_wildcards_get(src, &wc);
""")
    for key in sorted(match.of_v1_keys):
        if key in ["ipv4_src", "ipv4_dst"]: # Special cases for masks here
            out.write("""
    count = OF_MATCH_V1_WC_%(ku)s_GET(wc);
    dst->masks.%(key)s = of_ip_index_to_mask(count);
    of_match_v1_%(key)s_get(src, &dst->fields.%(key)s);
    /* Clear the bits not indicated by mask; IP addrs are special for 1.0 */
    dst->fields.%(key)s &= dst->masks.%(key)s;
""" % dict(ku=key.upper(), key=key))
        else:
            out.write("""
    if (!(OF_MATCH_V1_WC_%(ku)s_TEST(wc))) {
        of_match_v1_%(key)s_get(src, &dst->fields.%(key)s);
        OF_MATCH_MASK_%(ku)s_EXACT_SET(dst);
    }
""" % dict(ku=key.upper(), key=key))

    out.write("""
    return OF_ERROR_NONE;
}
""")

def gen_v2_to_unified_match(out):
    """
    Generate the code that maps a v2 wire format match object
    to a unified match object
    """
    out.write("""
int
of_match_v2_to_match(of_match_v2_t *src, of_match_t *dst)
{
    of_wc_bmap_t wc;

    MEMSET(dst, 0, sizeof(*dst));
    dst->version = src->version;

    of_match_v2_wildcards_get(src, &wc);
""")
    for key in match.of_v2_keys:
        if key in match.of_v2_full_mask:
            out.write("""
    of_match_v2_%(key)s_mask_get(src, &dst->masks.%(key)s);
    if (OF_VARIABLE_IS_NON_ZERO(&dst->masks.%(key)s)) { /* Matching something */
        of_match_v2_%(key)s_get(src, &dst->fields.%(key)s);
    }
""" % dict(ku=key.upper(), key=key))
        else:
            out.write("""
    if (!(OF_MATCH_V2_WC_%(ku)s_TEST(wc))) {
        of_match_v2_%(key)s_get(src, &dst->fields.%(key)s);
        OF_MATCH_MASK_%(ku)s_EXACT_SET(dst);
    }
""" % dict(ku=key.upper(), key=key))

    out.write("""
    /* Clear values outside of masks */
    of_match_values_mask(dst);

    return OF_ERROR_NONE;
}
""")


def gen_v3_to_unified_match(out):
    """
    Generate the code that maps a v3 wire format match object
    to a unified match object
    """
    # Iterate thru the OXM list members
    out.write("""
int
of_match_v3_to_match(of_match_v3_t *src, of_match_t *dst)
{
    int rv;
    of_list_oxm_t oxm_list;
    of_oxm_t oxm_entry;
""")
#    for key in match.of_match_members:
#        out.write("    of_oxm_%s_t *%s;\n" % (key, key))
#        out.write("    of_oxm_%s_masked_t *%s_masked;\n" % (key, key))

    out.write("""
    MEMSET(dst, 0, sizeof(*dst));
    dst->version = src->version;

    of_match_v3_oxm_list_bind(src, &oxm_list);
    rv = of_list_oxm_first(&oxm_list, &oxm_entry);

    while (rv == OF_ERROR_NONE) {
        switch (oxm_entry.header.object_id) { /* What kind of entry is this */
""")
    for key in match.of_match_members:
        out.write("""
        case OF_OXM_%(ku)s_MASKED:
            of_oxm_%(key)s_masked_value_mask_get(
                &oxm_entry.%(key)s_masked,
                &dst->masks.%(key)s);
            of_oxm_%(key)s_masked_value_get(
                &oxm_entry.%(key)s,
                &dst->fields.%(key)s);
            of_memmask(&dst->fields.%(key)s, &dst->masks.%(key)s, sizeof(&dst->fields.%(key)s));
            break;
        case OF_OXM_%(ku)s:
            OF_MATCH_MASK_%(ku)s_EXACT_SET(dst);
            of_oxm_%(key)s_value_get(
                &oxm_entry.%(key)s,
                &dst->fields.%(key)s);
            break;
""" % (dict(ku=key.upper(), key=key)))

    out.write("""
        default:
             /* @fixme Add debug statement */
             return OF_ERROR_PARSE;
        } /* end switch */
        rv = of_list_oxm_next(&oxm_list, &oxm_entry);
    } /* end OXM iteration */

    return OF_ERROR_NONE;
}
""")

def gen_serialize(out):
    out.write("""
/**
 * Serialize a match structure according to the version passed
 * @param version The version to use for serialization protocol
 * @param match Pointer to the structure to serialize
 * @param octets Pointer to an octets object to fill out
 *
 * A buffer is allocated using normal internal ALLOC/FREE semantics
 * and pointed to by the octets object.  The length of the resulting
 * serialization is in octets->bytes.
 *
 * For 1.2 matches, returns the padded serialized structure
 *
 * Note that FREE must be called on octets->data when processing of
 * the object is complete.
 */

int
of_match_serialize(of_version_t version, of_match_t *match, of_octets_t *octets)
{
    int rv;

    switch (version) {
""")
    for version in of_g.of_version_range:
        out.write("""
    case %(ver_name)s:
        {
            of_match_v%(version)s_t *wire_match;
            wire_match = of_match_v%(version)s_new(version);
            if (wire_match == NULL) {
                return OF_ERROR_RESOURCE;
            }
            if ((rv = of_match_to_wire_match_v%(version)s(match, wire_match)) < 0) {
                of_match_v%(version)s_delete(wire_match);
                return rv;
            }
            octets->bytes = OF_MATCH_BYTES(wire_match->length);
            of_object_wire_buffer_steal((of_object_t *)wire_match,
                                        &octets->data);
            of_match_v%(version)s_delete(wire_match);
        }
        break;
""" % dict(version=version, ver_name=of_g.of_version_wire2name[version]))
    out.write("""
    default:
        return OF_ERROR_COMPAT;
    }

    return OF_ERROR_NONE;
}
""")


def gen_deserialize(out):
    out.write("""
/**
 * Deserialize a match structure according to the version passed
 * @param version The version to use for deserialization protocol
 * @param match Pointer to the structure to fill out
 * @param octets Pointer to an octets object holding serial buffer
 *
 * Normally the octets object will point to a part of a wire buffer.
 */

int
of_match_deserialize(of_version_t version, of_match_t *match,
                     of_octets_t *octets)
{
    if (octets->bytes == 0) { /* No match specified means all wildcards */
        MEMSET(match, 0, sizeof(*match));
        match->version = version;

        return OF_ERROR_NONE;
    }

    switch (version) {
""")
    for version in of_g.of_version_range:
        out.write("""
    case %(ver_name)s:
        { /* FIXME: check init bytes */
            uint8_t *tmp;
            of_match_v%(version)d_t wire_match;
            of_match_v%(version)d_init(&wire_match,
                   %(ver_name)s, -1, 1);
            of_object_buffer_bind((of_object_t *)&wire_match,
                octets->data, octets->bytes, NULL);
            OF_TRY(of_match_v%(version)d_to_match(&wire_match, match));

            /* Free the wire buffer control block without freeing
             * octets->bytes. */
            of_wire_buffer_steal(wire_match.wire_object.wbuf, &tmp);
        }
        break;
""" % dict(version=version, ver_name=of_g.of_version_wire2name[version]))

    out.write("""
    default:
        return OF_ERROR_COMPAT;
    }

    return OF_ERROR_NONE;
}
""")

def gen_match_comp(out=sys.stdout):
    """
    Generate match comparison functions
    """
    out.write("""
/**
 * Determine "more specific" relationship between mac addrs
 * @return true if v1 is equal to or more specific than v2
 *
 * @todo Could be optimized
 *
 * Check: Every bit in v2 is set in v1; v1 may have add'l bits set.
 * That is, return false if there is a bit set in v2 and not in v1.
 */

static inline int
of_more_specific_ipv6(of_ipv6_t *v1, of_ipv6_t *v2) {
    int idx;

    for (idx = 0; idx < OF_IPV6_BYTES; idx++) {
        /* If there's a bit set in v2 that is clear in v1, return false */
        if (~v1->addr[idx] & v2->addr[idx]) {
            return 0;
        }
    }

    return 1;
}

/**
 * Boolean test if two values agree when restricted to a mask
 */

static inline int
of_restricted_match_ipv6(of_ipv6_t *v1, of_ipv6_t *v2, of_ipv6_t *mask) {
    int idx;

    for (idx = 0; idx < OF_IPV6_BYTES; idx++) {
        if ((v1->addr[idx] & mask->addr[idx]) !=
               (v2->addr[idx] & mask->addr[idx])) {
            return 0;
        }
    }

    return 1;
}

/**
 * Boolean test if two values "overlap" (agree on common masks)
 */

static inline int
of_overlap_ipv6(of_ipv6_t *v1, of_ipv6_t *v2,
                         of_ipv6_t *m1, of_ipv6_t *m2) {
    int idx;

    for (idx = 0; idx < OF_IPV6_BYTES; idx++) {
        if (((v1->addr[idx] & m1->addr[idx]) & m2->addr[idx]) !=
               ((v2->addr[idx] & m1->addr[idx]) & m2->addr[idx])) {
            return 0;
        }
    }

    return 1;
}

#define OF_MORE_SPECIFIC_IPV6(v1, v2) of_more_specific_ipv6((v1), (v2))

#define OF_RESTRICTED_MATCH_IPV6(v1, v2, mask) \\
    of_restricted_match_ipv6((v1), (v2), (mask))

#define OF_OVERLAP_IPV6(v1, v2, m1, m2) of_overlap_ipv6((v1), (v2), (m1), (m2))

/**
 * Determine "more specific" relationship between mac addrs
 * @return true if v1 is equal to or more specific than v2
 *
 * @todo Could be optimized
 *
 * Check: Every bit in v2 is set in v1; v1 may have add'l bits set.
 * That is, return false if there is a bit set in v2 and not in v1.
 */
static inline int
of_more_specific_mac_addr(of_mac_addr_t *v1, of_mac_addr_t *v2) {
    int idx;

    for (idx = 0; idx < OF_MAC_ADDR_BYTES; idx++) {
        /* If there's a bit set in v2 that is clear in v1, return false */
        if (~v1->addr[idx] & v2->addr[idx]) {
            return 0;
        }
    }

    return 1;
}

/**
 * Boolean test if two values agree when restricted to a mask
 */
static inline int
of_restricted_match_mac_addr(of_mac_addr_t *v1, of_mac_addr_t *v2,
                             of_mac_addr_t *mask) {
    int idx;

    for (idx = 0; idx < OF_MAC_ADDR_BYTES; idx++) {
        if ((v1->addr[idx] & mask->addr[idx]) !=
               (v2->addr[idx] & mask->addr[idx])) {
            return 0;
        }
    }

    return 1;
}

/**
 * Boolean test if two values "overlap" (agree on common masks)
 */

static inline int
of_overlap_mac_addr(of_mac_addr_t *v1, of_mac_addr_t *v2,
                         of_mac_addr_t *m1, of_mac_addr_t *m2) {
    int idx;

    for (idx = 0; idx < OF_MAC_ADDR_BYTES; idx++) {
        if (((v1->addr[idx] & m1->addr[idx]) & m2->addr[idx]) !=
               ((v2->addr[idx] & m1->addr[idx]) & m2->addr[idx])) {
            return 0;
        }
    }

    return 1;
}

#define OF_MORE_SPECIFIC_MAC_ADDR(v1, v2) of_more_specific_mac_addr((v1), (v2))

#define OF_RESTRICTED_MATCH_MAC_ADDR(v1, v2, mask) \\
    of_restricted_match_mac_addr((v1), (v2), (mask))

#define OF_OVERLAP_MAC_ADDR(v1, v2, m1, m2) \\
    of_overlap_mac_addr((v1), (v2), (m1), (m2))

#define OF_MORE_SPECIFIC_BITMAP_128(v1, v2) \\
    (OF_MORE_SPECIFIC_INT((v1)->lo, (v2)->lo) && OF_MORE_SPECIFIC_INT((v1)->hi, (v2)->hi))

#define OF_RESTRICTED_MATCH_BITMAP_128(v1, v2, mask) \\
    (OF_RESTRICTED_MATCH_INT((v1)->lo, (v2)->lo, (mask)->lo) && OF_RESTRICTED_MATCH_INT((v1)->hi, (v2)->hi, (mask)->hi))

#define OF_OVERLAP_BITMAP_128(v1, v2, m1, m2) \\
    (OF_OVERLAP_INT((v1)->lo, (v2)->lo, (m1)->lo, (m2)->lo) && OF_OVERLAP_INT((v1)->hi, (v2)->hi, (m1)->hi, (m2)->hi))

/**
 * More-specific-than macro for integer types; see above
 * @return true if v1 is equal to or more specific than v2
 *
 * If there is a bit that is set in v2 and not in v1, return false.
 */
#define OF_MORE_SPECIFIC_INT(v1, v2) (!(~(v1) & (v2)))

/**
 * Boolean test if two values agree when restricted to a mask
 */
#define OF_RESTRICTED_MATCH_INT(v1, v2, mask) \\
   (((v1) & (mask)) == ((v2) & (mask)))


#define OF_OVERLAP_INT(v1, v2, m1, m2) \\
    ((((v1) & (m1)) & (m2)) == (((v2) & (m1)) & (m2)))
""")

    out.write("""
/**
 * Compare two match structures for exact equality
 *
 * We just do memcmp assuming structs were memset to 0 on init
 */
static inline int
of_match_eq(of_match_t *match1, of_match_t *match2)
{
    return (MEMCMP(match1, match2, sizeof(of_match_t)) == 0);
}

/**
 * Is the entry match more specific than (or equal to) the query match?
 * @param entry Match expected to be more specific (subset of query)
 * @param query Match expected to be less specific (superset of entry)
 * @returns Boolean, see below
 *
 * The assumption is that a query is being done for a non-strict
 * match against an entry in a table.  The result is true if the
 * entry match indicates a more specific (but compatible) flow space
 * specification than that in the query match.  This means that the
 * values agree between the two where they overlap, and that each mask
 * for the entry is more specific than that of the query.
 *
 * The query has the less specific mask (fewer mask bits) so it is
 * used for the mask when checking values.
 */

static inline int
of_match_more_specific(of_match_t *entry, of_match_t *query)
{
    of_match_fields_t *q_m, *e_m;  /* Short hand for masks, fields */
    of_match_fields_t *q_f, *e_f;

    q_m = &query->masks;
    e_m = &entry->masks;
    q_f = &query->fields;
    e_f = &entry->fields;
""")
    for key, entry in match.of_match_members.items():
        q_m = "&q_m->%s" % key
        e_m = "&e_m->%s" % key
        q_f = "&q_f->%s" % key
        e_f = "&e_f->%s" % key
        if entry["m_type"] == "of_ipv6_t":
            comp = "OF_MORE_SPECIFIC_IPV6"
            match_type = "OF_RESTRICTED_MATCH_IPV6"
        elif entry["m_type"] == "of_mac_addr_t":
            comp = "OF_MORE_SPECIFIC_MAC_ADDR"
            match_type = "OF_RESTRICTED_MATCH_MAC_ADDR"
        elif entry["m_type"] == "of_bitmap_128_t":
            comp = "OF_MORE_SPECIFIC_BITMAP_128"
            match_type = "OF_RESTRICTED_MATCH_BITMAP_128"
        else: # Integer
            comp = "OF_MORE_SPECIFIC_INT"
            match_type = "OF_RESTRICTED_MATCH_INT"
            q_m = "q_m->%s" % key
            e_m = "e_m->%s" % key
            q_f = "q_f->%s" % key
            e_f = "e_f->%s" % key
        out.write("""
    /* Mask and values for %(key)s */
    if (!%(comp)s(%(e_m)s, %(q_m)s)) {
        return 0;
    }
    if (!%(match_type)s(%(e_f)s, %(q_f)s,
            %(q_m)s)) {
        return 0;
    }
""" % dict(match_type=match_type, comp=comp, q_f=q_f, e_f=e_f,
           q_m=q_m, e_m=e_m, key=key))

    out.write("""
    return 1;
}
""")

    out.write("""

/**
 * Do two entries overlap?
 * @param match1 One match struct
 * @param match2 Another match struct
 * @returns Boolean: true if there is a packet that would match both
 *
 */

static inline int
of_match_overlap(of_match_t *match1, of_match_t *match2)
{
    of_match_fields_t *m1, *m2;  /* Short hand for masks, fields */
    of_match_fields_t *f1, *f2;

    m1 = &match1->masks;
    m2 = &match2->masks;
    f1 = &match1->fields;
    f2 = &match2->fields;
""")
    for key, entry in match.of_match_members.items():
        m1 = "&m1->%s" % key
        m2 = "&m2->%s" % key
        f1 = "&f1->%s" % key
        f2 = "&f2->%s" % key
        if entry["m_type"] == "of_ipv6_t":
            check = "OF_OVERLAP_IPV6"
        elif entry["m_type"] == "of_mac_addr_t":
            check = "OF_OVERLAP_MAC_ADDR"
        elif entry["m_type"] == "of_bitmap_128_t":
            check = "OF_OVERLAP_BITMAP_128"
        else: # Integer
            check = "OF_OVERLAP_INT"
            m1 = "m1->%s" % key
            m2 = "m2->%s" % key
            f1 = "f1->%s" % key
            f2 = "f2->%s" % key
        out.write("""
    /* Check overlap for %(key)s */
    if (!%(check)s(%(f1)s, %(f2)s,
        %(m2)s, %(m1)s)) {
        return 0; /* This field differentiates; all done */
    }
""" % dict(check=check, f1=f1, f2=f2, m1=m1, m2=m2, key=key))

    out.write("""
    return 1; /* No field differentiates matches */
}
""")

def gen_match_conversions(out=sys.stdout):
    match.match_sanity_check()
    gen_wc_convert_literal(out)
    out.write("""
/**
 * IP Mask map.  IP maks wildcards from OF 1.0 are interpretted as
 * indices into the map below.
 */

int of_ip_mask_map_init_done = 0;
uint32_t of_ip_mask_map[OF_IP_MASK_MAP_COUNT];
void
of_ip_mask_map_init(void)
{
    int idx;

    MEMSET(of_ip_mask_map, 0, sizeof(of_ip_mask_map));
    for (idx = 0; idx < 32; idx++) {
        of_ip_mask_map[idx] = ~((1U << idx) - 1);
    }

    of_ip_mask_map_init_done = 1;
}

/**
 * @brief Set non-default IP mask for given index
 */
int
of_ip_mask_map_set(int index, uint32_t mask)
{
    OF_IP_MASK_INIT_CHECK;

    if ((index < 0) || (index >= OF_IP_MASK_MAP_COUNT)) {
        return OF_ERROR_RANGE;
    }
    of_ip_mask_map[index] = mask;

    return OF_ERROR_NONE;
}

/**
 * @brief Get a non-default IP mask for given index
 */
int
of_ip_mask_map_get(int index, uint32_t *mask)
{
    OF_IP_MASK_INIT_CHECK;

    if ((mask == NULL) || (index < 0) || (index >= OF_IP_MASK_MAP_COUNT)) {
        return OF_ERROR_RANGE;
    }
    *mask = of_ip_mask_map[index];

    return OF_ERROR_NONE;
}

/**
 * @brief Return the index (used as the WC field in 1.0 match) given the mask
 */

int
of_ip_mask_to_index(uint32_t mask)
{
    int idx;

    OF_IP_MASK_INIT_CHECK;

    /* Handle most common cases directly */
    if ((mask == 0) && (of_ip_mask_map[63] == 0)) {
        return 63;
    }
    if ((mask == 0xffffffff) && (of_ip_mask_map[0] == 0xffffffff)) {
        return 0;
    }

    for (idx = 0; idx < OF_IP_MASK_MAP_COUNT; idx++) {
        if (mask == of_ip_mask_map[idx]) {
            return idx;
        }
    }

    LOCI_LOG_INFO("OF 1.0: Could not map IP addr mask 0x%x", mask);
    return 0x3f;
}

/**
 * @brief Return the mask for the given index
 */

uint32_t
of_ip_index_to_mask(int index)
{
    OF_IP_MASK_INIT_CHECK;

    if (index >= OF_IP_MASK_MAP_COUNT) {
        LOCI_LOG_INFO("IP index to map: bad index %d", index);
        return 0;
    }

    return of_ip_mask_map[index];
}

""")

    gen_unified_match_to_v1(out)
    gen_unified_match_to_v2(out)
    gen_unified_match_to_v3(out)
    gen_v1_to_unified_match(out)
    gen_v2_to_unified_match(out)
    gen_v3_to_unified_match(out)
    return
