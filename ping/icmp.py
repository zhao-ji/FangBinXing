#! /usr/bin/env python
# -*- coding: utf8 -*-

import os
import socket
import struct
import sys

import logbook
from scapy.all import *

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
    logbook.info(
        "the checksum is {}".format(repr(header_checksum)))

    header = struct.pack(
        "bbHHh",
        ICMP_ECHO_REQUEST, ICMP_ECHO_CODE,
        header_checksum, identifier, ICMP_ECHO_SEQ)

    return header + content

def pack_reply(content):
    init_checksum = 0
    identifier = 0
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

def pack_reply_with_scapy(dst_ip, identifier, content):
    return str(IP(dst=dst_ip)/ICMP(id=identifier)/content)

def unpack(data):
    return data[28:]

def unpack_reply(data):
    return data.strip()[24:26], data.strip()[28:]
