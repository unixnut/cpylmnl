# -*- coding: utf-8 -*-

from ctypes import *
from cpylmnl.nlstruct import NLStructure
import cpylmnl.linux.netlinkh as netlink
try:
    from enum import Enum
except ImportError:
    Enum = object


# rtnetlink families. Values up to 127 are reserved for real address
# families, values above 128 may be used arbitrarily.
RTNL_FAMILY_IPMR		= 128
RTNL_FAMILY_IP6MR		= 129
RTNL_FAMILY_MAX			= 129


# Routing/neighbour discovery messages.
# Types of messages
# enum
RTM_BASE 		= 16
RTM_NEWLINK		= 16
RTM_DELLINK		= 17
RTM_GETLINK		= 18
RTM_SETLINK		= 19
RTM_NEWADDR		= 20
RTM_DELADDR		= 21
RTM_GETADDR		= 22
RTM_NEWROUTE		= 24
RTM_DELROUTE		= 25
RTM_GETROUTE		= 26
RTM_NEWNEIGH		= 28
RTM_DELNEIGH		= 29
RTM_GETNEIGH		= 30
RTM_NEWRULE		= 32
RTM_DELRULE		= 33
RTM_GETRULE		= 34
RTM_NEWQDISC		= 36
RTM_DELQDISC		= 37
RTM_GETQDISC		= 38
RTM_NEWTCLASS		= 40
RTM_DELTCLASS		= 41
RTM_GETTCLASS		= 42
RTM_NEWTFILTER		= 44
RTM_DELTFILTER		= 45
RTM_GETTFILTER		= 46
RTM_NEWACTION		= 48
RTM_DELACTION		= 49
RTM_GETACTION		= 50
RTM_NEWPREFIX		= 52
RTM_GETMULTICAST	= 58
RTM_GETANYCAST		= 62
RTM_NEWNEIGHTBL		= 64
RTM_GETNEIGHTBL		= 66
RTM_SETNEIGHTBL		= 67
RTM_NEWNDUSEROPT	= 68
RTM_NEWADDRLABEL	= 72
RTM_DELADDRLABEL	= 73
RTM_GETADDRLABEL	= 74
RTM_GETDCB		= 78
RTM_SETDCB		= 79
RTM_NEWNETCONF		= 80
RTM_GETNETCONF		= 82
RTM_NEWMDB		= 84
RTM_DELMDB		= 85
RTM_GETMDB		= 86
__RTM_MAX		= 87
RTM_MAX			= (((__RTM_MAX + 3) & ~3) - 1)

RTM_NR_MSGTYPES = (RTM_MAX + 1 - RTM_BASE)
RTM_NR_FAMILIES = (RTM_NR_MSGTYPES >> 2)
#define RTM_FAM(cmd)	(((cmd) - RTM_BASE) >> 2)
def RTM_FAM(cmd):	return (cmd - RTM_BASE) >> 2


# Generic structure for encapsulation of optional route information.
# It is reminiscent of sockaddr, but with sa_family replaced
# with attribute type.
class Rtattr(NLStructure):
    """struct rtattr
    """
    _fields_ = [("len", 	c_ushort),  # unsigned short	rta_len
                ("type", 	c_ushort)]  # unsigned short	rta_type

### Macros to handle rtattributes
RTA_ALIGNTO	= 4
#define RTA_ALIGN(len) ( ((len)+RTA_ALIGNTO-1) & ~(RTA_ALIGNTO-1) )w
def RTA_ALIGN(sz):	return ((sz)+RTA_ALIGNTO-1) & ~(RTA_ALIGNTO-1)
#define RTA_OK(rta,len) ((len) >= (int)sizeof(struct rtattr) && \
#			 (rta)->rta_len >= sizeof(struct rtattr) && \
#			 (rta)->rta_len <= (len))
def RTA_OK(rta, sz):	return (sz >= sizeof(Rtattr) and
                                rta.len >= sizeof(Rtattr) and
                                rta.len <= sz)
