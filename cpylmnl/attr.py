# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function

import sys, os, errno
from ctypes import *

from . import netlink
from .cproto import *
from .mnlh import *

"""
libmnl (http://www.netfilter.org/projects/libmnl/) attr.c
    implementation by python ctypes
"""

### get type of netlink attribute
# uint16_t mnl_attr_get_type(const struct nlattr *attr)
attr_get_type		= c_attr_get_type

### get length of netlink attribute
# uint16_t mnl_attr_get_len(const struct nlattr *attr)
attr_get_len		= c_attr_get_len

### get the attribute payload-value length
# uint16_t mnl_attr_get_payload_len(const struct nlattr *attr)
attr_get_payload_len	= c_attr_get_payload_len

### get pointer to the attribute payload
# void *mnl_attr_get_payload(const struct nlattr *attr)
attr_get_payload	= c_attr_get_payload
def attr_get_payload_v(attr):
    return cast(c_attr_get_payload(attr),
                POINTER(c_ubyte * (attr.len - MNL_ATTR_HDRLEN))).contents
def attr_get_payload_as(attr, cls):
    return cast(c_attr_get_payload(attr), POINTER(cls)).contents

### check if there is room for an attribute in a buffer
# bool mnl_attr_ok(const struct nlattr *attr, int len)
attr_ok			= c_attr_ok

### get the next attribute in the payload of a netlink message
# struct nlattr *mnl_attr_next(const struct nlattr *attr)
def attr_next(attr):
    return c_attr_next(attr).contents

### check if the attribute type is valid
# int mnl_attr_type_valid(const struct nlattr *attr, uint16_t max)
def attr_type_valid(attr, maxtype):
    set_errno(0)
    ret = c_attr_type_valid(attr, maxtype)
    if ret < 0: c_raise_if_errno()
    return ret

### validate netlink attribute (simplified version)
# int mnl_attr_validate(const struct nlattr *attr, enum mnl_attr_data_type type)
def attr_validate(attr, data_type):
    set_errno(0)
    ret = c_attr_validate(attr, data_type)
    if ret < 0: c_raise_if_errno()
    return ret

### validate netlink attribute (extended version)
# int
# mnl_attr_validate2(const struct nlattr *attr, enum mnl_attr_data_type type,
#                    size_t exp_len)
def attr_validate2(attr, data_type, exp_len):
    set_errno(0)
    ret = c_attr_validate2(attr, data_type, exp_len)
    if ret < 0: c_raise_if_errno()
    return ret

### parse attributes
# int
# mnl_attr_parse(const struct nlmsghdr *nlh, unsigned int offset,
#                mnl_attr_cb_t cb, void *data)
def attr_parse(nlh, offset, cb, data):
    set_errno(0)
    ret = c_attr_parse(nlh, offset, cb, data)
    if ret < 0: c_raise_if_errno()
    return ret

### parse attributes inside a nest
# int
# mnl_attr_parse_nested(const struct nlattr *nested,
#                       mnl_attr_cb_t cb, void *data)
def attr_parse_nested(attr, cb, data):
    set_errno(0)
    ret = c_attr_parse_nested(attr, cb, data)
    if ret < 0: c_raise_if_errno()
    return ret

### parse attributes in payload of Netlink message
# int mnl_attr_parse_payload(const void *payload, size_t payload_len,
# 	                     mnl_attr_cb_t cb, void *data)
def attr_parse_payload(payload, cb, data):
    b = (c_ubyte * len(payload)).from_buffer(payload)
    set_errno(0)
    ret = c_attr_parse_payload(b, len(payload), cb, data)
    if ret < 0: c_raise_if_errno()
    return ret

### returns 8-bit unsigned integer attribute payload
# uint8_t mnl_attr_get_u8(const struct nlattr *attr)
attr_get_u8		= c_attr_get_u8

### returns 16-bit unsigned integer attribute payload
# uint16_t mnl_attr_get_u16(const struct nlattr *attr)
attr_get_u16		= c_attr_get_u16

### returns 32-bit unsigned integer attribute payload
# uint32_t mnl_attr_get_u32(const struct nlattr *attr)
attr_get_u32		= c_attr_get_u32

### returns 64-bit unsigned integer attribute.
# uint64_t mnl_attr_get_u64(const struct nlattr *attr)
attr_get_u64		= c_attr_get_u64

### returns pointer to string attribute.
# const char *mnl_attr_get_str(const struct nlattr *attr)
attr_get_str		= c_attr_get_str

