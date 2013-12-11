#! /usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function

import sys, random, unittest, struct, errno
import ctypes

from cpylmnl import netlink
import cpylmnl as mnl

from .netlink.buf import *


class TestSuite(unittest.TestCase):
    def setUp(self):
        buflen = 512

        self.msg_attr_hlen = mnl.MNL_NLMSG_HDRLEN + mnl.MNL_ATTR_HDRLEN

        # nlmsghdr
        self.hbuf = NlmsghdrBuf(buflen)
        self.nlh = mnl.Header(self.hbuf)

        # nlattr
        self.abuf = NlattrBuf(buflen)
        self.nla = mnl.Attribute(self.abuf)
        self.rand_abuf = NlattrBuf(bytearray([random.randrange(0, 255) for j in range(buflen)]))
        self.rand_abuf.len = buflen
        self.rand_nla = mnl.Attribute(self.rand_abuf)

        # for nla validation
        self.valid_len = {
            # {data_type: (nla.len, exp_len)
            mnl.MNL_TYPE_UNSPEC		: (0, 0),
            mnl.MNL_TYPE_U8		: (1, 1),
            mnl.MNL_TYPE_U16		: (2, 2),
            mnl.MNL_TYPE_U32		: (4, 4),
            mnl.MNL_TYPE_U64		: (8, 8),
            mnl.MNL_TYPE_STRING		: (64, 64),
            mnl.MNL_TYPE_FLAG		: (0, 0),
            mnl.MNL_TYPE_MSECS		: (8, 8),
            mnl.MNL_TYPE_NESTED		: (32, 32),
            mnl.MNL_TYPE_NESTED_COMPAT	: (32, 32),
            mnl.MNL_TYPE_NUL_STRING	: (64, 64),
            mnl.MNL_TYPE_BINARY		: (64, 64),
            # mnl.TYPE_MAX		: (, ),
        }
        self.invalid_len = {
            mnl.MNL_TYPE_U8		: (2, 3),
            mnl.MNL_TYPE_U16		: (3, 4),
            mnl.MNL_TYPE_U32		: (5, 6),
            mnl.MNL_TYPE_U64		: (9, 10),
        }


    def test_Attribute(self):
        self.assertTrue(self.nla.len == 0)
        self.assertTrue(self.nla.type == 0)

        self.abuf.len = 10
        self.abuf.type = 2

        self.assertTrue(self.nla.len == 10)
        self.assertTrue(self.nla.type == 2)


    def test_get_type(self):
        self.abuf.type = 2
        self.assertTrue(self.nla.get_type() == 2)
        self.abuf.type = 2 | netlink.NLA_F_NESTED
        self.assertTrue(self.nla.get_type() == 2)


    def test_get_len(self):
        self.abuf.len = 10
        self.assertTrue(self.nla.get_len() == 10)


    def test_get_payload_len(self):
        self.abuf.len = 123
        self.assertTrue(self.nla.get_payload_len() == 123 - mnl.MNL_ATTR_HDRLEN)


    def test_get_payload_v(self):
        self.abuf.len = 234
        self.assertTrue(bytearray(self.nla.get_payload_v()) == self.abuf[mnl.MNL_ATTR_HDRLEN:234])


    def test_ok(self):
        self.abuf.len = 3
        self.assertTrue(self.nla.ok(3) == False)
        self.assertTrue(self.nla.ok(4) == False)
        self.assertTrue(self.nla.ok(5) == False)

        self.abuf.len = 4
        self.assertTrue(self.nla.ok(3) == False)
        self.assertTrue(self.nla.ok(4) == True)
        self.assertTrue(self.nla.ok(5) == True)

        self.abuf.len = 8
        self.assertTrue(self.nla.ok(6) == False)
        self.assertTrue(self.nla.ok(7) == False)
        self.assertTrue(self.nla.ok(8) == True)


    def test_next_attr(self):
        # 256 bytes + 128 bytes
        self.abuf.len = 256
        self.abuf[256:258] = struct.pack("H", 128) # XXX: set next len

        next_nla = self.nla.next_attribute()
        self.assertTrue(next_nla.len == 128)
        self.assertTrue(next_nla.type == struct.unpack("H", bytes(self.abuf[258:260]))[0])


    def test_type_valid(self):
        self.abuf.len = 251
        for i in range(mnl.MNL_TYPE_MAX):
            self.nla.type = i
            self.assertTrue(self.nla.type_valid(i + 1) == 1)

        self.abuf.type = mnl.MNL_TYPE_MAX + 1
        self.assertRaises(OSError, self.nla.type_valid, mnl.MNL_TYPE_MAX)
        self.assertTrue(ctypes.get_errno() == errno.EOPNOTSUPP)


    def test_validate(self):
        self.assertRaises(OSError, self.nla.validate, mnl.MNL_TYPE_MAX)
        self.assertTrue(ctypes.get_errno() == errno.EINVAL)
        self.assertRaises(OSError, self.nla.validate2, mnl.MNL_TYPE_MAX, 1)
        self.assertTrue(ctypes.get_errno() == errno.EINVAL)

        for t in self.valid_len:
            self.abuf.len = mnl.MNL_ATTR_HDRLEN + self.valid_len[t][0]
            self.assertTrue(self.nla.validate(t) == 0)
            self.assertTrue(self.nla.validate2(t, self.valid_len[t][1]) == 0)

        for t in self.invalid_len:
            self.abuf.len = mnl.MNL_ATTR_HDRLEN + self.invalid_len[t][0]
            self.assertRaises(OSError, self.nla.validate, t)
            self.assertTrue(ctypes.get_errno() == errno.ERANGE)
            self.assertRaises(OSError, self.nla.validate2, t, self.invalid_len[t][1])
            self.assertTrue(ctypes.get_errno() == errno.ERANGE)

        self.abuf.len = mnl.MNL_ATTR_HDRLEN + 1
        self.assertRaises(OSError, self.nla.validate, mnl.MNL_TYPE_FLAG)
        self.assertTrue(ctypes.get_errno() == errno.ERANGE)

        self.abuf.len = 256
        self.abuf[self.abuf.len - 1] = 1
        self.assertRaises(OSError, self.nla.validate, mnl.MNL_TYPE_NUL_STRING)
        self.assertTrue(ctypes.get_errno() == errno.EINVAL)
        self.abuf[self.abuf.len - 1] = 0
        self.abuf.len = mnl.MNL_ATTR_HDRLEN
        self.assertRaises(OSError, self.nla.validate, mnl.MNL_TYPE_NUL_STRING)
        self.assertTrue(ctypes.get_errno() == errno.ERANGE)

        self.abuf.len = mnl.MNL_ATTR_HDRLEN
        self.assertRaises(OSError, self.nla.validate, mnl.MNL_TYPE_STRING)
        self.assertTrue(ctypes.get_errno() == errno.ERANGE)

        self.abuf.len = mnl.MNL_ATTR_HDRLEN
        self.assertTrue(self.nla.validate(mnl.MNL_TYPE_NESTED) == 0)

        self.abuf.len = mnl.MNL_ATTR_HDRLEN + 1
        self.assertRaises(OSError, self.nla.validate2, mnl.MNL_TYPE_NESTED, 0)
        self.assertTrue(ctypes.get_errno() == errno.ERANGE)


    def test_attr_parse(self):
        class _cb(object):
            def __init__(self):
                self.val = 0x10

            def __call__(self, attr, data):
                if data is not None:
                    # sorry, I do not know how to
                    # raise Exception("from your callback")
                    ctypes.set_errno(data)
                    return mnl.MNL_CB_ERROR

                preval = self.val
                self.val += 1
                if preval == attr.get_u8():
                    return mnl.MNL_CB_OK
                else: return mnl.MNL_CB_STOP

        cb = mnl.attribute_cb(_cb())

        # XXX: using functions defined here
        nlh = mnl.put_new_header(512)
        nlh.put_u8(mnl.MNL_TYPE_U8, 0x10)
        nlh.put_u8(mnl.MNL_TYPE_U8, 0x11)
        nlh.put_u8(mnl.MNL_TYPE_U8, 0x12)
        nlh.put_u8(mnl.MNL_TYPE_U8, 0x13)
        self.assertTrue(nlh.parse(0, cb, None) == mnl.MNL_CB_OK)

        # just testing closure
        nlh = mnl.put_new_header(512)
        nlh.put_u8(mnl.MNL_TYPE_U8, 0x14)
        nlh.put_u8(mnl.MNL_TYPE_U8, 0x15)
        nlh.put_u8(mnl.MNL_TYPE_U8, 0x16)
        nlh.put_u8(mnl.MNL_TYPE_U8, 0x17)
        self.assertTrue(nlh.parse(0, cb, None) == mnl.MNL_CB_OK)

        nlh = mnl.put_new_header(512)
        nlh.put_u8(mnl.MNL_TYPE_U8, 0x18)
        nlh.put_u8(mnl.MNL_TYPE_U8, 0x19)
        nlh.put_u8(mnl.MNL_TYPE_U8, 0x1a)
        nlh.put_u8(mnl.MNL_TYPE_U8, 0x10)
        self.assertTrue(nlh.parse(0, cb, None) == mnl.MNL_CB_STOP)

        nlh = mnl.put_new_header(512)
        nlh.put_u8(mnl.MNL_TYPE_U8, 0x00)
        self.assertRaises(OSError, nlh.parse, 0, cb, 1)


    def test_parse_nested(self):
        # XXX: using functions defined here
        nlh = mnl.put_new_header(512)
        nested = nlh.nest_start(1)
        nlh.put_u8(2, 10)
        nlh.put_u8(3, 10)
        nlh.put_u8(4, 10)
        nlh.nest_end(nested)

        atype = [2]
        @mnl.mnl_attr_cb_t
        def cb(attr, data):
            if not data: return mnl.MNL_CB_STOP
            if atype[0] != attr.type: return mnl.MNL_CB_ERROR
            atype[0] += 1
            return mnl.MNL_CB_OK

        self.assertTrue(nested.parse_nested(cb, True) == mnl.MNL_CB_OK)
        self.assertTrue(nested.parse_nested(cb, False) == mnl.MNL_CB_STOP)
        self.assertTrue(nested.parse_nested(cb, True) == mnl.MNL_CB_ERROR)


    def test_attr_parse_payload(self):
        # XXX: using functions defined here
        nlh = mnl.put_new_header(512)
        nlh.put_u8(2, 10)
        nlh.put_u8(3, 10)
        nlh.put_u8(4, 10)
        b = nlh.get_payload_v()

        atype = [2]
        @mnl.mnl_attr_cb_t
        def cb(attr, data):
            if not data: return mnl.MNL_CB_STOP
            if atype[0] != attr.type: return mnl.MNL_CB_ERROR
            atype[0] += 1
            return mnl.MNL_CB_OK

        self.assertTrue(mnl.attr_parse_payload(b, cb, True) == mnl.MNL_CB_OK)
        self.assertTrue(mnl.attr_parse_payload(b, cb, False) == mnl.MNL_CB_STOP)
        self.assertTrue(mnl.attr_parse_payload(b, cb, True) == mnl.MNL_CB_ERROR)


    def test_get_u8(self):
        self.abuf.len = 5
        self.abuf.type = mnl.MNL_TYPE_U8
        self.abuf[4] = 0x11
        self.assertTrue(self.nla.get_u8() == 0x11)


    def test_get_u16(self):
        self.abuf.len = 6
        self.abuf.type = mnl.MNL_TYPE_U16
        self.abuf[4:6] = struct.pack("H", 0x1234)
        self.assertTrue(self.nla.get_u16() == 0x1234)


    def test_get_u32(self):
        self.abuf.len = 8
        self.abuf.type = mnl.MNL_TYPE_U32
        self.abuf[4:8] = struct.pack("I", 0x12345678)
        self.assertTrue(self.nla.get_u32() == 0x12345678)


    def test_get_u64(self):
        self.abuf.len = 12
        self.abuf.type = mnl.MNL_TYPE_U64
        self.abuf[4:12] = struct.pack("Q", 0x123456789abcdef)
        self.assertTrue(self.nla.get_u64() == 0x123456789abcdef)


    def test_get_str(self):
        self.abuf.len = 11
        self.abuf.type = mnl.MNL_TYPE_STRING
        self.abuf[4:10] = struct.pack('6c', *'abcDEF')
        self.abuf[11] = 0
        self.assertTrue(self.nla.get_str() == b'abcDEF')


    def test_put(self):
        b = bytearray([1, 2, 3])
        self.nlh.put_header()
        self.nlh.put(1, b)
        self.assertTrue(self.hbuf.len == self.msg_attr_hlen + mnl.MNL_ALIGN(len(b)))

        _tbuf = NlattrBuf(self.hbuf[mnl.MNL_NLMSG_HDRLEN:])
        self.assertTrue(_tbuf.type == 1)
        self.assertTrue(_tbuf.len == mnl.MNL_ATTR_HDRLEN + len(b))
        self.assertTrue(_tbuf[mnl.MNL_ATTR_HDRLEN:mnl.MNL_ATTR_HDRLEN + len(b)] == b)


    def test_put_u8(self):
        self.nlh.put_header()
        self.nlh.put_u8(mnl.MNL_TYPE_U8, 7)
        self.assertTrue(self.hbuf.len == self.msg_attr_hlen + mnl.MNL_ALIGN(1))

        _tbuf = NlattrBuf(self.hbuf[mnl.MNL_NLMSG_HDRLEN:])
        self.assertTrue(_tbuf.type == mnl.MNL_TYPE_U8)
        self.assertTrue(_tbuf.len == mnl.MNL_ATTR_HDRLEN + 1)
        self.assertTrue(_tbuf[mnl.MNL_ATTR_HDRLEN] == 7)


    def test_put_u16(self):
        self.nlh.put_header()
        self.nlh.put_u16(mnl.MNL_TYPE_U16, 12345)
        self.assertTrue(self.hbuf.len == self.msg_attr_hlen + mnl.MNL_ALIGN(2))

        _tbuf = NlattrBuf(self.hbuf[mnl.MNL_NLMSG_HDRLEN:])
        self.assertTrue(_tbuf.type == mnl.MNL_TYPE_U16)
        self.assertTrue(_tbuf.len == mnl.MNL_ATTR_HDRLEN + 2)
        self.assertTrue(struct.unpack("H", bytes(_tbuf[mnl.MNL_ATTR_HDRLEN:mnl.MNL_ATTR_HDRLEN + 2]))[0] == 12345)


    def test_put_u32(self):
        self.nlh.put_header()
        self.nlh.put_u32(mnl.MNL_TYPE_U32, 0x12345678)
        self.assertTrue(self.hbuf.len == self.msg_attr_hlen + mnl.MNL_ALIGN(4))

        _tbuf = NlattrBuf(self.hbuf[mnl.MNL_NLMSG_HDRLEN:])
        self.assertTrue(_tbuf.type == mnl.MNL_TYPE_U32)
        self.assertTrue(_tbuf.len == mnl.MNL_ATTR_HDRLEN + 4)
        self.assertTrue(struct.unpack("I", bytes(_tbuf[mnl.MNL_ATTR_HDRLEN:mnl.MNL_ATTR_HDRLEN + 4]))[0] == 0x12345678)


    def test_put_u64(self):
        self.nlh.put_header()
        self.nlh.put_u64(mnl.MNL_TYPE_U64, 0x123456789abcdef0)
        self.assertTrue(self.hbuf.len == self.msg_attr_hlen + mnl.MNL_ALIGN(8))

        _tbuf = NlattrBuf(self.hbuf[mnl.MNL_NLMSG_HDRLEN:])
        self.assertTrue(_tbuf.type == mnl.MNL_TYPE_U64)
        self.assertTrue(_tbuf.len == mnl.MNL_ATTR_HDRLEN + 8)
        self.assertTrue(struct.unpack("Q", bytes(_tbuf[mnl.MNL_ATTR_HDRLEN:mnl.MNL_ATTR_HDRLEN + 8]))[0] == 0x123456789abcdef0)

    def test_put_str(self):
        s = "abcdEFGH"
        self.nlh.put_header()
        self.nlh.put_str(mnl.MNL_TYPE_STRING, s)
        self.assertTrue(self.hbuf.len == self.msg_attr_hlen + mnl.MNL_ALIGN(len(s)))

        # to check not null terminated
        self.nlh.put_str(mnl.MNL_TYPE_STRING, "a" * 333) # 256 <= size <= 512

        _tbuf = NlattrBuf(self.hbuf[mnl.MNL_NLMSG_HDRLEN:])
        self.assertTrue(_tbuf.type == mnl.MNL_TYPE_STRING)
        self.assertTrue(_tbuf.len == mnl.MNL_ATTR_HDRLEN + len(s))
        self.assertTrue("8c",_tbuf[self.msg_attr_hlen:self.msg_attr_hlen + len(s)] == s)
        self.assertTrue(_tbuf[mnl.MNL_ATTR_HDRLEN + len(s) + 1] != 0)


    def test_put_strz(self):
        s = "abcdEFGH"
        self.nlh.put_header()
        self.nlh.put_strz(mnl.MNL_TYPE_NUL_STRING, s)
        self.assertTrue(self.hbuf.len == self.msg_attr_hlen + mnl.MNL_ALIGN(len(s) + 1))

        # to check null terminated
        self.nlh.put_str(mnl.MNL_TYPE_STRING, "a" * 333) # 256 <= size <= 512

        _tbuf = NlattrBuf(self.hbuf[mnl.MNL_NLMSG_HDRLEN:])
        self.assertTrue(_tbuf.type == mnl.MNL_TYPE_NUL_STRING)
        self.assertTrue(_tbuf.len == mnl.MNL_ATTR_HDRLEN + len(s) + 1)
        self.assertTrue("8c",_tbuf[self.msg_attr_hlen:self.msg_attr_hlen + len(s)] == s)
        self.assertTrue(_tbuf[mnl.MNL_ATTR_HDRLEN + len(s) + 1] == 0)


    def test_nest_start(self):
        self.nlh.put_header()
        attr = self.nlh.nest_start(1)
        self.assertTrue(self.hbuf.len == mnl.MNL_NLMSG_HDRLEN + mnl.MNL_ATTR_HDRLEN)

        _tbuf = NlattrBuf(self.hbuf[mnl.MNL_NLMSG_HDRLEN:])
        self.assertTrue(_tbuf.type & netlink.NLA_F_NESTED == netlink.NLA_F_NESTED)
        self.assertTrue(_tbuf.type & 1 == 1)


    def test_put_check(self):
        b = bytearray([1, 2, 3])
        self.nlh.put_header()
        self.assertTrue(self.nlh.put_check(len(self.hbuf), 1, b))

        # same as test_put()
        self.assertTrue(self.hbuf.len == self.msg_attr_hlen + mnl.MNL_ALIGN(len(b)))

        _tbuf = NlattrBuf(self.hbuf[mnl.MNL_NLMSG_HDRLEN:])
        self.assertTrue(_tbuf.type == 1)
        self.assertTrue(_tbuf.len == mnl.MNL_ATTR_HDRLEN + len(b))
        self.assertTrue(_tbuf[mnl.MNL_ATTR_HDRLEN:mnl.MNL_ATTR_HDRLEN + len(b)] == b)

        # should be false
        _hbuf = NlmsghdrBuf(self.msg_attr_hlen)
        _nlh = mnl.Header(_hbuf)
        _nlh.put_header()
        pb = _hbuf[:]
        self.assertFalse(_nlh.put_check(self.msg_attr_hlen, 1, b))
        self.assertTrue(_hbuf == pb)


    def test_put_u8_check(self):
        self.nlh.put_header()
        self.assertTrue(self.nlh.put_u8_check(len(self.hbuf), mnl.MNL_TYPE_U8, 7))

        # same as test_put()
        self.assertTrue(self.hbuf.len == self.msg_attr_hlen + mnl.MNL_ALIGN(1))

        _tbuf = NlattrBuf(self.hbuf[mnl.MNL_NLMSG_HDRLEN:])
        self.assertTrue(_tbuf.type == mnl.MNL_TYPE_U8)
        self.assertTrue(_tbuf.len == mnl.MNL_ATTR_HDRLEN + 1)
        self.assertTrue(_tbuf[mnl.MNL_ATTR_HDRLEN] == 7)

        # should be false
        _hbuf = NlmsghdrBuf(self.msg_attr_hlen)
        _nlh = mnl.Header(_hbuf)
        _nlh.put_header()
        pb = _hbuf[:]
        self.assertFalse(_nlh.put_u8_check(self.msg_attr_hlen, mnl.MNL_TYPE_U8, 7))
        self.assertTrue(_hbuf == pb)


    def test_put_u16_check(self):
        self.nlh.put_header()
        self.assertTrue(self.nlh.put_u16_check(len(self.hbuf), mnl.MNL_TYPE_U16, 12345))

        # same as test_put()
        self.assertTrue(self.hbuf.len == self.msg_attr_hlen + mnl.MNL_ALIGN(2))

        _tbuf = NlattrBuf(self.hbuf[mnl.MNL_NLMSG_HDRLEN:])
        self.assertTrue(_tbuf.type == mnl.MNL_TYPE_U16)
        self.assertTrue(_tbuf.len == mnl.MNL_ATTR_HDRLEN + 2)
        self.assertTrue(struct.unpack("H", bytes(_tbuf[mnl.MNL_ATTR_HDRLEN:mnl.MNL_ATTR_HDRLEN + 2]))[0] == 12345)

        # should be false
        _hbuf = NlmsghdrBuf(self.msg_attr_hlen)
        _nlh = mnl.Header(_hbuf)
        _nlh.put_header()
        pb = _hbuf[:]
        self.assertFalse(_nlh.put_u16_check(self.msg_attr_hlen, mnl.MNL_TYPE_U16, 12345))
        self.assertTrue(_hbuf == pb)


    def test_put_u32_check(self):
        self.nlh.put_header()
        self.assertTrue(self.nlh.put_u32_check(len(self.hbuf), mnl.MNL_TYPE_U32, 0x12345678))

        # same as test_put()
        self.assertTrue(self.hbuf.len == self.msg_attr_hlen + mnl.MNL_ALIGN(4))

        _tbuf = NlattrBuf(self.hbuf[mnl.MNL_NLMSG_HDRLEN:])
        self.assertTrue(_tbuf.type == mnl.MNL_TYPE_U32)
        self.assertTrue(_tbuf.len == mnl.MNL_ATTR_HDRLEN + 4)
        self.assertTrue(struct.unpack("I", bytes(_tbuf[mnl.MNL_ATTR_HDRLEN:mnl.MNL_ATTR_HDRLEN + 4]))[0] == 0x12345678)

        # should be false
        _hbuf = NlmsghdrBuf(self.msg_attr_hlen)
        _nlh = mnl.Header(_hbuf)
        _nlh.put_header()
        pb = _hbuf[:]
        self.assertFalse(_nlh.put_u32_check(self.msg_attr_hlen, mnl.MNL_TYPE_U32, 0x12345678))
        self.assertTrue(_hbuf == pb)


    def test_put_u64_check(self):
        self.nlh.put_header()
        self.assertTrue(self.nlh.put_u64_check(len(self.hbuf), mnl.MNL_TYPE_U64, 0x123456789abcdef0))

        # same as test_put()
        self.assertTrue(self.hbuf.len == self.msg_attr_hlen + mnl.MNL_ALIGN(8))

        _tbuf = NlattrBuf(self.hbuf[mnl.MNL_NLMSG_HDRLEN:])
        self.assertTrue(_tbuf.type == mnl.MNL_TYPE_U64)
        self.assertTrue(_tbuf.len == mnl.MNL_ATTR_HDRLEN + 8)
        self.assertTrue(struct.unpack("Q", bytes(_tbuf[mnl.MNL_ATTR_HDRLEN:mnl.MNL_ATTR_HDRLEN + 8]))[0] == 0x123456789abcdef0)

        # should be false
        _hbuf = NlmsghdrBuf(self.msg_attr_hlen)
        _nlh = mnl.Header(_hbuf)
        _nlh.put_header()
        pb = _hbuf[:]
        self.assertFalse(_nlh.put_u64_check(self.msg_attr_hlen, mnl.MNL_TYPE_U64, 0x123456789abcdef0))
        self.assertTrue(_hbuf == pb)


    def test_put_str_check(self):
        s = "abcdEFGH"
        self.nlh.put_header()
        self.assertTrue(self.nlh.put_str_check(len(self.hbuf), mnl.MNL_TYPE_STRING, s))

        # same as test_put()
        self.assertTrue(self.hbuf.len == self.msg_attr_hlen + mnl.MNL_ALIGN(len(s)))

        # to check not null terminated
        self.nlh.put_str(mnl.MNL_TYPE_STRING, "a" * 333) # 256 <= size <= 512

        _tbuf = NlattrBuf(self.hbuf[mnl.MNL_NLMSG_HDRLEN:])
        self.assertTrue(_tbuf.type == mnl.MNL_TYPE_STRING)
        self.assertTrue(_tbuf.len == mnl.MNL_ATTR_HDRLEN + len(s))
        self.assertTrue("8c",_tbuf[self.msg_attr_hlen:self.msg_attr_hlen + len(s)] == s)
        self.assertTrue(_tbuf[mnl.MNL_ATTR_HDRLEN + len(s) + 1] != 0)

        # should be false
        _hbuf = NlmsghdrBuf(self.msg_attr_hlen)
        _nlh = mnl.Header(_hbuf)
        _nlh.put_header()
        pb = _hbuf[:]
        self.assertFalse(_nlh.put_str_check(self.msg_attr_hlen, mnl.MNL_TYPE_STRING, s))
        self.assertTrue(_hbuf == pb)


    def test_put_strz_check(self):
        s = "abcdEFGH"
        self.nlh.put_header()
        self.assertTrue(self.nlh.put_strz_check(len(self.hbuf), mnl.MNL_TYPE_NUL_STRING, s))

        # same as test_put()
        self.assertTrue(self.hbuf.len == self.msg_attr_hlen + mnl.MNL_ALIGN(len(s) + 1))

        # to check null terminated
        self.nlh.put_str(mnl.MNL_TYPE_STRING, "a" * 333) # 256 <= size <= 512

        _tbuf = NlattrBuf(self.hbuf[mnl.MNL_NLMSG_HDRLEN:])
        self.assertTrue(_tbuf.type == mnl.MNL_TYPE_NUL_STRING)
        self.assertTrue(_tbuf.len == mnl.MNL_ATTR_HDRLEN + len(s) + 1)
        self.assertTrue("8c",_tbuf[self.msg_attr_hlen:self.msg_attr_hlen + len(s)] == s)
        self.assertTrue(_tbuf[mnl.MNL_ATTR_HDRLEN + len(s) + 1] == 0)

        # should be false
        _hbuf = NlmsghdrBuf(self.msg_attr_hlen)
        _nlh = mnl.Header(_hbuf)
        _nlh.put_header()
        pb = _hbuf[:]
        self.assertFalse(_nlh.put_strz_check(self.msg_attr_hlen, mnl.MNL_TYPE_NUL_STRING, s))
        self.assertTrue(_hbuf == pb)


    def test_nest_end(self):
        self.nlh.put_header()
        _nla = self.nlh.nest_start(1)				# payload len: aligned
        self.nlh.put_u8(mnl.MNL_TYPE_U8, 0x12)			# 1: 4
        self.nlh.put_u16(mnl.MNL_TYPE_U16, 0x3456)		# 2: 4
        self.nlh.put_u32(mnl.MNL_TYPE_U32, 0x3456789a)		# 4: 4
        self.nlh.put_u64(mnl.MNL_TYPE_U64, 0xbcdef0123456789a)	# 8: 8
        self.nlh.put_str(mnl.MNL_TYPE_STRING, "bcdef")		# 5: 8
        self.nlh.put_strz(mnl.MNL_TYPE_NUL_STRING, "01234567")	# 9: 12 = 40 + MNL_ATTR_HDRLEN * 7
        self.nlh.nest_end(_nla)
        _abuf = NlattrBuf(self.hbuf[mnl.MNL_NLMSG_HDRLEN:])
        self.assertTrue(_abuf.len == 68)


    def test_nest_cancel(self):
        self.nlh.put_header()
        _nla = self.nlh.nest_start(1)
        self.nlh.put_u8(mnl.MNL_TYPE_U8, 0x12)
        self.nlh.put_u16(mnl.MNL_TYPE_U16, 0x3456)
        self.nlh.put_u32(mnl.MNL_TYPE_U32, 0x3456789a)
        self.nlh.put_u64(mnl.MNL_TYPE_U64, 0xbcdef0123456789a)
        self.nlh.put_str(mnl.MNL_TYPE_STRING, "bcdef")
        self.nlh.put_strz(mnl.MNL_TYPE_NUL_STRING, "01234567")
        self.assertTrue(self.hbuf.len == mnl.MNL_NLMSG_HDRLEN + 68)
        self.nlh.nest_cancel(_nla)
        self.assertTrue(self.hbuf.len == mnl.MNL_NLMSG_HDRLEN)


if __name__ == '__main__':
    unittest.main()