#define RTA_NEXT(rta,attrlen)	((attrlen) -= RTA_ALIGN((rta)->rta_len), \
#				 (struct rtattr*)(((char*)(rta)) + RTA_ALIGN((rta)->rta_len)))
def RTA_NEXT(rta, attrlen): return Rtattr.pointer(addressof(rta) + RTA_ALIGN(rta.len)), attrlen - RTA_ALIGN(rta.len)
#define RTA_LENGTH(len)	(RTA_ALIGN(sizeof(struct rtattr)) + (len))
def RTA_LENGTH(len):	return RTA_ALIGN(sizeof(Rtattr) + len)
#define RTA_SPACE(len)	RTA_ALIGN(RTA_LENGTH(len))
def RTA_SPACE(len):	return RTA_ALIGN(RTA_LENGTH(len))
#define RTA_DATA(rta)   ((void*)(((char*)(rta)) + RTA_LENGTH(0)))
def RTA_DATA(rta):	return cast(addressof(rta) + RTA_LENGTH(0), POINTER(c_ubyte * (rta.len - RTA_LENGTH))).contents
#define RTA_PAYLOAD(rta) ((int)((rta)->rta_len) - RTA_LENGTH(0))
def RTA_PAYLOAD(rta):	return rta.len - RTA_LENGTH(0)


# Definitions used in routing table administration.
class Rtmsg(NLStructure):
    """struct rtmsg
    """
    _fields_ = [("family", 	c_ubyte), # unsigned char rtm_family                                   
                ("dst_len", 	c_ubyte), # unsigned char rtm_dst_len                                  
                ("src_len", 	c_ubyte), # unsigned char rtm_src_len                                  
                ("tos", 	c_ubyte), # unsigned char rtm_tos                                      
                ("table", 	c_ubyte), # unsigned char rtm_table - Routing table id                 
                ("protocol", 	c_ubyte), # unsigned char rtm_protocol - Routing protocol; see below   
                ("scope", 	c_ubyte), # unsigned char rtm_scope - See below                        
                ("type", 	c_ubyte), # unsigned char rtm_type - See below                         
                ("flags", 	c_uint)]  # unsigned	  rtm_flags

# rtm_type
# enum
RTN_UNSPEC		= 0
RTN_UNICAST		= 1  # Gateway or direct route	
RTN_LOCAL		= 2  # Accept locally		
RTN_BROADCAST		= 3  # Accept locally as broadcast,
			     # send as broadcast 
RTN_ANYCAST		= 4  # Accept locally as broadcast,
			     # but send as unicast 
RTN_MULTICAST		= 5  # Multicast route		
RTN_BLACKHOLE		= 6  # Drop				
RTN_UNREACHABLE		= 7  # Destination is unreachable   
RTN_PROHIBIT		= 8  # Administratively prohibited	
RTN_THROW		= 9  # Not in this table		
RTN_NAT			= 10 # Translate this address	
RTN_XRESOLVE		= 11 # Use external resolver	
__RTN_MAX		= 12
RTN_MAX			= (__RTN_MAX - 1)

# rtm_protocol 
RTPROT_UNSPEC	= 0
RTPROT_REDIRECT	= 1	# Route installed by ICMP redirects;
			# not used by current IPv4 
RTPROT_KERNEL	= 2	# Route installed by kernel		
RTPROT_BOOT	= 3	# Route installed during boot		
RTPROT_STATIC	= 4	# Route installed by administrator	

