# Generated by h2py from ./h/linux/genetlink.h

from __future__ import absolute_import

GENL_NAMSIZ = 16
# H2PY_ERR: ./h/linux/genetlink.h - define: GENL_MIN_ID = NLMSG_MIN_TYPE
GENL_MAX_ID = 1023
# H2PY_ERR: ./h/linux/genetlink.h - define: GENL_HDRLEN = NLMSG_ALIGN(sizeof(struct genlmsghdr))
GENL_ADMIN_PERM = 0x01
GENL_CMD_CAP_DO = 0x02
GENL_CMD_CAP_DUMP = 0x04
GENL_CMD_CAP_HASPOL = 0x08
GENL_ID_GENERATE = 0
# H2PY_ERR: ./h/linux/genetlink.h - define: GENL_ID_CTRL = NLMSG_MIN_TYPE
CTRL_CMD_UNSPEC = 0
CTRL_CMD_NEWFAMILY = 1
CTRL_CMD_DELFAMILY = 2
CTRL_CMD_GETFAMILY = 3
CTRL_CMD_NEWOPS = 4
CTRL_CMD_DELOPS = 5
CTRL_CMD_GETOPS = 6
CTRL_CMD_NEWMCAST_GRP = 7
CTRL_CMD_DELMCAST_GRP = 8
CTRL_CMD_GETMCAST_GRP = 9
__CTRL_CMD_MAX = 10
CTRL_CMD_MAX = (__CTRL_CMD_MAX - 1)
CTRL_ATTR_UNSPEC = 0
CTRL_ATTR_FAMILY_ID = 1
CTRL_ATTR_FAMILY_NAME = 2
CTRL_ATTR_VERSION = 3
CTRL_ATTR_HDRSIZE = 4
CTRL_ATTR_MAXATTR = 5
CTRL_ATTR_OPS = 6
CTRL_ATTR_MCAST_GROUPS = 7
__CTRL_ATTR_MAX = 8
CTRL_ATTR_MAX = (__CTRL_ATTR_MAX - 1)
CTRL_ATTR_OP_UNSPEC = 0
CTRL_ATTR_OP_ID = 1
CTRL_ATTR_OP_FLAGS = 2
__CTRL_ATTR_OP_MAX = 3
CTRL_ATTR_OP_MAX = (__CTRL_ATTR_OP_MAX - 1)
CTRL_ATTR_MCAST_GRP_UNSPEC = 0
CTRL_ATTR_MCAST_GRP_NAME = 1
CTRL_ATTR_MCAST_GRP_ID = 2
__CTRL_ATTR_MCAST_GRP_MAX = 3
CTRL_ATTR_MCAST_GRP_MAX = (__CTRL_ATTR_MCAST_GRP_MAX - 1)
