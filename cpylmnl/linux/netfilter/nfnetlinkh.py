# -*- coding: utf-8 -*-

from ctypes import *
import cpylmnl.linux.netlinkh as netlink
from cpylmnl.nlstruct import NLStructure
try:
    from enum import Enum
except ImportError:
    Enum = object


class NfnetlinkGroups(Enum):
    NFNLGRP_NONE			= 0
    NFNLGRP_CONNTRACK_NEW		= 1
    NFNLGRP_CONNTRACK_UPDATE		= 2
    NFNLGRP_CONNTRACK_DESTROY		= 3
    NFNLGRP_CONNTRACK_EXP_NEW		= 4
    NFNLGRP_CONNTRACK_EXP_UPDATE	= 5
    NFNLGRP_CONNTRACK_EXP_DESTROY	= 6
    NFNLGRP_NFTABLES			= 7
    __NFNLGRP_MAX			= 8
    NFNLGRP_MAX				= (__NFNLGRP_MAX - 1)
NFNLGRP_NONE			= 0
NFNLGRP_CONNTRACK_NEW		= 1
NFNLGRP_CONNTRACK_UPDATE	= 2
NFNLGRP_CONNTRACK_DESTROY	= 3
NFNLGRP_CONNTRACK_EXP_NEW	= 4
NFNLGRP_CONNTRACK_EXP_UPDATE	= 5
NFNLGRP_CONNTRACK_EXP_DESTROY	= 6
NFNLGRP_NFTABLES		= 7
__NFNLGRP_MAX			= 8
NFNLGRP_MAX			= (__NFNLGRP_MAX - 1)

# General form of address family dependent message.
class Nfgenmsg(NLStructure):
    """struct nfgenmsg
    """
    _fields_ = [("family",	c_uint8),  # __u8   nfgen_family /* AF_xxx */
                ("version",	c_uint8),  # __u8   version      /* nfnetlink version */
                ("res_id",	c_uint16)] # __be16 res_id       /* resource id */

NFNETLINK_V0 = 0

# netfilter netlink message types are split in two pieces:
# 8 bit subsystem, 8bit operation.
#define NFNL_SUBSYS_ID(x)	((x & 0xff00) >> 8)
def NFNL_SUBSYS_ID(x):		return ((x & 0xff00) >> 8)
#define NFNL_MSG_TYPE(x)	(x & 0x00ff)
def NFNL_MSG_TYPE(x):		return (x & 0x00ff)

# No enum here, otherwise __stringify() trick of MODULE_ALIAS_NFNL_SUBSYS()
# won't work anymore
NFNL_SUBSYS_NONE			= 0
NFNL_SUBSYS_CTNETLINK			= 1
NFNL_SUBSYS_CTNETLINK_EXP		= 2
NFNL_SUBSYS_QUEUE			= 3
NFNL_SUBSYS_ULOG			= 4
NFNL_SUBSYS_OSF				= 5
NFNL_SUBSYS_IPSET			= 6
NFNL_SUBSYS_ACCT			= 7
NFNL_SUBSYS_CTNETLINK_TIMEOUT		= 8
NFNL_SUBSYS_CTHELPER			= 9
NFNL_SUBSYS_NFTABLES			= 10
NFNL_SUBSYS_NFT_COMPAT			= 11
NFNL_SUBSYS_COUNT			= 12

# Reserved control nfnetlink messages
#define NFNL_MSG_BATCH_BEGIN		NLMSG_MIN_TYPE
NFNL_MSG_BATCH_BEGIN			= netlink.NLMSG_MIN_TYPE
#define NFNL_MSG_BATCH_END		NLMSG_MIN_TYPE+1
NFNL_MSG_BATCH_END			= netlink.NLMSG_MIN_TYPE + 1