# Values of protocol >= RTPROT_STATIC are not interpreted by kernel;
# they are just passed from user and back as is.
# It will be used by hypothetical multiple routing daemons.
# Note that protocol values should be standardized in order to
# avoid conflicts.
RTPROT_GATED	= 8	# Apparently, GateD 
RTPROT_RA	= 9	# RDISC/ND router advertisements 
RTPROT_MRT	= 10	# Merit MRT 
RTPROT_ZEBRA	= 11	# Zebra 
RTPROT_BIRD	= 12	# BIRD 
RTPROT_DNROUTED	= 13	# DECnet routing daemon 
RTPROT_XORP	= 14	# XORP 
RTPROT_NTK	= 15	# Netsukuku 
RTPROT_DHCP	= 16	# DHCP client 
RTPROT_MROUTED	= 17	# Multicast daemon 

# rtm_scope
# Really it is not scope, but sort of distance to the destination.
# NOWHERE are reserved for not existing destinations, HOST is our
# local addresses, LINK are destinations, located on directly attached
# link and UNIVERSE is everywhere in the Universe.
#
# Intermediate values are also possible f.e. interior routes
# could be assigned a value between UNIVERSE and LINK.

# enum rt_scope_t
class RtScopeT(Enum):
	RT_SCOPE_UNIVERSE	= 0
	# User defined values  
	RT_SCOPE_SITE		= 200
	RT_SCOPE_LINK		= 253
	RT_SCOPE_HOST		= 254
	RT_SCOPE_NOWHERE	= 255
RT_SCOPE_UNIVERSE	= 0
RT_SCOPE_SITE		= 200
RT_SCOPE_LINK		= 253
RT_SCOPE_HOST		= 254
RT_SCOPE_NOWHERE	= 255

# rtm_flags 
RTM_F_NOTIFY		= 0x100	# Notify user of route change	
RTM_F_CLONED		= 0x200	# This route is cloned		
RTM_F_EQUALIZE		= 0x400	# Multipath equalizer: NI	
RTM_F_PREFIX		= 0x800	# Prefix addresses		

# Reserved table identifiers 
# enum rt_class_t
class RtClassT(Enum):
	RT_TABLE_UNSPEC		= 0
	# User defined values 
	RT_TABLE_COMPAT		= 252
	RT_TABLE_DEFAULT	= 253
	RT_TABLE_MAIN		= 254
	RT_TABLE_LOCAL		= 255
	RT_TABLE_MAX		= 0xFFFFFFFF
RT_TABLE_UNSPEC		= 0
RT_TABLE_COMPAT		= 252
RT_TABLE_DEFAULT	= 253
RT_TABLE_MAIN		= 254
RT_TABLE_LOCAL		= 255
RT_TABLE_MAX		= 0xFFFFFFFF

# Routing message attributes 
# enum rtattr_type_t
class RtattrTypeT(Enum):
	RTA_UNSPEC	= 0
	RTA_DST		= 1
	RTA_SRC		= 2
	RTA_IIF		= 3
	RTA_OIF		= 4
	RTA_GATEWAY	= 5
	RTA_PRIORITY	= 6
	RTA_PREFSRC	= 7
	RTA_METRICS	= 8
	RTA_MULTIPATH	= 9
	RTA_PROTOINFO	= 10 # no longer used 
	RTA_FLOW	= 11
	RTA_CACHEINFO	= 12
	RTA_SESSION	= 13 # no longer used 
	RTA_MP_ALGO	= 14 # no longer used 
	RTA_TABLE	= 15
	RTA_MARK	= 16
	RTA_MFC_STATS	= 17
	__RTA_MAX	= 18
	RTA_MAX		= (__RTA_MAX - 1)
RTA_UNSPEC	= 0
RTA_DST		= 1
RTA_SRC		= 2
RTA_IIF		= 3
RTA_OIF		= 4
RTA_GATEWAY	= 5
RTA_PRIORITY	= 6
RTA_PREFSRC	= 7
RTA_METRICS	= 8
RTA_MULTIPATH	= 9
RTA_PROTOINFO	= 10
RTA_FLOW	= 11
RTA_CACHEINFO	= 12
RTA_SESSION	= 13
RTA_MP_ALGO	= 14
RTA_TABLE	= 15
RTA_MARK	= 16
RTA_MFC_STATS	= 17
__RTA_MAX	= 18
RTA_MAX		= (__RTA_MAX - 1)

