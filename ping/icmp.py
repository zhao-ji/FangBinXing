#! /usr/bin/env python
# -*- coding: utf8 -*-

import os
import socket
import struct
import sys

import logbook

ICMP_ECHO_REPLY = 0
ICMP_ECHO_REQUEST = 8
ICMP_ECHO_CODE = 0
ICMP_ECHO_SEQ = 0


def get_identifier():
    return os.getpid() & 0xFFFF

def carry_around_add(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16)

def checksum(msg):
    # filed with zero if the length of msg is odd
    if len(msg)%2 is 1:
        msg += b'\x00'
    # process the internet checksum
    s = 0
    for i in range(0, len(msg), 2):
        w = ord(msg[i]) + (ord(msg[i+1]) << 8)
        s = carry_around_add(s, w)
    # make the result in big endian
    answer = ~s & 0xffff
    return answer >> 8 | (answer << 8 & 0xff00)

def pack(content):
    init_checksum = 0
    identifier = get_identifier()
    header = struct.pack(
        "bbHHh",
        ICMP_ECHO_REQUEST, ICMP_ECHO_CODE,
        init_checksum, identifier, ICMP_ECHO_SEQ)

    header_checksum = socket.htons(checksum(header + content))
    logbook.info(repr(header_checksum))

    header = struct.pack(
        "bbHHh",
        ICMP_ECHO_REQUEST, ICMP_ECHO_CODE,
        header_checksum, identifier, ICMP_ECHO_SEQ)

    return header + content

def pack_reply(identifier, content):
    init_checksum = 0
    header = struct.pack(
        "bbHHh",
        ICMP_ECHO_REPLY, ICMP_ECHO_CODE,
        init_checksum, identifier, ICMP_ECHO_SEQ)

    header_checksum = socket.htons(checksum(header + content))
    logbook.info(repr(header_checksum))

    header = struct.pack(
        "bbHHh",
        ICMP_ECHO_REPLY, ICMP_ECHO_CODE,
        header_checksum, identifier, ICMP_ECHO_SEQ)

    return header + content

def unpack(data):
    return data[8:]

def unpack_reply(data):
    return data[4:6], data[8:]