### add an attribute to netlink message
# void
# mnl_attr_put(struct nlmsghdr *nlh, uint16_t type, size_t len, const void *data)
def attr_put(nlh, attr_type, data):
    if hasattr(data, "sizeof"): size = data.sizeof() # netlink.UStructure
    else: size = len(data)
    
    c_attr_put(nlh, attr_type, size, (c_ubyte * size).from_buffer(data))

### add 8-bit unsigned integer attribute to netlink message
# void mnl_attr_put_u8(struct nlmsghdr *nlh, uint16_t type, uint8_t data)
attr_put_u8		= c_attr_put_u8

### add 16-bit unsigned integer attribute to netlink message
# void mnl_attr_put_u16(struct nlmsghdr *nlh, uint16_t type, uint16_t data)
attr_put_u16		= c_attr_put_u16

### add 32-bit unsigned integer attribute to netlink message
# void mnl_attr_put_u32(struct nlmsghdr *nlh, uint16_t type, uint32_t data)
attr_put_u32		= c_attr_put_u32

### add 64-bit unsigned integer attribute to netlink message
# void mnl_attr_put_u64(struct nlmsghdr *nlh, uint16_t type, uint64_t data)
attr_put_u64		= c_attr_put_u64

### add string attribute to netlink message
# void mnl_attr_put_str(struct nlmsghdr *nlh, uint16_t type, const char *data)
attr_put_str		= c_attr_put_str

### add string attribute to netlink message
# void mnl_attr_put_strz(struct nlmsghdr *nlh, uint16_t type, const char *data)
attr_put_strz		= c_attr_put_strz

### start an attribute nest
# struct nlattr *mnl_attr_nest_start(struct nlmsghdr *nlh, uint16_t type)
def attr_nest_start(nlh, attr_type):
    return c_attr_nest_start(nlh, attr_type).contents

### add an attribute to netlink message
# bool mnl_attr_put_check(struct nlmsghdr *nlh, size_t buflen,
#                         uint16_t type, size_t len, const void *data)
def attr_put_check(nlh, buflen, attr_type, data):
    cbuf = (c_ubyte * len(data)).from_buffer(data)
    return c_attr_put_check(nlh, buflen, attr_type, len(data), cbuf)

### add 8-bit unsigned int attribute to netlink message
# bool
# mnl_attr_put_u8_check(struct nlmsghdr *nlh, size_t buflen,
#                       uint16_t type, uint8_t data)
attr_put_u8_check	= c_attr_put_u8_check

### add 16-bit unsigned int attribute to netlink message
# bool
# mnl_attr_put_u16_check(struct nlmsghdr *nlh, size_t buflen,
#                        uint16_t type, uint16_t data)
attr_put_u16_check	= c_attr_put_u16_check

### add 32-bit unsigned int attribute to netlink message
# bool
# mnl_attr_put_u32_check(struct nlmsghdr *nlh, size_t buflen,
#                        uint16_t type, uint32_t data)
attr_put_u32_check	= c_attr_put_u32_check

### add 64-bit unsigned int attribute to netlink message
# bool
# mnl_attr_put_u64_check(struct nlmsghdr *nlh, size_t buflen,
#                        uint16_t type, uint64_t data)
attr_put_u64_check	= c_attr_put_u64_check

### add string attribute to netlink message
# bool
# mnl_attr_put_str_check(struct nlmsghdr *nlh, size_t buflen,
#                        uint16_t type, const char *data)
attr_put_str_check	= c_attr_put_str_check

### add string attribute to netlink message
# bool
# mnl_attr_put_strz_check(struct nlmsghdr *nlh, size_t buflen,
#                         uint16_t type, const char *data)
attr_put_strz_check	= c_attr_put_strz_check

### start an attribute nest
# struct nlattr *
# mnl_attr_nest_start_check(struct nlmsghdr *nlh, size_t buflen, uint16_t type)
def attr_nest_start_check(nlh, buflen, attr_type):
    return c_attr_nest_start_check(nlh, buflen, attr_type).contents

### start an attribute nest
# struct nlattr *
# mnl_attr_nest_start_check(struct nlmsghdr *nlh, size_t buflen, uint16_t type)
attr_nest_end		= c_attr_nest_end

### end an attribute nest
# void
# mnl_attr_nest_end(struct nlmsghdr *nlh, struct nlattr *start)
attr_nest_cancel	= c_attr_nest_cancel