#define RTM_RTA(r)  ((struct rtattr*)(((char*)(r)) + NLMSG_ALIGN(sizeof(struct rtmsg))))
def RTM_RTA(r):		return Rtattr.pointer(addressof(r) + netlink.NLMSG_ALIGN(sizeof(Rtmsg)))
#define RTM_PAYLOAD(n) NLMSG_PAYLOAD(n,sizeof(struct rtmsg))
def RTM_PAYLOAD(n):	return netlink.NLMSG_PAYLOAD(n, sizeof(Rtmsg))


# RTM_MULTIPATH --- array of struct rtnexthop.
# 
# struct rtnexthop" describes all necessary nexthop information,
# i.e. parameters of path to a destination via this nexthop.
# 
# At the moment it is impossible to set different prefsrc, mtu, window
# and rtt for different paths from multipath.
class Rtnexthop(NLStructure):
    """struct rtnexthop
    """
    _fields_ = [("len",		c_ushort), # unsigned short		rtnh_len
                ("flags", 	c_ubyte),  # unsigned char		rtnh_flags
                ("hops", 	c_ubyte),  # unsigned char		rtnh_hops
                ("ifindex", 	c_int)]    # int			rtnh_ifindex
 
# rtnh_flags 
RTNH_F_DEAD		= 1	# Nexthop is dead (used by multipath)	
RTNH_F_PERVASIVE	= 2	# Do recursive gateway lookup	
RTNH_F_ONLINK		= 4	# Gateway is forced on link	

# Macros to handle hexthops 
RTNLH_ALIGNTO	= 4
#define RTNH_ALIGN(len) ( ((len)+RTNH_ALIGNTO-1) & ~(RTNH_ALIGNTO-1) )
def RTNL_ALIGN(len):	return (len + RTNH_ALIGNTO - 1) & ~(RTNH_ALIGNTO - 1)
#define RTNH_OK(rtnh,len) ((rtnh)->rtnh_len >= sizeof(struct rtnexthop) && \
#			   ((int)(rtnh)->rtnh_len) <= (len))
def RTNH_OK(rtnh, len):	return (rtnh.len >= sizeof(Rtnexthop) and
                                rtnh.len <= len)
#define RTNH_NEXT(rtnh)	((struct rtnexthop*)(((char*)(rtnh)) + RTNH_ALIGN((rtnh)->rtnh_len)))
def RTNH_NEXT(rtnh):	return Rtnexthop.pointer(addressof(rtnh) + RTNL_ALIGN(rtnh.len))
#define RTNH_LENGTH(len) (RTNH_ALIGN(sizeof(struct rtnexthop)) + (len))
def RTNH_LENGTH(len):	return RTNL_ALIGN(sizeof(Rtnexthop)) + len
#define RTNH_SPACE(len)	RTNH_ALIGN(RTNH_LENGTH(len))
def RTNH_SPACE(len):	return RTNH_ALIGN(RTNH_LENGTH(len))
#define RTNH_DATA(rtnh)   ((struct rtattr*)(((char*)(rtnh)) + RTNH_LENGTH(0)))
def RTNH_DATA(rtnh):	return Rtattr(addressof(rtnh) + RTNH_LENGTH(0))


# RTM_CACHEINFO
class RtaCacheinfo(Structure):
    """struct rta_cacheinfo
    """
    _fields_ = [("clntref",	c_uint32), # __u32	rta_clntref
                ("lastuse",	c_uint32), # __u32	rta_lastuse
                ("expires",	c_uint32), # __s32	rta_expires
                ("error", 	c_uint32), # __u32	rta_error
                ("used",	c_uint32), # __u32	rta_used
                #? define RTNETLINK_HAVE_PEERINFO 1
                ("id",		c_uint32), # __u32	rta_id
                ("ts",		c_uint32), # __u32	rta_ts
                ("tsage",	c_uint32)] # __u32	rta_tsage

