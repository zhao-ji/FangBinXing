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

    return ~s & 0xffff

def pack(content):
    init_checksum = 0
    identifier = get_identifier()
    header = struct.pack(
        "bbHHH",
        ICMP_ECHO_REQUEST, ICMP_ECHO_CODE,
        init_checksum, identifier, 0)

    header_checksum = checksum(header + content)

    header = struct.pack(
        "bbHHH",
        ICMP_ECHO_REQUEST, ICMP_ECHO_CODE,
        header_checksum, identifier, 0)

    return header + content

def pack_reply(identifier, sequence, content):
    init_checksum = 0
    header = struct.pack(
        ">bbHHH",
        ICMP_ECHO_REPLY, ICMP_ECHO_CODE,
        init_checksum, identifier, sequence)

    header_checksum = checksum(header + content)

    header = struct.pack(
        ">bbHHH",
        ICMP_ECHO_REPLY, ICMP_ECHO_CODE,
        header_checksum, identifier, sequence)

    return header + content

def unpack(data):
    return data[28:]

def unpack_reply(data):
    identifier, sequence = struct.unpack(">HH", data.strip()[24:28])
    content = data.strip()[28:]
    return identifier, sequence, content