RTNETLINK_HAVE_PEERINFO = 1

# RTM_METRICS --- array of struct rtattr with types of RTAX_* 
# enum
RTAX_UNSPEC	= 0
RTAX_LOCK	= 1
RTAX_MTU	= 2
RTAX_WINDOW	= 3
RTAX_RTT	= 4
RTAX_RTTVAR	= 5
RTAX_SSTHRESH	= 6
RTAX_CWND	= 7
RTAX_ADVMSS	= 8
RTAX_REORDERING	= 9
RTAX_HOPLIMIT	= 10
RTAX_INITCWND	= 11
RTAX_FEATURES	= 12
RTAX_RTO_MIN	= 13
RTAX_INITRWND	= 14
RTAX_QUICKACK	= 15
__RTAX_MAX	= 16
RTAX_MAX	= (__RTAX_MAX - 1)

RTAX_FEATURE_ECN	= 0x00000001
RTAX_FEATURE_SACK	= 0x00000002
RTAX_FEATURE_TIMESTAMP	= 0x00000004
RTAX_FEATURE_ALLFRAG	= 0x00000008


"""
struct rta_session
	__u8	proto
	__u8	pad1
	__u16	pad2

	union
		struct
			__u16	sport
			__u16	dport
		} ports

		struct
			__u8	type
			__u8	code
			__u16	ident
		} icmpt

		__u32		spi
	} u

struct rta_mfc_stats
	__u64	mfcs_packets
	__u64	mfcs_bytes
	__u64	mfcs_wrong_if
"""

# General form of address family dependent message.
class Rtgenmsg(NLStructure):
    """struct rtgenmsg
    """
    _fields_ = [("family",	c_ubyte)] # unsigned char		rtgen_family


# Link layer specific messages.
#
# struct ifinfomsg
# passes link level specific information, not dependent
# on network protocol.
class Ifinfomsg(NLStructure):
    """struct ifinfomsg
    """
    _fields_ = [("family",	c_ubyte),  # unsigned char  ifi_family
                ("_pad",	c_ubyte),  # unsigned char   __ifi_pad
                ("type",	c_ushort), # unsigned short ifi_type   /* ARPHRD_* */
                ("index",	c_int),    # int            ifi_index  /* Link index	*/
                ("flags",	c_uint),   # unsigned	    ifi_flags  /* IFF_* flags	*/
                ("change",	c_uint)]   # unsigned	    ifi_change /* IFF_* change mask */


# prefix information 
class Prefixmsg(Structure):
    """struct prefixmsg
    """
    _fields_ = [("family", 	c_ubyte),  # unsigned char	prefix_family
                ("pad1",	c_ubyte),  # unsigned char	prefix_pad1
                ("pad2", 	c_ushort), # unsigned short	prefix_pad2
                ("ifindex", 	c_int),	   # int		prefix_ifindex
                ("type", 	c_ubyte),  # unsigned char	prefix_type
                ("len",		c_ubyte),  # unsigned char	prefix_len
                ("flags", 	c_ubyte),  # unsigned char	prefix_flags
                ("pad3", 	c_ubyte)]  # unsigned char	prefix_pad3

# enum 
PREFIX_UNSPEC		= 0
PREFIX_ADDRESS		= 1
PREFIX_CACHEINFO	= 2
__PREFIX_MAX		= 3
PREFIX_MAX		= (__PREFIX_MAX - 1)

class PrefixCacheinfo(Structure):
    """struct prefix_cacheinfo
    """
    _fields_ = [("preferred_time",	c_uint32), # __u32	preferred_time
                ("valid_time", 		c_uint32)] # __u32	valid_time


# Traffic control messages.
class Tcmsg(Structure):
    """struct tcmsg
    """
    _fields_ = [("family",	c_ubyte),  # unsigned char	tcm_family
                ("__pad1",	c_ubyte),  # unsigned char	tcm__pad1
                ("__pad2", 	c_ushort), # unsigned short	tcm__pad2
                ("ifindex",	c_int),    # int		tcm_ifindex
                ("handle", 	c_uint32), # __u32		tcm_handle
                ("parent", 	c_uint32), # __u32		tcm_parent
                ("info",	c_uint32)] # __u32		tcm_info

# enum
TCA_UNSPEC	= 0
TCA_KIND	= 1
TCA_OPTIONS	= 2
TCA_STATS	= 3
TCA_XSTATS	= 4
TCA_RATE	= 5
TCA_FCNT	= 6
TCA_STATS2	= 7
TCA_STAB	= 8
__TCA_MAX	= 9
TCA_MAX		= (__TCA_MAX - 1)

#define TCA_RTA(r)  ((struct rtattr*)(((char*)(r)) + NLMSG_ALIGN(sizeof(struct tcmsg))))
def TCA_RTA(r):		return Rtattr.pointer(addressof(r) + netlink.NLMSG_ALIGN(sizeof(Tcmsg)))
#define TCA_PAYLOAD(n) NLMSG_PAYLOAD(n,sizeof(struct tcmsg))
def TCA_PAYLOAD(n):	return netlink.NLMSG_PAYLOAD(n, sizeof(Tcmsg))


# Neighbor Discovery userland options
class Nduseroptmsg(Structure):
    """Neighbor Discovery userland options
    struct nduseroptmsg
    """
    _fields_ = [("family",	c_ubyte),  # unsigned char	nduseropt_family
                ("pad1",	c_ubyte),  # unsigned char	nduseropt_pad1
                ("opts_len",	c_ushort), # unsigned short	nduseropt_opts_len	# Total length of options
                ("ifindex",	c_int),    # int		nduseropt_ifindex
                ("icmp_type",	c_uint8),  # __u8		nduseropt_icmp_type
                ("icmp_code",	c_uint8),  # __u8		nduseropt_icmp_code
                ("pad2",	c_ushort), # unsigned short	nduseropt_pad2
                ("pad3",	c_uint)]   # unsigned int	nduseropt_pad3
    # Followed by one or more ND options 

# enum
NDUSEROPT_UNSPEC	= 0
NDUSEROPT_SRCADDR	= 1
__NDUSEROPT_MAX		= 2
NDUSEROPT_MAX		= (__NDUSEROPT_MAX - 1)


# RTnetlink multicast groups - backwards compatibility for userspace 
RTMGRP_LINK		= 1
RTMGRP_NOTIFY		= 2
RTMGRP_NEIGH		= 4
RTMGRP_TC		= 8

RTMGRP_IPV4_IFADDR	= 0x10
RTMGRP_IPV4_MROUTE	= 0x20
RTMGRP_IPV4_ROUTE	= 0x40
RTMGRP_IPV4_RULE	= 0x80

RTMGRP_IPV6_IFADDR	= 0x100
RTMGRP_IPV6_MROUTE	= 0x200
RTMGRP_IPV6_ROUTE	= 0x400
RTMGRP_IPV6_IFINFO	= 0x800

RTMGRP_DECnet_IFADDR    = 0x1000
RTMGRP_DECnet_ROUTE     = 0x4000

RTMGRP_IPV6_PREFIX	= 0x20000


# RTnetlink multicast groups 
# enum rtnetlink_groups
class RtnetlinkGroups(Enum):
	RTNLGRP_NONE		= 0
	RTNLGRP_LINK		= 1
	RTNLGRP_NOTIFY		= 2
	RTNLGRP_NEIGH		= 3
	RTNLGRP_TC		= 4
	RTNLGRP_IPV4_IFADDR	= 5
	RTNLGRP_IPV4_MROUTE	= 6
	RTNLGRP_IPV4_ROUTE	= 7
	RTNLGRP_IPV4_RULE	= 8
	RTNLGRP_IPV6_IFADDR	= 9
	RTNLGRP_IPV6_MROUTE	= 10
	RTNLGRP_IPV6_ROUTE	= 11
	RTNLGRP_IPV6_IFINFO	= 12
	RTNLGRP_DECnet_IFADDR	= 13
	RTNLGRP_NOP2		= 14
	RTNLGRP_DECnet_ROUTE	= 15
	RTNLGRP_DECnet_RULE	= 16
	RTNLGRP_NOP4		= 17
	RTNLGRP_IPV6_PREFIX	= 18
	RTNLGRP_IPV6_RULE	= 19
	RTNLGRP_ND_USEROPT	= 20
	RTNLGRP_PHONET_IFADDR	= 21
	RTNLGRP_PHONET_ROUTE	= 22
	RTNLGRP_DCB		= 23
	RTNLGRP_IPV4_NETCONF	= 24
	RTNLGRP_IPV6_NETCONF	= 25
	RTNLGRP_MDB		= 26
	__RTNLGRP_MAX		= 27
	RTNLGRP_MAX		= (__RTNLGRP_MAX - 1)
RTNLGRP_NONE		= 0
RTNLGRP_LINK		= 1
RTNLGRP_NOTIFY		= 2
RTNLGRP_NEIGH		= 3
RTNLGRP_TC		= 4
RTNLGRP_IPV4_IFADDR	= 5
RTNLGRP_IPV4_MROUTE	= 6
RTNLGRP_IPV4_ROUTE	= 7
RTNLGRP_IPV4_RULE	= 8
RTNLGRP_IPV6_IFADDR	= 9
RTNLGRP_IPV6_MROUTE	= 10
RTNLGRP_IPV6_ROUTE	= 11
RTNLGRP_IPV6_IFINFO	= 12
RTNLGRP_DECnet_IFADDR	= 13
RTNLGRP_NOP2		= 14
RTNLGRP_DECnet_ROUTE	= 15
RTNLGRP_DECnet_RULE	= 16
RTNLGRP_NOP4		= 17
RTNLGRP_IPV6_PREFIX	= 18
RTNLGRP_IPV6_RULE	= 19
RTNLGRP_ND_USEROPT	= 20
RTNLGRP_PHONET_IFADDR	= 21
RTNLGRP_PHONET_ROUTE	= 22
RTNLGRP_DCB		= 23
RTNLGRP_IPV4_NETCONF	= 24
RTNLGRP_IPV6_NETCONF	= 25
RTNLGRP_MDB		= 26
__RTNLGRP_MAX		= 27
RTNLGRP_MAX		= (__RTNLGRP_MAX - 1)


# TC action piece
class Tcamsg(Structure):
    """struct tcamsg
    """
    _fields_ = [("family",	c_ubyte),  # unsigned char	tca_family
                ("_pad1",	c_ubyte),  # unsigned char	tca__pad1
                ("_pad2",	c_ushort)] # unsigned short	tca__pad2

#define TA_RTA(r)  ((struct rtattr*)(((char*)(r)) + NLMSG_ALIGN(sizeof(struct tcamsg))))
def TA_RTA(r):		return Rtattr.pointer(addressof(r) + netlink.NLMSG_ALIGN(sizeof(Tcamsg)))
#define TA_PAYLOAD(n) NLMSG_PAYLOAD(n,sizeof(struct tcamsg))
def TA_PAYLOAD(n):	return netlink.NLMSG_PAYLOAD(n, sizeof(Tcamsg))

TCA_ACT_TAB 	= 1 # attr type must be >=1 	
TCAA_MAX	= 1

# New extended info filters for IFLA_EXT_MASK 
RTEXT_FILTER_VF		= (1 << 0)
RTEXT_FILTER_BRVLAN	= (1 << 1)